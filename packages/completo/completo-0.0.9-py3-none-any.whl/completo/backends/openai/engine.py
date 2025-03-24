from collections.abc import AsyncIterator, Iterator

import openai
from openai.types.chat.chat_completion_content_part_param import (
    ChatCompletionContentPartTextParam,
)

from ...backends.engine import AsyncEngine, SyncEngine
from ...backends.openai.transformers import (
    OpenAIContentTransformer,
    OpenAIMessageTransformer,
)
from ...models.content import Content
from ...models.messages import Message


class SyncOpenAIEngine(SyncEngine):
    client: openai.OpenAI
    content_transformer: OpenAIContentTransformer
    message_transformer: OpenAIMessageTransformer

    def __init__(self, client: openai.OpenAI | None = None):
        self.client = client or openai.OpenAI()

        self.content_transformer = OpenAIContentTransformer()
        self.message_transformer = OpenAIMessageTransformer(self.content_transformer)
        # self.tool_call_transformer = ToolCallTransformer()
        # self.tool_call_result_transformer = ToolCallResultTransformer()

    def _stream_deltas(
        self, messages: list[Message], *, model: str
    ) -> Iterator[list[Content]]:
        openai_messages = self.message_transformer.to_backend(messages)

        completion = self.client.chat.completions.create(
            messages=openai_messages,
            model=model,
            stream=True,
        )

        for chunk in completion:
            if content := chunk.choices[0].delta.content:
                chunk_content = self.content_transformer.from_backend(
                    string_content_to_text_content(content)
                )

                yield [chunk_content]

    def _embed(self, input_text: str, *, model: str) -> list[float]:
        embedding = self.client.embeddings.create(
            input=input_text,
            model=model,
        )

        return embedding.data[0].embedding

    def get_name(self) -> str:
        return "OpenAI"


class AsyncOpenAIEngine(AsyncEngine):
    client: openai.AsyncOpenAI
    content_transformer: OpenAIContentTransformer
    message_transformer: OpenAIMessageTransformer

    def __init__(self, client: openai.AsyncOpenAI | None = None):
        self.client = client or openai.AsyncOpenAI()

        self.content_transformer = OpenAIContentTransformer()
        self.message_transformer = OpenAIMessageTransformer(self.content_transformer)
        # self.tool_call_transformer = ToolCallTransformer()
        # self.tool_call_result_transformer = ToolCallResultTransformer()

    async def _stream_deltas(
        self, messages: list[Message], *, model: str
    ) -> AsyncIterator[list[Content]]:
        openai_messages = self.message_transformer.to_backend(messages)

        completion = await self.client.chat.completions.create(
            messages=openai_messages,
            model=model,
            stream=True,
        )

        async for chunk in completion:
            if content := chunk.choices[0].delta.content:
                chunk_content = self.content_transformer.from_backend(
                    string_content_to_text_content(content)
                )

                yield [chunk_content]

    async def _embed(self, input_text: str, *, model: str) -> list[float]:
        embedding = await self.client.embeddings.create(
            input=input_text,
            model=model,
        )

        return embedding.data[0].embedding

    def get_name(self) -> str:
        return "OpenAI"


def string_content_to_text_content(
    content: str | None,
) -> ChatCompletionContentPartTextParam:
    return ChatCompletionContentPartTextParam(
        type="text",
        text=content or "",
    )
