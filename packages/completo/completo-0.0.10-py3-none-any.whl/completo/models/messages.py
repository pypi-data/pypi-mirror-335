"""
Messages hold the state of the conversation so far. These are then translated into the
backend specific format.

"""

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, field_validator

from .content import Content, TextContent
from .tools import ToolCall, ToolCallResult


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    DEVELOPER = "developer"
    TOOL = "tool"


class BaseMessage(BaseModel):
    role: Role
    content: list[Content]

    @field_validator("content")
    def content_to_list(cls: Self, v: Content | list[Content] | str) -> list[Content]:
        if isinstance(v, str):
            return [TextContent(text=v)]
        if not isinstance(v, list):
            return [v]
        return v


class UserMessage(BaseMessage):
    role: Literal[Role.USER] = Role.USER


class AssistantMessage(BaseMessage):
    role: Literal[Role.ASSISTANT] = Role.ASSISTANT
    tool_calls: list[ToolCall] = Field(default_factory=list)

    backend_name: str
    model_name: str


class DeveloperMessage(BaseMessage):
    role: Literal[Role.DEVELOPER] = Role.DEVELOPER


class ToolResultMessage(BaseMessage):
    role: Literal[Role.TOOL] = Role.TOOL
    tool_call: ToolCallResult


Message = Annotated[
    UserMessage | AssistantMessage | DeveloperMessage | ToolResultMessage,
    Field(discriminator="role"),
]


class Conversation(BaseModel):
    messages: list[Message]
