from completo.models.messages import Conversation, DeveloperMessage, UserMessage
from completo.shortcuts import prompt, prompt_with_instructions


def test_prompt():
    m = prompt("Hello, world!")

    assert isinstance(m, Conversation)
    assert len(m.messages) == 1
    assert isinstance(m.messages[0], UserMessage)
    assert m.messages[0].content[0].text == "Hello, world!"


def test_prompt_with_instructions():
    m = prompt_with_instructions("You are a helpful assistant.", "Hello, world!")

    assert isinstance(m, Conversation)
    assert len(m.messages) == 2

    assert isinstance(m.messages[0], DeveloperMessage)
    assert m.messages[0].content[0].text == "You are a helpful assistant."

    assert isinstance(m.messages[1], UserMessage)
    assert m.messages[1].content[0].text == "Hello, world!"
