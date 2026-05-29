"""Tool registry for managing available tools."""
from typing import Dict, Any, Optional, List, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
import importlib
import inspect

from ...config import Config, ToolConfig
from ..utils import ToolError
from ..tools.base import BaseTool, ToolContext

logger = logging.getLogger(__name__)

@dataclass
class ToolInfo:
    """Information about a registered tool."""
    name: str
    description: str
    tool_class: Type[BaseTool]
    config: ToolConfig
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)

class ToolManager:
    """Manager for available tools."""
    
    def __init__(self):
        """Initialize tool manager."""
        self.tools: Dict[str, ToolInfo] = {}
        
    def register_tool(
        self,
        name: str,
        tool_class: Type[BaseTool],
        description: Optional[str] = None,
        config: Optional[ToolConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolInfo:
        """Register a new tool."""
        if name in self.tools:
            raise ToolError(f"Tool {name} already registered")
            
        tool_info = ToolInfo(
            name=name,
            description=description or tool_class.__doc__ or "",
            tool_class=tool_class,
            config=config or ToolConfig(),
            metadata=metadata or {}
        )
        
        self.tools[name] = tool_info
        logger.info(f"Registered tool: {name}")
        return tool_info
        
    def unregister_tool(self, name: str):
        """Unregister a tool."""
        if name not in self.tools:
            raise ToolError(f"Tool {name} not found")
            
        del self.tools[name]
        logger.info(f"Unregistered tool: {name}")
        
    def get_tool(self, name: str, context: ToolContext) -> BaseTool:
        """Get tool instance with context."""
        if name not in self.tools:
            raise ToolError(f"Tool {name} not found")
            
        tool_info = self.tools[name]
        return tool_info.tool_class(context)
        
    def list_tools(self) -> List[ToolInfo]:
        """List all registered tools."""
        return list(self.tools.values())
        
    def clear(self):
        """Clear all registered tools."""
        self.tools.clear()
        
    @classmethod
    def from_config(cls, config: Config) -> "ToolManager":
        """Create manager from configuration."""
        manager = cls()
        
        # Register tools from config
        for tool_config in config.tools:
            try:
                # Import module
                module = importlib.import_module(tool_config.module)
                
                # Get tool class
                tool_class = getattr(module, tool_config.handler)
                
                if not issubclass(tool_class, BaseTool):
                    raise ToolError(f"Tool {tool_config.name} must inherit from BaseTool")
                
                # Register tool
                manager.register_tool(
                    name=tool_config.name,
                    tool_class=tool_class,
                    description=tool_config.description,
                    config=tool_config,
                    metadata=tool_config.metadata
                )
                
            except Exception as e:
                logger.error(f"Failed to register tool {tool_config.name}: {e}")
                
        return manager
        
    async def execute_tool(
        self,
        name: str,
        context: ToolContext,
        parameters: Dict[str, Any]
    ) -> Any:
        """Execute a tool."""
        tool = self.get_tool(name, context)
        
        try:
            # Validate parameters
            tool.validate_parameters(**parameters)
            
            # Execute tool
            result = await tool.execute(**parameters)
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute tool {name}: {e}")
            raise ToolError(f"Tool execution failed: {str(e)}")
            
    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self.tools) 