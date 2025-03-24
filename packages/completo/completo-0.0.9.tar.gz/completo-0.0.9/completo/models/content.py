"""
Discriminates between various types of message content.

"""

import base64
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field


class BaseContent(BaseModel):
    type: str

    def append(self, other: Self) -> None:
        raise ValueError(f"Cannot append content of {type(other)} to {type(self)}")

    def __str__(self) -> str:
        raise NotImplementedError(f"Cannot convert {type(self)} to string")


class TextContent(BaseContent):
    type: Literal["text"] = Field(default="text")
    text: str

    def append(self, other: Self) -> None:
        self.text += other.text

    def __str__(self) -> str:
        return self.text


class ReasoningContent(BaseContent):
    type: Literal["reasoning"] = Field(default="reasoning")
    reasoning: str

    def __str__(self) -> str:
        return self.reasoning


class ImageContent(BaseContent):
    type: Literal["image"] = Field(default="image")
    mimetype: str
    data: bytes

    def as_base64_uri(self) -> str:
        return f"data:{self.mimetype};base64,{base64.b64encode(self.data).decode()}"


class VideoContent(BaseContent):
    type: Literal["video"] = Field(default="video")
    mimetype: str
    data: bytes

    def as_base64_uri(self) -> str:
        return f"data:{self.mimetype};base64,{base64.b64encode(self.data).decode()}"


class AudioContent(BaseContent):
    type: Literal["audio"] = Field(default="audio")
    mimetype: str
    data: bytes

    def as_base64_uri(self) -> str:
        return f"data:{self.mimetype};base64,{base64.b64encode(self.data).decode()}"


Content = Annotated[
    TextContent | ReasoningContent | ImageContent | VideoContent | AudioContent,
    Field(discriminator="type"),
]
