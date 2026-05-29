"""LLM client implementations."""
from typing import Dict, Any, Optional, List, AsyncIterator, Type, Union, TypeVar, Generic, Set
import asyncio
from datetime import datetime, timedelta
import time
from collections import deque
import json

from litellm import acompletion, Router
import instructor
from pydantic import BaseModel

from core.base.manager import BaseManager
from core.logging import BackendLogger
from .base import LLMBase, LLMProvider, LLMError
from core.types.llm import Message, ModelResponse, FunctionCall
from core.types.audio import AudioChunk, AudioFormat, TranscriptionOutput
from core.config.base import AppConfig

logger = BackendLogger(__name__).get_logger()

T = TypeVar('T', bound=BaseModel)

"""
    Asynchronously executes a litellm.completion() call for any of litellm supported llms (example gpt-4, gpt-3.5-turbo, claude-2, command-nightly)

    Parameters:
        model (str): The name of the language model to use for text completion. see all supported LLMs: https://docs.litellm.ai/docs/providers/
        messages (List): A list of message objects representing the conversation context (default is an empty list).

        OPTIONAL PARAMS
        functions (List, optional): A list of functions to apply to the conversation messages (default is an empty list).
        function_call (str, optional): The name of the function to call within the conversation (default is an empty string).
        temperature (float, optional): The temperature parameter for controlling the randomness of the output (default is 1.0).
        top_p (float, optional): The top-p parameter for nucleus sampling (default is 1.0).
        n (int, optional): The number of completions to generate (default is 1).
        stream (bool, optional): If True, return a streaming response (default is False).
        stream_options (dict, optional): A dictionary containing options for the streaming response. Only use this if stream is True.
        stop(string/list, optional): - Up to 4 sequences where the LLM API will stop generating further tokens.
        max_tokens (integer, optional): The maximum number of tokens in the generated completion (default is infinity).
        max_completion_tokens (integer, optional): An upper bound for the number of tokens that can be generated for a completion, including visible output tokens and reasoning tokens.
        modalities (List[ChatCompletionModality], optional): Output types that you would like the model to generate for this request. You can use `["text", "audio"]`
        prediction (ChatCompletionPredictionContentParam, optional): Configuration for a Predicted Output, which can greatly improve response times when large parts of the model response are known ahead of time. This is most common when you are regenerating a file with only minor changes to most of the content.
        audio (ChatCompletionAudioParam, optional): Parameters for audio output. Required when audio output is requested with modalities: ["audio"]
        presence_penalty (float, optional): It is used to penalize new tokens based on their existence in the text so far.
        frequency_penalty: It is used to penalize new tokens based on their frequency in the text so far.
        logit_bias (dict, optional): Used to modify the probability of specific tokens appearing in the completion.
        user (str, optional):  A unique identifier representing your end-user. This can help the LLM provider to monitor and detect abuse.
        metadata (dict, optional): Pass in additional metadata to tag your completion calls - eg. prompt version, details, etc.
        api_base (str, optional): Base URL for the API (default is None).
        api_version (str, optional): API version (default is None).
        api_key (str, optional): API key (default is None).
        model_list (list, optional): List of api base, version, keys
        timeout (float, optional): The maximum execution time in seconds for the completion request.

        LITELLM Specific Params
        mock_response (str, optional): If provided, return a mock completion response for testing or debugging purposes (default is None).
        custom_llm_provider (str, optional): Used for Non-OpenAI LLMs, Example usage for bedrock, set model="amazon.titan-tg1-large" and custom_llm_provider="bedrock"
    Returns:
        ModelResponse: A response object containing the generated completion and associated metadata.

    Notes:
        - This function is an asynchronous version of the `completion` function.
        - The `completion` function is called using `run_in_executor` to execute synchronously in the event loop.
        - If `stream` is True, the function returns an async generator that yields completion lines.
    """

