"""OpenAI provider implementation."""
from typing import Any, Dict, List, Optional, Type, TypeVar, AsyncIterator

import aisuite
import instructor
from instructor import OpenAISchema

from core.types.model import CoreBaseModel
from core.types.prompt import PromptMessage
from core.config.llm_config import OpenAIConfig
from core.llm.providers.base import BaseLLMProvider

T = TypeVar("T", bound=CoreBaseModel)

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation."""

    def __init__(self, name: str, config: OpenAIConfig) -> None:
        """Initialize provider.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        super().__init__(name, config)
        self._client = aisuite.OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            streaming=config.streaming,
            timeout=config.timeout,
            retry_count=config.retry_count
        )
        self._instructor = instructor.patch(self._client)

    async def _generate_impl(
        self,
        messages: List[PromptMessage],
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> T:
        """Implementation for generating responses."""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        if output_model is not None and issubclass(output_model, OpenAISchema):
            # Use instructor for structured output
            response = await self._instructor.chat.completions.create(
                messages=formatted_messages,
                response_model=output_model,
                **kwargs
            )
            return response
        else:
            # Use regular completion
            response = await self._client.chat.completions.create(
                messages=formatted_messages,
                **kwargs
            )
            return response.choices[0].message.content

    async def _generate_stream_impl(
        self,
        messages: List[PromptMessage],
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> AsyncIterator[T]:
        """Implementation for generating streaming responses."""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        if output_model is not None and issubclass(output_model, OpenAISchema):
            # Use instructor for structured streaming
            async for chunk in self._instructor.chat.completions.create(
                messages=formatted_messages,
                response_model=output_model,
                stream=True,
                **kwargs
            ):
                yield chunk
        else:
            # Use regular streaming
            async for chunk in self._client.chat.completions.create(
                messages=formatted_messages,
                stream=True,
                **kwargs
            ):
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content 