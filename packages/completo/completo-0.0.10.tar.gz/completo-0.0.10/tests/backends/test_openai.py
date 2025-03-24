from openai.types.chat.chat_completion_content_part_text_param import (
    ChatCompletionContentPartTextParam,
)
from pydantic import TypeAdapter

from completo.backends.openai import (
    OpenAIContentTransformer,
    OpenAIMessageTransformer,
)
from completo.models.content import TextContent
from completo.models.messages import Conversation


def test_transform_content():
    transformer = OpenAIContentTransformer()

    content = TextContent(text="Hello, world!")
    openai_content = transformer.to_backend(content)

    adapter = TypeAdapter(ChatCompletionContentPartTextParam)
    assert adapter.validate_python(openai_content) == openai_content


def test_translate_messages(conversation: Conversation):
    transformer = OpenAIMessageTransformer(
        content_transformer=OpenAIContentTransformer(),
    )

    openai_messages = transformer.to_backend(conversation.messages)

    assert len(openai_messages) == len(conversation.messages)
