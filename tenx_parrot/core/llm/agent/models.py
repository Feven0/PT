from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional, Union
from datetime import datetime


class ContentData(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentUpdate(BaseModel):
    type: Literal['content']
    data: ContentData


class MessageData(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageUpdate(BaseModel):
    type: Literal['message']
    data: MessageData


class ToolCallData(BaseModel):
    tool: str
    input: Dict[str, Any] = Field(default_factory=dict)
    call_id: str
    timestamp: datetime


class ToolCallUpdate(BaseModel):
    type: Literal['tool_call']
    data: ToolCallData


class ToolResultData(BaseModel):
    call_id: str
    tool: str
    input: Dict[str, Any] = Field(default_factory=dict)
    result: Any
    status: Literal['completed', 'failed']
    timestamp: datetime


class ToolResultUpdate(BaseModel):
    type: Literal['tool_result']
    data: ToolResultData


class ErrorData(BaseModel):
    error: str
    task_id: Optional[str] = None


class ErrorUpdate(BaseModel):
    type: Literal['error']
    data: ErrorData


class CompleteData(BaseModel):
    task_id: str
    content: str
    status: Literal['completed']


class CompleteUpdate(BaseModel):
    type: Literal['complete']
    data: CompleteData


# A union type for all possible agent stream responses
AgentStreamResponse = Union[
    ContentUpdate,
    MessageUpdate,
    ToolCallUpdate,
    ToolResultUpdate,
    ErrorUpdate,
    CompleteUpdate
] 