class LLMClient(BaseManager):
    """Enhanced LLM client with instructor and instructor integration."""
    
    def __init__(self, 
                 name: str,
                 config: AppConfig,                  
                 metrics: Optional[Any] = None,
                 logger: Optional[BackendLogger] = None,
                 dependencies: Optional[Set[str]] = None):
        
        """Initialize LLM client with enhanced capabilities."""
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )

        self.metrics_service = None

        self.provider = self.config.default_provider
        self.provider_config = self.config.providers.get(self.provider)

        if not self.provider_config.api_key:
            raise ValueError('API key is required')

        # Initialize instructor client with litellm settings
        
        client_config = {
            "model": self.provider_config.model,
            "api_key": self.provider_config.api_key,
            "timeout": self.provider_config.timeout
        }
        
        # Configure model based on provider
        # https://docs.litellm.ai/docs/tutorials/instructor
        self.aclient = instructor.patch(
            Router(
                model_list=[
                    {
                        "model_name": self.provider_config.model,
                        "litellm_params": client_config,
                    }
                ],
                default_litellm_params={"acompletion": True},  # 👈 IMPORTANT - tells litellm to route to async completion function.
            )
        )

        
        self.Message = Message
        self.FunctionCall = FunctionCall
        self.ModelResponse = ModelResponse

        
        # Metrics tracking
        self._request_times = []
        self._total_requests = 0
        self._error_count = 0

    def _set_model(self, 
                   provider: Optional[str] = None, 
                   model: Optional[str] = None):
        """Set the model for the LLM client."""
        if provider:
            if provider not in self.config.providers:
                raise ValueError(f"Provider {provider} not found in config.providers")
            self.provider_config = self.config.providers[provider]

            if model:
                self.provider_config.model = model
        else:
            if model:
                if '/' in model:
                    provider, model = model.split('/')
                    self._set_model(provider=provider, model=model)
                else:   
                    self.provider_config.model = model

    def _parse_function_call(self, function_call: Optional[Dict[str, Any]]) -> Optional[FunctionCall]:
        """Parse function call from instructor response."""
        if not function_call:
            return None
            
        try:
            return self.FunctionCall(
                name=function_call.get("name", ""),
                arguments=function_call.get("arguments", {}),
                parameters=function_call.get("parameters", {}),
                call_id=function_call.get("id", "")
            )
        except Exception as e:
            logger.error(f"Error parsing function call: {e}")
            return None

    async def _record_request(
        self,
        duration: float,
        is_error: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a request for metrics calculation and store in database."""
        try:
            request_data = {
                'timestamp': datetime.now(),
                'duration': duration,
                'is_error': is_error,
                'provider': self.provider_config.name,
                'model': self.provider_config.model
            }
            if metadata:
                request_data['metadata'] = metadata
                
            # Store in memory for immediate access
            self._request_times.append(request_data)
            self._total_requests += 1
            if is_error:
                self._error_count += 1
                
            # Store in database if storage is configured
            if self.metrics_service:
                try:
                    # Convert to format expected by storage
                    metric_data = {
                        'timestamp': request_data['timestamp'],
                        'provider': request_data['provider'],
                        'model': request_data['model'],
                        'total_requests': 1,
                        'successful_requests': 0 if is_error else 1,
                        'failed_requests': 1 if is_error else 0,
                        'total_tokens': metadata.get('token_usage', {}).get('total_tokens', 0) if metadata else 0,
                        'average_latency': duration,
                        'error_rate': 1.0 if is_error else 0.0,
                        'token_usage': json.dumps(metadata.get('token_usage', {})) if metadata else '{}',
                        'metadata': json.dumps(metadata or {})
                    }
                    await self.metrics_service.record_metric(metric_data)
                except Exception as e:
                    logger.error(f"Failed to store metric in database: {e}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")

    def _convert_message(self, msg: Union[Message, Dict[str, Any]]) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        # If already a dict, extract only the required fields
        if isinstance(msg, dict):
            return {
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
                # **({"name": msg["name"]} if "name" in msg and msg["name"] else {"name": ""}),
                # # Only include non-empty metadata
                # **({"metadata": {k: v for k, v in msg.get("metadata", {}).items() if v is not None}} 
                #    if "metadata" in msg and msg.get("metadata") else {"metadata": {}})
            }
        
        # If Message instance, use its to_dict method but clean the output
        if isinstance(msg, Message):
            msg_dict = msg.to_dict()
            return {
                "role": msg_dict["role"],
                "content": msg_dict["content"],
                # **({"name": msg_dict["name"]} if "name" in msg_dict and msg_dict["name"] else {"name": ""}),
                # # Only include non-empty metadata
                # **({"metadata": {k: v for k, v in msg_dict.get("metadata", {}).items() if v is not None}} 
                #    if msg_dict.get("metadata") else {"metadata": {}})
            }
        
        # For any other object, try to extract required fields
        return {
            "role": getattr(msg, "role", "user"),
            "content": getattr(msg, "content", ""),
            # **({"name": getattr(msg, "name")} if hasattr(msg, "name") and getattr(msg, "name") else {"name": ""}),
            # # Only include non-empty metadata
            # **({"metadata": {k: v for k, v in getattr(msg, "metadata", {}).items() if v is not None}} 
            #    if hasattr(msg, "metadata") and getattr(msg, "metadata") else {"metadata": {}})
        }
            
    async def generate(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        functions: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> ModelResponse[T]:
        """Generate completion using instructor with structured output support."""

        self._set_model(provider=provider, model=model)

        start_time = time.time()
        try:
            # Convert messages to instructor format
            messages_dict = [self._convert_message(msg) for msg in messages]
            
            # Prepare generation parameters
            params = {
                "model": self.provider_config.model,
                "provider": self.provider_config.name,
                "messages": messages_dict,
                "temperature": temperature or self.provider_config.temperature,
                "max_tokens": max_tokens or self.provider_config.max_tokens
            }
            
            # Add function calling if provided
            if functions:
                params["tools"] = functions
                
            # Generate response
            if response_model:
                # Use instructor for structured output
                logger.info(f"Using instructor for structured output: {response_model}")
                response = await self.aclient.chat.completions.create(
                    response_model=response_model,
                    **params
                )
                try:
                    content = response.model_dump_json()
                    fcall = response['function_call']
                except Exception as e:
                    logger.error(f"Error parsing function call: {e}")
                    print('type of response',type(response))
                    print('response',response)
                    content = ""
                    fcall = None
            else:
                # Regular completion
                logger.info(f"Using regular completion")
                try:
                    params["stream"] = False
                    response = await self.aclient.chat.completions.create(**params)
                    content = response.choices[0].message.content
                    fcall = response.choices[0].message.function_call
                except Exception as e:
                    logger.error(f"Error in regular completion: {e}")
                    print('dir response',dir(response))   
                    print('type of response',type(response))            
                    content = ""
                    fcall = None
            

            fcall = self._parse_function_call(fcall) if fcall else None
            usage = response.usage.dict() if hasattr(response, "usage") else {}
        

            # Convert to our ModelResponse format
            model_response = ModelResponse(
                content=content,
                function_call=fcall,
                metadata={
                    "model": params["model"],
                    "provider": params["provider"],
                    "usage": usage,
                    **(metadata or {})
                },
                model=params["model"],
                provider=params["provider"],
                usage=usage
            )
            
            # Record metrics
            await self._record_request(
                duration=time.time() - start_time,
                metadata={
                    **(metadata or {}),
                    "model": params["model"],
                    "provider": params["provider"],
                    "message_count": len(messages),
                    "token_usage": model_response.usage
                }
            )
            
            return model_response
            
        except Exception as e:
            # Record error metrics
            await self._record_request(
                duration=time.time() - start_time,
                is_error=True,
                metadata={
                    **(metadata or {}),
                    "model": model or self.provider_config.model,
                    "provider": self.provider_config.name,
                    "message_count": len(messages),
                    "error": str(e)
                }
            )
            raise LLMError(f"Generation failed: {str(e)}")
                
    async def stream(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        functions: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        response_model: Optional[type[BaseModel]] = None
    ) -> AsyncIterator[ModelResponse]:
        """Stream completion using instructor with optional structured output support."""

        self._set_model(provider=provider, model=model)

        start_time = time.time()
        try:
            # Convert messages to instructor format
            messages_dict = [self._convert_message(msg) for msg in messages]
            
            # Prepare generation parameters
            params = {
                "model": self.provider_config.model,
                "provider": self.provider_config.name,
                "messages": messages_dict,
                "temperature": temperature or self.provider_config.temperature,
                "max_tokens": max_tokens or self.provider_config.max_tokens,
                "stream": True
            }
            
            # Add function calling if provided
            if functions:
                params["tools"] = functions
                
            # Stream response
            async for chunk in await self.aclient.chat.completions.create(**params):
                # Handle different response formats
                try:
                    # Extract delta content and function call based on response type
                    if isinstance(chunk, dict):
                        # Handle dictionary response
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        function_call_data = delta.get("function_call")
                    else:
                        # Handle object response
                        delta = chunk.choices[0].delta if hasattr(chunk, "choices") else chunk.delta
                        content = delta.content if hasattr(delta, "content") else None
                        function_call_data = getattr(delta, "function_call", None)

                    # Parse function call if present
                    function_call = None
                    if function_call_data:
                        function_call = self._parse_function_call(function_call_data)

                    # Create response metadata
                    response_metadata = {
                        "model": params["model"],
                        "provider": params["provider"],
                        "is_chunk": True,
                        "timestamp": datetime.now().isoformat(),
                        **(metadata or {})
                    }

                    if content or function_call:
                        yield ModelResponse(
                            content=content or "",
                            function_call=function_call,
                            metadata=response_metadata,
                            model=params["model"],
                            provider=params["provider"]
                        )

                except Exception as e:
                    logger.error(f"Error processing stream chunk: {e}", exc_info=True)
                    continue
            
            # Record metrics after streaming completes
            await self._record_request(
                duration=time.time() - start_time,
                metadata={
                    **(metadata or {}),
                    "model": params["model"],
                    "provider": params["provider"],
                    "message_count": len(messages),
                    "streaming": True
                }
            )
            
        except Exception as e:
            # Record error metrics
            await self._record_request(
                duration=time.time() - start_time,
                is_error=True,
                metadata={
                    **(metadata or {}),
                    "model": model or self.provider_config.model,
                    "provider": self.provider_config.name,
                    "message_count": len(messages),
                    "error": str(e),
                    "streaming": True
                }
            )
            raise LLMError(f"Streaming failed: {str(e)}")
            
    async def check_health(self) -> Dict[str, Any]:
        """Check the health of the LLM provider and return metrics."""
        try:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            
            # Calculate requests per minute
            recent_requests = [t for t in self._request_times if t['timestamp'] > one_minute_ago]
            requests_per_minute = len(recent_requests)
            
            # Calculate average latency
            if recent_requests:
                avg_latency = sum(r['duration'] for r in recent_requests) / len(recent_requests)
                avg_latency_ms = avg_latency * 1000  # Convert to milliseconds
            else:
                avg_latency_ms = 0
            
            # Calculate token usage statistics
            total_prompt_tokens = 0
            total_completion_tokens = 0
            total_messages = 0
            total_audio_tokens = 0
            total_reasoning_tokens = 0
            total_cached_tokens = 0
            
            for request in self._request_times:
                if 'metadata' in request and 'token_usage' in request['metadata']:
                    usage = request['metadata']['token_usage']
                    # Basic token counts
                    total_prompt_tokens += usage.get('prompt_tokens', 0)
                    total_completion_tokens += usage.get('completion_tokens', 0)
                    
                    # Detailed token breakdowns
                    prompt_details = usage.get('prompt_tokens_details', {})
                    completion_details = usage.get('completion_tokens_details', {})
                    
                    total_audio_tokens += (prompt_details.get('audio_tokens', 0) + 
                                         completion_details.get('audio_tokens', 0))
                    total_reasoning_tokens += completion_details.get('reasoning_tokens', 0)
                    total_cached_tokens += prompt_details.get('cached_tokens', 0)
                
                # Message count
                if 'metadata' in request and 'message_count' in request['metadata']:
                    total_messages += request['metadata']['message_count']
            
            # Calculate averages
            total_requests = len(self._request_times)
            avg_messages = total_messages / total_requests if total_requests > 0 else 0
            
            # Calculate error rate
            error_rate = (self._error_count / self._total_requests * 100) if self._total_requests > 0 else 0
            
            return {
                "status": "healthy",
                "provider": self.provider_config.name,
                "model": self.provider_config.model,
                "requests_per_minute": requests_per_minute,
                "average_latency_ms": round(avg_latency_ms, 2),
                "error_rate": round(error_rate, 2),
                "total_requests": self._total_requests,
                "error_count": self._error_count,
                "token_usage": {
                    "total_prompt_tokens": total_prompt_tokens,
                    "total_completion_tokens": total_completion_tokens,
                    "total_tokens": total_prompt_tokens + total_completion_tokens,
                    "average_prompt_tokens": round(total_prompt_tokens / total_requests if total_requests > 0 else 0, 2),
                    "average_completion_tokens": round(total_completion_tokens / total_requests if total_requests > 0 else 0, 2),
                    "token_details": {
                        "audio_tokens": total_audio_tokens,
                        "reasoning_tokens": total_reasoning_tokens,
                        "cached_tokens": total_cached_tokens
                    }
                },
                "message_stats": {
                    "total_messages": total_messages,
                    "average_messages_per_request": round(avg_messages, 2)
                }
            }
                        
        except Exception as e:
            logger.error(f"Error checking LLM health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_config.name,
                "model": self.provider_config.model
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get current LLM metrics.
        
        Returns:
            Dictionary containing current metrics:
            - total_requests: Total number of requests made
            - successful_requests: Number of successful requests
            - failed_requests: Number of failed requests
            - total_tokens: Total tokens used
            - average_latency: Average request latency
            - error_rate: Rate of failed requests
            - requests_per_minute: Average requests per minute
            - token_usage_per_model: Token usage broken down by model
            - provider_metrics: Metrics broken down by provider
            - model_metrics: Metrics broken down by model
        """
        metrics = {
            "total_requests": self._total_requests,
            "successful_requests": self._total_requests - self._error_count,
            "failed_requests": self._error_count,
            "total_tokens": sum(r['metadata'].get('token_usage', {}).get('total_tokens', 0) for r in self._request_times),
            "average_latency": sum(r['duration'] for r in self._request_times) / len(self._request_times) if len(self._request_times) > 0 else 0.0,
            "error_rate": self._error_count / self._total_requests if self._total_requests > 0 else 0.0,
            "requests_per_minute": len([t for t in self._request_times if t['timestamp'] > datetime.now() - timedelta(minutes=1)]) if len(self._request_times) > 0 else 0,
            "token_usage_per_model": {r['metadata'].get('model', 'unknown'): r['metadata'].get('token_usage', {}) for r in self._request_times},
            "provider_metrics": {self.provider_config.name: self.check_health()},
            "model_metrics": {r['metadata'].get('model', 'unknown'): r['metadata'].get('token_usage', {}) for r in self._request_times}
        }
        return metrics 

    async def transcribe(
        self,
        audio: bytes,
        format: AudioFormat,
        sample_rate: int,
        channels: int,
        **kwargs: Any
    ) -> ModelResponse[TranscriptionOutput]:
        """Transcribe audio data using litellm pattern."""
        try:
            # Prepare transcription parameters
            params = {
                "file": ("audio", audio, f"audio/{format.value}"),
                "model": kwargs.get("model", self.provider_config.model),
                "response_format": "verbose_json",
                **kwargs
            }
            
            # Use instructor for structured output
            response = await self.aclient.chat.completions.create(
                response_model=TranscriptionOutput,
                messages=[{"role": "system", "content": "Transcribe the audio"}],
                **params
            )
            
            return ModelResponse(
                content=response.text,
                metadata={
                    "confidence": response.confidence,
                    "start_time": response.start_time,
                    "end_time": response.end_time,
                    **(response.metadata if hasattr(response, "metadata") else {})
                }
            )
            
        except Exception as e:
            raise LLMError(f"Transcription failed: {str(e)}")

    async def transcribe_stream(
        self,
        stream: AsyncIterator[AudioChunk],
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[TranscriptionOutput]]:
        """Transcribe streaming audio data using litellm pattern."""
        try:
            buffer = bytearray()
            chunk_duration = 0
            
            async for chunk in stream:
                buffer.extend(chunk.data)
                chunk_duration += chunk.duration
                
                # Process in ~30 second chunks
                if chunk_duration >= 30:
                    # Use instructor for structured output
                    response = await self.aclient.chat.completions.create(
                        response_model=TranscriptionOutput,
                        messages=[{"role": "system", "content": "Process streaming audio"}],
                        stream=True,
                        file=("audio", bytes(buffer), f"audio/{chunk.format.value}"),
                        **kwargs
                    )
                    
                    yield ModelResponse(
                        content=response.text,
                        metadata={
                            "confidence": response.confidence,
                            "start_time": response.start_time,
                            "end_time": response.end_time,
                            "is_final": True,
                            **(response.metadata if hasattr(response, "metadata") else {})
                        }
                    )
                    
                    # Reset buffer
                    buffer.clear()
                    chunk_duration = 0
                    
            # Process any remaining audio
            if buffer:
                response = await self.aclient.chat.completions.create(
                    response_model=TranscriptionOutput,
                    messages=[{"role": "system", "content": "Process final audio chunk"}],
                    stream=True,
                    file=("audio", bytes(buffer), f"audio/{chunk.format.value}"),
                    **kwargs
                )
                
                yield ModelResponse(
                    content=response.text,
                    metadata={
                        "confidence": response.confidence,
                        "start_time": response.start_time,
                        "end_time": response.end_time,
                        "is_final": True,
                        **(response.metadata if hasattr(response, "metadata") else {})
                    }
                )
                
        except Exception as e:
            raise LLMError(f"Streaming transcription failed: {str(e)}")

    async def _record_audio_request(
        self,
        duration: float,
        audio_size: int,
        is_error: bool = False,
        token_usage: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record audio request metrics."""
        if self.metrics_service:
            metric_data = {
                "provider": self.provider_config.name,
                "model": self.provider_config.model,
                "total_requests": 1,
                "successful_requests": 1 if not is_error else 0,
                "failed_requests": 0 if not is_error else 1,
                "total_tokens": token_usage.get("total_tokens", 0),
                "average_latency": duration,
                "error_rate": 0.0 if not is_error else 1.0,
                "token_usage": token_usage,                
                "duration": duration,
                "metadata": {
                    "audio_size": audio_size,
                    "request_type": "audio",
                    **(metadata or {})
                }
            }
            await self.metrics_service.record_metric(metric_data)

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> ModelResponse[bytes]:
        """Synthesize text to speech using litellm pattern."""
        try:
            # Prepare synthesis parameters
            params = {
                "input": text,
                "voice": voice or self.provider_config.voice,
                "model": kwargs.get("model", self.provider_config.model),
                "response_format": format.value,
                "sampling_rate": sample_rate,
                **kwargs
            }
            
            # Use instructor for structured output
            response = await self.aclient.audio.speech.create(**params)
            
            return ModelResponse(
                content=response.content,
                metadata={
                    "format": format.value,
                    "sample_rate": sample_rate,
                    "duration": response.duration,
                    **(response.metadata if hasattr(response, "metadata") else {})
                },
                model=params["model"],
                provider=params["provider"]
            )
            
        except Exception as e:
            raise LLMError(f"Audio synthesis failed: {str(e)}") from e

    async def synthesize_stream(
        self,
        text_stream: AsyncIterator[str],
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[bytes]]:
        """Stream text to speech synthesis using litellm pattern."""
        try:
            async for text_chunk in text_stream:
                # Prepare synthesis parameters for chunk
                params = {
                    "input": text_chunk,
                    "voice": voice or self.provider_config.voice,
                    "model": kwargs.get("model", self.provider_config.model),
                    "response_format": format.value,
                    "sampling_rate": sample_rate,
                    **kwargs
                }
                
                # Use instructor for structured output
                response = await self.aclient.audio.speech.create(**params)
                
                yield ModelResponse(
                    content=response.content,
                    metadata={
                        "format": format.value,
                        "sample_rate": sample_rate,
                        "duration": response.duration,
                        "is_final": False,
                        **(response.metadata if hasattr(response, "metadata") else {})
                    },
                    model=params["model"],
                    provider=params["provider"]
                )
                
        except Exception as e:
            raise LLMError(f"Streaming audio synthesis failed: {str(e)}") from e 