from openai.types.chat.chat_completion_content_part_param import (
    ChatCompletionContentPartParam,
)
from openai.types.chat.chat_completion_content_part_text_param import (
    ChatCompletionContentPartTextParam,
)
from openai.types.chat.chat_completion_message_param import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionDeveloperMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)

from ...backends.transformers import (
    ContentTransformer,
    MessageTransformer,
)
from ...models.content import Content, TextContent
from ...models.messages import (
    AssistantMessage,
    DeveloperMessage,
    Message,
    ToolResultMessage,
    UserMessage,
)
from ...util import is_instance_typeddict


class OpenAIContentTransformer(ContentTransformer[ChatCompletionContentPartParam]):
    def to_backend(self, content: Content) -> ChatCompletionContentPartParam:
        match content:
            case TextContent():
                return ChatCompletionContentPartTextParam(
                    type="text",
                    text=content.text,
                )

            case _:
                raise ValueError(f"Unsupported content type: {type(content)}")

    def from_backend(self, content: ChatCompletionContentPartParam) -> Content:
        """
        OpenAI uses TypedDicts as well as Pydantic models, but we can't validate
        TypedDicts at runtime, so we'll use Pydantic TypeAdapters.
        """

        if is_instance_typeddict(content, ChatCompletionContentPartTextParam):
            return TextContent(text=content["text"])  # type: ignore[typeddict-item]

        raise ValueError(f"Unsupported OpenAI content type: {type(content)}")


class OpenAIMessageTransformer(MessageTransformer[ChatCompletionMessageParam]):
    content_transformer: OpenAIContentTransformer

    def __init__(self, content_transformer: OpenAIContentTransformer):
        self.content_transformer = content_transformer

    def transform_message_to_backend(
        self, message: Message
    ) -> ChatCompletionMessageParam:
        match message:
            case UserMessage():
                return self._transform_user_message(message)
            case AssistantMessage():
                return self._transform_assistant_message(message)
            case DeveloperMessage():
                return self._transform_developer_message(message)
            case ToolResultMessage():
                return self._transform_tool_result_message(message)
            case _:
                raise ValueError(f"Unsupported message type: {type(message)}")

    def _transform_user_message(
        self, message: UserMessage
    ) -> ChatCompletionUserMessageParam:
        content = [self.content_transformer.to_backend(c) for c in message.content]
        return ChatCompletionUserMessageParam(
            role="user",
            content=content,
        )

    def _transform_assistant_message(
        self, message: AssistantMessage
    ) -> ChatCompletionAssistantMessageParam:
        content = [self.content_transformer.to_backend(c) for c in message.content]
        return ChatCompletionAssistantMessageParam(
            role="assistant",
            content=content,  # type: ignore[typeddict-item]  # Must be ChatCompletionContentPartTextParam | ChatCompletionContentPartRefusalParam
            # tool_calls=message.tool_calls,  # TODO: Add tool calls
        )

    def _transform_developer_message(
        self, message: DeveloperMessage
    ) -> ChatCompletionDeveloperMessageParam:
        content = [self.content_transformer.to_backend(c) for c in message.content]
        return ChatCompletionDeveloperMessageParam(
            role="developer",
            content=content,  # type: ignore[typeddict-item]  # Must be ChatCompletionContentPartTextParam
        )

    def _transform_tool_result_message(
        self, message: ToolResultMessage
    ) -> ChatCompletionToolMessageParam:
        content = [self.content_transformer.to_backend(c) for c in message.content]
        return ChatCompletionToolMessageParam(
            role="tool",
            content=content,  # type: ignore[typeddict-item]  # Must be ChatCompletionContentPartTextParam
            tool_call_id=message.tool_call.tool_call.id,
            # tool_calls=message.tool_calls,  # TODO: Add tool calls
        )
