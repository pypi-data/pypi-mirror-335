from collections.abc import Sequence

from anthropic.types.content_block import ContentBlock
from anthropic.types.message_param import MessageParam
from anthropic.types.text_block import TextBlock
from anthropic.types.text_block_param import TextBlockParam

from ...backends.transformers import ContentTransformer, MessageTransformer
from ...models.content import Content, TextContent
from ...models.messages import (
    AssistantMessage,
    DeveloperMessage,
    Message,
    UserMessage,
)


class AnthropicContentTransformer(ContentTransformer[ContentBlock]):
    def to_backend(self, content: Content) -> ContentBlock:
        match content:
            case TextContent():
                return self.transform_text(content)
            case _:
                raise ValueError(f"Unsupported content type: {type(content)}")

    def transform_text(self, content: TextContent) -> TextBlock:
        return TextBlock(type="text", text=content.text)

    """
    TODO:
    TextBlockParam,
    ImageBlockParam,
    ToolUseBlockParam,
    ToolResultBlockParam,
    DocumentBlockParam,
    """


class AnthropicMessageTransformer(MessageTransformer[MessageParam | TextBlockParam]):
    content_transformer: AnthropicContentTransformer

    def __init__(self, content_transformer: AnthropicContentTransformer):
        self.content_transformer = content_transformer

    def to_backend(
        self, messages: Sequence[Message]
    ) -> Sequence[MessageParam | TextBlockParam]:
        raise NotImplementedError(
            "Anthropic accepts messages, and system prompts separately "
            "- use transform_messages and transform_systems"
        )

    def transform_messages(self, messages: Sequence[Message]) -> Sequence[MessageParam]:
        m = []
        for message in messages:
            if not isinstance(message, DeveloperMessage):
                m.append(self.transform_message_to_backend(message))
        return m

    def transform_systems(
        self, messages: Sequence[Message]
    ) -> Sequence[TextBlockParam]:
        m = []
        for message in messages:
            if isinstance(message, DeveloperMessage):
                m.append(self.transform_developer_message(message))
        return m

    def transform_message_to_backend(self, message: Message) -> MessageParam:
        match message:
            case UserMessage():
                return self.transform_user_message(message)
            case AssistantMessage():
                return self.transform_assistant_message(message)
            case _:
                raise ValueError(f"Unsupported message type: {type(message)}")

    def transform_user_message(self, message: UserMessage) -> MessageParam:
        return MessageParam(
            role="user",
            content=[
                self.content_transformer.to_backend(content)
                for content in message.content
            ],
        )

    def transform_assistant_message(self, message: AssistantMessage) -> MessageParam:
        return MessageParam(
            role="assistant",
            content=[
                self.content_transformer.to_backend(content)
                for content in message.content
            ],
        )

    def transform_developer_message(self, message: DeveloperMessage) -> TextBlockParam:
        system_content = ""
        for content in message.content:
            if not isinstance(content, TextContent):
                raise ValueError(
                    f"Unsupported content type for system prompt: {type(content)}"
                )

            system_content += (
                content.text + "\n"
            )  # TODO: Undocumented newline behaviour, what's best?

        return TextBlockParam(
            type="text",
            text=system_content,
        )
