"""Chain manager for handling chain creation and execution."""
from typing import List, Optional, Dict, Any, AsyncIterator, Union, Set

from core.base.manager import BaseManager
from core.config.base import AppConfig
from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.types.llm import Message, ModelResponse, ChainState
from .chain import Chain
from .chain_state import ChainStateManager
from ..client import LLMClient
from ..response_formatter import ChainResponse
from ..errors import handle_chain_error

class ChainManager(BaseManager):
    """Manages chain creation and execution."""
    
    def __init__(self, 
                 name: str,
                 config: AppConfig,
                 llm_client: LLMClient,                                 
                 metrics: Optional[MetricsManager] = None,
                 logger: Optional[BackendLogger] = None,
                 dependencies: Optional[Set[str]] = None):
        """Initialize chain manager."""
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        self.llm_client = llm_client
        self.state_manager = ChainStateManager()
    
    def create_chain(self, 
                     name: str, 
                     messages: List[Message], 
                     metadata: Optional[Dict[str, Any]] = None) -> Chain:
        """Create a new chain with the given messages and metadata."""
        chain = Chain(
            llm_client=self.llm_client,
            name=name,
            metadata=metadata or {}
        )
        
        # Add messages to chain
        for msg in messages:
            if not isinstance(msg, Message):
                msg = Message(
                    role=msg.role,
                    content=msg.content,
                    name=getattr(msg, 'name', None),
                    metadata=getattr(msg, 'metadata', {})
                )
            chain.add_message(msg)
            
        return chain
    
    async def execute_chain(self, chain: Chain) -> ChainResponse:
        """Execute a chain and manage its state."""
        try:
            # Execute chain
            response = await chain.execute()
            return response
            
        except Exception as e:
            # Handle chain failure
            error = handle_chain_error(e, {
                "chain_id": chain.chain_id,
                "name": chain.name,
                "metadata": chain.metadata
            })
            raise error

    async def stream_chain(self, chain: Chain) -> AsyncIterator[Union[ModelResponse, Dict[str, Any]]]:
        """Stream chain execution."""
        try:
            # Stream chain execution
            async for chunk in chain.stream():
                yield chunk
                
        except Exception as e:
            # Handle chain failure
            error = handle_chain_error(e, {
                "chain_id": chain.chain_id,
                "name": chain.name,
                "metadata": chain.metadata
            })
            yield {
                "type": "error",
                "data": error.to_dict()
            }
            raise error 