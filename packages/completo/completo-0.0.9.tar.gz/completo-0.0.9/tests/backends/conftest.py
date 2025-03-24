import pytest

from completo.models.content import TextContent
from completo.models.messages import (
    AssistantMessage,
    Conversation,
    DeveloperMessage,
    UserMessage,
)


@pytest.fixture
def conversation() -> Conversation:
    return Conversation(
        messages=[
            DeveloperMessage(
                content=[
                    TextContent(text="You are a helpful assistant."),
                ]
            ),
            UserMessage(
                content=[
                    TextContent(text="Hello, world!"),
                ]
            ),
            AssistantMessage(
                content=[
                    TextContent(text="Hello! How can I help you today?"),
                ],
                backend_name="OpenAI",
                model_name="gpt-4o-mini",
            ),
            # ToolResultMessage(content="Hello, world!"),
        ]
    )
