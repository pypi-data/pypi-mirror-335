"""
For convenience, we define a Completion model that can be used to return the result of a
completion. This is in addition to an AssistantMessage, which is held in the
Conversation.

"""

from pydantic import BaseModel

from .content import Content, TextContent


class Completion(BaseModel):
    content: list[Content]

    def __str__(self) -> str:
        return "\n".join(
            content.text for content in self.content if isinstance(content, TextContent)
        )


class CompletionDelta(BaseModel):
    full: Completion
    delta: list[Content]

    def __str__(self) -> str:
        return "\n".join(
            content.text for content in self.delta if isinstance(content, TextContent)
        )
