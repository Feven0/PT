"""Chain implementation for LLM operations."""
from typing import Dict, Any, Optional, List, AsyncIterator, Union, Callable, Awaitable
from datetime import datetime
import logging
import asyncio
import uuid

from core.llm.base import LLMBase, LLMError
from core.types.llm import (
    Message, 
    ModelResponse, 
    ChainStep, 
    ChainStepStatus,
    ChainState, 
    ChainStatus,
)
from core.types.audio import AudioFormat
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.prompt.templates.chain_prompts import CHAIN_PROMPTS, CHAIN_TEMPLATES
from ..response_formatter import ChainResponseFormatter, ChainResponse
from ..errors import ChainError, handle_chain_error
from .chain_state import ChainStateManager

logger = logging.getLogger(__name__)



class Chain:
    """Chain of LLM operations."""
    
    def __init__(
        self,
        llm_client: LLMBase,
        name: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """Initialize chain."""
        self.chain_id = str(uuid.uuid4())
        self.name = name
        self.llm_client = llm_client
        self.state_manager = ChainStateManager()
        self.response_formatter = ChainResponseFormatter()
        self.steps: List[Dict[str, Any]] = []
        self.messages: List[Message] = []
        self.metadata = metadata or {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._current_step: Optional[ChainStep] = None
        self._step_results: List[Dict[str, Any]] = []

        # Initialize chain state
        self.state_manager.create_chain(
            chain_id=self.chain_id,
            name=self.name,
            metadata=self.metadata
        )        
        
    def add_step(
        self,
        name: str,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None,
        retry_strategy: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a step to the chain."""
        step = {
            "name": name,
            "prompt": prompt,
            "metadata": metadata or {},
            "retry_strategy": retry_strategy or {
                "max_retries": self.max_retries,
                "delay": self.retry_delay
            }
        }
        self.steps.append(step)
        
        # Update chain state
        self.state_manager.add_step(
            chain_id=self.chain_id,
            step=ChainStep(
                name=name,
                description=f"Added step: {name}",
                status=ChainStepStatus.PENDING,
                metadata=step
            )
        )
        
    def add_message(self, message: Message) -> None:
        """Add a message to the chain."""
        self.messages.append(message)
        
        # Update chain state
        self.state_manager.update_chain(
            chain_id=self.chain_id,
            updates={
                "messages": [msg.to_dict() for msg in self.messages],
                "last_message": message.to_dict()
            }
        )
        
    async def _execute_step(
        self,
        step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a single step."""
        chain_step = None
        try:
            # Create chain step
            chain_step = ChainStep(
                name=step["name"],
                description=f"Executing step: {step['name']} with context",
                status=ChainStepStatus.RUNNING,
                started_at=datetime.now(),
                metadata={
                    **step["metadata"],
                    **(context or {}),
                    "retry_strategy": step["retry_strategy"]
                }
            )
            self._current_step = chain_step
            
            # Update chain state
            self.state_manager.update_step(
                chain_id=self.chain_id,
                step_name=step["name"],
                updates={
                    "status": ChainStepStatus.RUNNING,
                    "started_at": chain_step.started_at,
                    "metadata": chain_step.metadata
                }
            )
            
            # Format prompt using templates
            formatted_prompt = step["prompt"]
            if step["name"] in CHAIN_TEMPLATES:
                formatted_prompt = CHAIN_TEMPLATES[step["name"]].format(
                    step_name=step["name"],
                    prompt=step["prompt"],
                    context=context or {},
                    chain_state=self.state_manager.get_chain(self.chain_id).to_dict()
                )
            
            # Execute with retry and exponential backoff
            retry_count = 0
            max_retries = step["retry_strategy"]["max_retries"]
            delay = step["retry_strategy"]["delay"]
            
            while retry_count <= max_retries:
                try:
                    # Generate response
                    response = await self.llm_client.generate(
                        messages=self.messages + [Message(
                            role="system",
                            content=formatted_prompt
                        )],
                        metadata={
                            **step["metadata"],
                            "retry_count": retry_count
                        }
                    )
                    
                    # Format result
                    result = self.response_formatter.format_step_result(
                        step=chain_step,
                        response=response,
                        messages=self.messages
                    )
                    
                    # Validate result
                    if not result or not isinstance(result, dict):
                        raise ChainError(f"Invalid step result for {step['name']}")
                    
                    # Update step status
                    chain_step.status = ChainStepStatus.COMPLETED
                    chain_step.completed_at = datetime.now()
                    chain_step.result = result
                    
                    # Update chain state
                    self.state_manager.update_step(
                        chain_id=self.chain_id,
                        step_name=step["name"],
                        updates={
                            "status": ChainStepStatus.COMPLETED,
                            "completed_at": chain_step.completed_at,
                            "result": result
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count <= max_retries:
                        # Update state for retry
                        self.state_manager.update_step(
                            chain_id=self.chain_id,
                            step_name=step["name"],
                            updates={
                                "metadata": {
                                    **chain_step.metadata,
                                    "retry_count": retry_count,
                                    "last_error": str(e)
                                }
                            }
                        )
                        await asyncio.sleep(delay * (2 ** (retry_count - 1)))  # Exponential backoff
                        continue
                    raise e
                    
        except Exception as e:
            error = handle_chain_error(e, {
                "chain_id": self.chain_id,
                "step": step,
                "context": context
            })
            
            if chain_step:
                # Update step status
                chain_step.status = ChainStepStatus.ERROR
                chain_step.error = error.to_dict()
                chain_step.completed_at = datetime.now()
                
                # Update chain state
                self.state_manager.update_step(
                    chain_id=self.chain_id,
                    step_name=step["name"],
                    updates={
                        "status": ChainStepStatus.ERROR,
                        "error": error.to_dict(),
                        "completed_at": chain_step.completed_at
                    }
                )
            
            raise error
            
    async def execute(self) -> ChainResponse:
        """Execute the chain."""
        try:
            # Initialize chain execution
            self.state_manager.start_chain(self.chain_id)
            logger.info(f"Starting chain execution: {self.chain_id}")
            
            # Execute steps
            results = []
            for step in self.steps:
                try:
                    # Update current step in chain state
                    self.state_manager.update_chain(
                        chain_id=self.chain_id,
                        updates={"current_step": step["name"]}
                    )
                    
                    # Execute step
                    result = await self._execute_step(
                        step,
                        context={"previous_results": results}
                    )
                    results.append(result)
                    self._step_results.append(result)
                    
                except Exception as e:
                    # Handle step failure
                    error = handle_chain_error(e, {
                        "chain_id": self.chain_id,
                        "step": step,
                        "results": results
                    })
                    logger.error(f"Step execution failed: {error.message}")
                    raise error
            
            # Create final response
            response = self.response_formatter.create_response(
                state=self.state_manager.get_chain(self.chain_id),
                step_results=self._step_results,
                metadata={
                    "total_steps": len(self.steps),
                    "completed_steps": len(results),
                    "execution_time": (datetime.now() - self.state_manager.get_chain(self.chain_id).started_at).total_seconds()
                }
            )
            
            # Complete chain
            self.state_manager.complete_chain(
                chain_id=self.chain_id,
                result=response.to_dict()
            )
            logger.info(f"Chain execution completed: {self.chain_id}")
            
            return response
            
        except Exception as e:
            error = handle_chain_error(e, {
                "chain_id": self.chain_id,
                "name": self.name,
                "step_results": self._step_results
            })
            logger.error(f"Chain execution failed: {error.message}")
            
            # Fail chain
            self.state_manager.fail_chain(
                chain_id=self.chain_id,
                error=error.to_dict()
            )
            
            raise error
            
    async def stream(self) -> AsyncIterator[Union[ModelResponse, Dict[str, Any]]]:
        """Stream chain execution."""
        try:
            # Initialize chain execution
            self.state_manager.start_chain(self.chain_id)
            logger.info(f"Starting chain streaming: {self.chain_id}")
            
            # Stream initialization
            yield {
                "type": "chain_start",
                "chain_id": self.chain_id,
                "total_steps": len(self.steps)
            }
            
            # Stream steps
            for i, step in enumerate(self.steps):
                try:
                    # Update current step
                    self.state_manager.update_chain(
                        chain_id=self.chain_id,
                        updates={
                            "current_step": step["name"],
                            "progress": (i + 1) / len(self.steps)
                        }
                    )
                    
                    # Stream step start
                    yield {
                        "type": "step_start",
                        "step": step["name"],
                        "step_number": i + 1
                    }
                    
                    # Stream step execution
                    async for response in self.llm_client.stream(
                        messages=self.messages + [Message(
                            role="system",
                            content=step["prompt"]
                        )],
                        metadata=step["metadata"]
                    ):
                        yield response
                        
                    # Stream step completion
                    yield {
                        "type": "step_complete",
                        "step": step["name"],
                        "step_number": i + 1
                    }
                    
                except Exception as e:
                    error = handle_chain_error(e, {
                        "chain_id": self.chain_id,
                        "step": step
                    })
                    yield {
                        "type": "error",
                        "error": error.to_dict()
                    }
                    raise error
                    
            # Complete chain
            self.state_manager.complete_chain(self.chain_id)
            yield {
                "type": "chain_complete",
                "chain_id": self.chain_id
            }
            logger.info(f"Chain streaming completed: {self.chain_id}")
            
        except Exception as e:
            error = handle_chain_error(e, {
                "chain_id": self.chain_id,
                "name": self.name
            })
            logger.error(f"Chain streaming failed: {error.message}")
            
            # Fail chain
            self.state_manager.fail_chain(
                chain_id=self.chain_id,
                error=error.to_dict()
            )
            
            yield {
                "type": "chain_error",
                "error": error.to_dict()
            }
            raise error

    def get_execution_graph(self) -> Dict[str, Any]:
        """Get chain execution graph."""
        nodes = []
        edges = []
        
        # Add nodes for each step
        for step in self.steps:
            nodes.append({
                "id": step["name"],
                "type": "step",
                "status": self.state_manager.get_chain(self.chain_id).steps[
                    next(i for i, s in enumerate(self.state_manager.get_chain(self.chain_id).steps) 
                    if s.name == step["name"])
                ].status.value
            })
            
        # Add edges between consecutive steps
        for i in range(len(self.steps) - 1):
            edges.append({
                "source": self.steps[i]["name"],
                "target": self.steps[i + 1]["name"],
                "type": "sequence"
            })
            
        return {
            "nodes": nodes,
            "edges": edges
        }
        
    def get_dependencies(self) -> Dict[str, List[str]]:
        """Get step dependencies."""
        dependencies = {}
        
        # Each step depends on all previous steps in sequence
        for i, step in enumerate(self.steps):
            dependencies[step["name"]] = [
                prev_step["name"] for prev_step in self.steps[:i]
            ]
            
        return dependencies 

class AudioChain(Chain):
    """Chain for audio processing operations."""

    def __init__(
        self,
        client: LLMBase,
        config: Optional[Dict[str, Any]] = None,
        state_manager: Optional[ChainStateManager] = None,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None
    ):
        super().__init__(
            name="audio_chain",
            client=client,
            config=config,
            state_manager=state_manager,
            metrics=metrics,
            logger=logger
        )
        self._audio_buffer: Dict[str, bytes] = {}
        self._transcription_cache: Dict[str, str] = {}

    async def transcribe_and_process(
        self,
        audio_data: bytes,
        format: AudioFormat,
        sample_rate: int,
        channels: int,
        process_func: Callable[[str], Awaitable[str]],
        **kwargs: Any
    ) -> ChainResponse:
        """Transcribe audio and process the text."""
        steps = [
            ChainStep(
                name="transcribe",
                description="Transcribe audio to text",
                func=self._transcribe_step,
                args={
                    "audio_data": audio_data,
                    "format": format,
                    "sample_rate": sample_rate,
                    "channels": channels,
                    **kwargs
                }
            ),
            ChainStep(
                name="process",
                description="Process transcribed text",
                func=self._process_step,
                args={
                    "process_func": process_func
                }
            )
        ]
        return await self.execute(steps)

    async def process_and_synthesize(
        self,
        text: str,
        process_func: Callable[[str], Awaitable[str]],
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> ChainResponse:
        """Process text and synthesize to audio."""
        steps = [
            ChainStep(
                name="process",
                description="Process input text",
                func=self._process_step,
                args={
                    "text": text,
                    "process_func": process_func
                }
            ),
            ChainStep(
                name="synthesize",
                description="Synthesize text to audio",
                func=self._synthesize_step,
                args={
                    "voice": voice,
                    "format": format,
                    "sample_rate": sample_rate,
                    **kwargs
                }
            )
        ]
        return await self.execute(steps)

    async def _transcribe_step(
        self,
        audio_data: bytes,
        format: AudioFormat,
        sample_rate: int,
        channels: int,
        **kwargs: Any
    ) -> str:
        """Transcribe audio to text."""
        try:
            response = await self.client.transcribe(
                audio_data,
                format=format,
                sample_rate=sample_rate,
                channels=channels,
                **kwargs
            )
            text = response.content
            self._transcription_cache[self.state.chain_id] = text
            return text
        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            raise ChainError("Transcription failed", details={"error": str(e)})

    async def _process_step(
        self,
        text: Optional[str] = None,
        process_func: Optional[Callable[[str], Awaitable[str]]] = None
    ) -> str:
        """Process text using provided function."""
        try:
            if text is None:
                text = self._transcription_cache.get(self.state.chain_id)
                if text is None:
                    raise ChainError("No text available for processing")

            if process_func is None:
                raise ChainError("No processing function provided")

            processed_text = await process_func(text)
            return processed_text
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            raise ChainError("Text processing failed", details={"error": str(e)})

    async def _synthesize_step(
        self,
        text: Optional[str] = None,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> bytes:
        """Synthesize text to audio."""
        try:
            if text is None:
                text = self._transcription_cache.get(self.state.chain_id)
                if text is None:
                    raise ChainError("No text available for synthesis")

            response = await self.client.synthesize(
                text,
                voice=voice,
                format=format,
                sample_rate=sample_rate,
                **kwargs
            )
            audio_data = response.content
            self._audio_buffer[self.state.chain_id] = audio_data
            return audio_data
        except Exception as e:
            self.logger.error(f"Audio synthesis failed: {str(e)}")
            raise ChainError("Audio synthesis failed", details={"error": str(e)})

    async def cleanup(self) -> None:
        """Clean up resources."""
        self._audio_buffer.clear()
        self._transcription_cache.clear()
        await super().cleanup() 