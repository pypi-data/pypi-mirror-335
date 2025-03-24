"""
Models holding requests for, and results of tools.

"""

from typing import Any

from pydantic import BaseModel


class ToolCall(BaseModel):
    id: str
    function: str
    arguments: dict[str, Any]


class ToolCallResult(BaseModel):
    tool_call: ToolCall
    content: str  # TODO: Make this a list of Content
    is_error: bool
