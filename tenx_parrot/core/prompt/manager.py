"""Prompt manager implementation."""
from typing import Any, Dict, List, Optional
import os
import json
import yaml
from pathlib import Path

from core.base.manager import BaseManager
from core.types.prompt import (
    PromptMessage, 
    PromptTemplate
)
from core.config.prompt_config import PromptConfig
from core.types.components import HealthStatus
from core.types.metrics import MetricType

class PromptManager(BaseManager):
    """Manager for prompt templates."""

    REQUIRED_CONFIG = {
        "enabled": bool,
        "template_paths": list,
        "cache_templates": bool,
        "cache_ttl": int,
        "max_retries": int,
        "timeout": int,
        "default_variables": dict
    }

    def __init__(
        self,
        name: str,
        config: Any,
        metrics: Optional[Any] = None,
        logger: Optional[Any] = None,
        dependencies: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize manager.
        
        Args:
            name: Manager name
            config: Manager configuration
            metrics: Optional metrics manager
            logger: Optional logger
            dependencies: Optional dependencies
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        self._templates: Dict[str, PromptTemplate] = {}

    async def _initialize_impl(self) -> None:
        """Implementation for initialization."""
        # Load templates from configured paths
        await self.load_templates()

        # Register metrics
        if self._metrics:
            self._metrics.register_metric(
                name="prompt_renders_total",
                type=MetricType.COUNTER,
                description="Total number of prompt renders",
                labels={"template": "template", "success": "success"},
                component=self.name
            )
            self._metrics.register_metric(
                name="prompt_render_duration_seconds",
                type=MetricType.HISTOGRAM,
                description="Duration of prompt renders in seconds",
                labels={"template": "template"},
                component=self.name
            )
            self._metrics.register_metric(
                name="prompt_tokens_total",
                type=MetricType.COUNTER,
                description="Total number of tokens in rendered prompts",
                labels={"template": "template"},
                component=self.name
            )

    async def _start_impl(self) -> None:
        """Implementation for starting."""
        pass

    async def _stop_impl(self) -> None:
        """Implementation for stopping."""
        pass

    async def _check_health_impl(self) -> Dict[str, Any]:
        """Implementation for health check."""
        return {
            "templates": {
                "count": len(self._templates),
                "names": list(self._templates.keys())
            }
        }

    def register_template(self, template: PromptTemplate) -> None:
        """Register a prompt template.
        
        Args:
            template: Template to register
        """
        self._templates[template.name] = template

    def get_templates(self) -> Dict[str, PromptTemplate]:
        """Get registered templates.
        
        Returns:
            Dictionary of registered templates
        """
        return self._templates

    def get_template(self, name: str) -> PromptTemplate:
        """Get a specific template.
        
        Args:
            name: Template name
            
        Returns:
            Prompt template
            
        Raises:
            KeyError: If template not found
        """
        if name not in self._templates:
            raise KeyError(f"Template {name} not found")
        return self._templates[name]

    async def render(
        self,
        template_name: str,
        **kwargs: Any
    ) -> List[PromptMessage]:
        """Render a template with variables.
        
        Args:
            template_name: Name of template to render
            **kwargs: Variables to render template with
            
        Returns:
            List of rendered prompt messages
            
        Raises:
            KeyError: If template not found
            ValueError: If template variables are invalid
        """
        if template_name not in self._templates:
            raise KeyError(f"Template {template_name} not found")

        try:
            # Merge default variables with provided kwargs
            variables = {**self._config["default_variables"], **kwargs}
            messages = self._templates[template_name].format(**variables)
            
            if self._metrics:
                self._metrics.increment_counter(
                    "prompt_renders_total",
                    {"template": template_name, "success": "true"}
                )
                # TODO: Add token counting
                # self._metrics.increment_counter(
                #     "prompt_tokens_total",
                #     {"template": template_name},
                #     len(tokens)
                # )
            return messages
        except Exception as e:
            if self._metrics:
                self._metrics.increment_counter(
                    "prompt_renders_total",
                    {"template": template_name, "success": "false"}
                )
            raise ValueError(f"Failed to render template {template_name}: {str(e)}")

    async def load_templates(self, paths: Optional[List[str]] = None) -> None:
        """Load templates from paths.
        
        Args:
            paths: Optional list of paths to load from (uses config if not specified)
            
        Raises:
            ValueError: If template loading fails
        """
        template_paths = paths or self._config.get("prompt_config", {}).get("template_paths",[])
        
        for path in template_paths:
            try:
                path_obj = Path(path)
                if not path_obj.exists():
                    if self._logger:
                        self._logger.warning(f"Template path {path} does not exist")
                    continue

                if path_obj.is_file():
                    await self._load_template_file(path_obj)
                elif path_obj.is_dir():
                    for file_path in path_obj.rglob("*"):
                        if file_path.suffix in [".json", ".yaml", ".yml"]:
                            await self._load_template_file(file_path)
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Failed to load templates from {path}: {str(e)}")
                raise ValueError(f"Failed to load templates from {path}: {str(e)}")

    async def _load_template_file(self, path: Path) -> None:
        """Load templates from a file.
        
        Args:
            path: Path to template file
            
        Raises:
            ValueError: If template loading fails
        """
        try:
            with path.open() as f:
                if path.suffix == ".json":
                    data = json.load(f)
                else:  # .yaml or .yml
                    data = yaml.safe_load(f)

            if isinstance(data, dict):
                templates = [data]
            elif isinstance(data, list):
                templates = data
            else:
                raise ValueError(f"Invalid template format in {path}")

            for template_data in templates:
                template = PromptTemplate(**template_data)
                self.register_template(template)

            if self._logger:
                self._logger.info(f"Loaded {len(templates)} templates from {path}")
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to load template file {path}: {str(e)}")
            raise ValueError(f"Failed to load template file {path}: {str(e)}") 