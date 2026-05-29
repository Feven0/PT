"""Chain state management."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from core.types.llm import ChainState, ChainStep, ChainStatus

class ChainStateManager:
    """Manages chain state."""
    
    def __init__(self):
        """Initialize state manager."""
        self._chains: Dict[str, ChainState] = {}
        
    def create_chain(
        self,
        chain_id: str,
        name: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create new chain state."""
        if chain_id in self._chains:
            raise ValueError(f"Chain {chain_id} already exists")
            
        self._chains[chain_id] = ChainState(
            chain_id=chain_id,
            name=name,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
    def get_chain(self, chain_id: str) -> ChainState:
        """Get chain state."""
        if chain_id not in self._chains:
            raise ValueError(f"Chain {chain_id} not found")
        return self._chains[chain_id]
        
    def add_step(
        self,
        chain_id: str,
        step: ChainStep
    ) -> None:
        """Add step to chain."""
        chain = self.get_chain(chain_id)
        chain.steps.append(step)
        
    def update_step(
        self,
        chain_id: str,
        step_name: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update step state."""
        chain = self.get_chain(chain_id)
        for step in chain.steps:
            if step.name == step_name:
                for key, value in updates.items():
                    if hasattr(step, key):
                        setattr(step, key, value)
                break
                
    def start_chain(self, chain_id: str) -> None:
        """Start chain execution."""
        chain = self.get_chain(chain_id)
        chain.status = ChainStatus.RUNNING
        chain.started_at = datetime.now()
        chain.current_step = chain.steps[0].name if chain.steps else None
        
    def complete_chain(
        self,
        chain_id: str,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """Complete chain execution."""
        chain = self.get_chain(chain_id)
        chain.status = ChainStatus.COMPLETED
        chain.completed_at = datetime.now()
        if result:
            chain.result = result
            
    def fail_chain(
        self,
        chain_id: str,
        error: Dict[str, Any]
    ) -> None:
        """Fail chain execution."""
        chain = self.get_chain(chain_id)
        chain.status = ChainStatus.ERROR
        chain.completed_at = datetime.now()
        chain.error = error
        
    def cancel_chain(
        self,
        chain_id: str,
        reason: Optional[str] = None
    ) -> None:
        """Cancel chain execution."""
        chain = self.get_chain(chain_id)
        chain.status = ChainStatus.CANCELLED
        chain.completed_at = datetime.now()
        chain.metadata["cancel_reason"] = reason
        
    def update_chain(
        self,
        chain_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update chain state."""
        chain = self.get_chain(chain_id)
        for key, value in updates.items():
            if hasattr(chain, key):
                setattr(chain, key, value)
            else:
                chain.metadata[key] = value 