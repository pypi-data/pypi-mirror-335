from collections.abc import AsyncIterator, Iterator

import anthropic
from anthropic.types.raw_content_block_delta_event import RawContentBlockDeltaEvent
from anthropic.types.raw_content_block_start_event import RawContentBlockStartEvent
from anthropic.types.raw_content_block_stop_event import RawContentBlockStopEvent
from anthropic.types.raw_message_delta_event import RawMessageDeltaEvent
from anthropic.types.raw_message_start_event import RawMessageStartEvent
from anthropic.types.raw_message_stop_event import RawMessageStopEvent
from anthropic.types.text_block import TextBlock
from anthropic.types.text_delta import TextDelta

from ...backends.anthropic.transformers import (
    AnthropicContentTransformer,
    AnthropicMessageTransformer,
)
from ...backends.engine import AsyncEngine, SyncEngine
from ...models.content import Content, TextContent
from ...models.messages import Message


class SyncAnthropicEngine(SyncEngine):
    client: anthropic.Anthropic
    max_tokens: int
    content_transformer: AnthropicContentTransformer
    message_transformer: AnthropicMessageTransformer

    def __init__(
        self, client: anthropic.Anthropic | None = None, max_tokens: int = 4096
    ):
        self.client = client or anthropic.Anthropic()
        self.max_tokens = max_tokens

        self.content_transformer = AnthropicContentTransformer()
        self.message_transformer = AnthropicMessageTransformer(self.content_transformer)

    def _stream_deltas(
        self, messages: list[Message], *, model: str
    ) -> Iterator[list[Content]]:
        response = self.client.messages.create(
            model=model,
            messages=self.message_transformer.transform_messages(messages),
            system=self.message_transformer.transform_systems(messages),
            max_tokens=self.max_tokens,
            stream=True,
        )

        for chunk in response:
            match chunk:
                case RawMessageStartEvent():
                    continue
                case RawMessageStopEvent():
                    continue
                case RawMessageDeltaEvent():
                    continue

                case RawContentBlockStartEvent():
                    if not isinstance(chunk.content_block, TextBlock):
                        raise NotImplementedError(
                            "Unsupported Anthropic content block type: "
                            f"{type(chunk.content_block)}"
                        )

                    content = TextContent(text=chunk.content_block.text)

                    # TODO: Yield initial empty content deltas?
                    if content.text:
                        yield [content]
                    continue

                case RawContentBlockDeltaEvent():
                    if not isinstance(chunk.delta, TextDelta):
                        raise NotImplementedError(
                            "Unsupported Anthropic content block type: "
                            f"{type(chunk.delta)}"
                        )

                    content = TextContent(text=chunk.delta.text)
                    yield [content]
                    continue

                case RawContentBlockStopEvent():
                    continue

    def get_name(self) -> str:
        return "Anthropic"


class AsyncAnthropicEngine(AsyncEngine):
    client: anthropic.AsyncAnthropic
    max_tokens: int
    content_transformer: AnthropicContentTransformer
    message_transformer: AnthropicMessageTransformer

    def __init__(
        self, client: anthropic.AsyncAnthropic | None = None, max_tokens: int = 4096
    ):
        self.client = client or anthropic.AsyncAnthropic()
        self.max_tokens = max_tokens

        self.content_transformer = AnthropicContentTransformer()
        self.message_transformer = AnthropicMessageTransformer(self.content_transformer)

    async def _stream_deltas(
        self, messages: list[Message], *, model: str
    ) -> AsyncIterator[list[Content]]:
        response = await self.client.messages.create(
            model=model,
            messages=self.message_transformer.transform_messages(messages),
            system=self.message_transformer.transform_systems(messages),
            max_tokens=self.max_tokens,
            stream=True,
        )

        async for chunk in response:
            match chunk:
                case RawMessageStartEvent():
                    continue
                case RawMessageStopEvent():
                    continue
                case RawMessageDeltaEvent():
                    continue

                case RawContentBlockStartEvent():
                    if not isinstance(chunk.content_block, TextBlock):
                        raise NotImplementedError(
                            "Unsupported Anthropic content block type: "
                            f"{type(chunk.content_block)}"
                        )

                    content = TextContent(text=chunk.content_block.text)

                    # TODO: Yield initial empty content deltas?
                    if content.text:
                        yield [content]
                    continue

                case RawContentBlockDeltaEvent():
                    if not isinstance(chunk.delta, TextDelta):
                        raise NotImplementedError(
                            "Unsupported Anthropic content block type: "
                            f"{type(chunk.delta)}"
                        )

                    content = TextContent(text=chunk.delta.text)
                    yield [content]
                    continue

                case RawContentBlockStopEvent():
                    continue

    def get_name(self) -> str:
        return "Anthropic"
