from completo.models.content import TextContent
from completo.models.messages import Conversation, DeveloperMessage, UserMessage


def text(text: str) -> TextContent:
    return TextContent(text=text)


def prompt(message: str) -> Conversation:
    return Conversation(messages=[UserMessage(content=[text(message)])])


def prompt_with_instructions(instructions: str, message: str) -> Conversation:
    return Conversation(
        messages=[
            DeveloperMessage(content=[text(instructions)]),
            UserMessage(content=[text(message)]),
        ]
    )
