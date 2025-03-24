from importlib.metadata import version

from .interfaces import AsyncCompleto
from .interfaces import SyncCompleto as Completo
from .models.embeddings import Embedding
from .models.messages import (
    AssistantMessage,
    Conversation,
    DeveloperMessage,
    UserMessage,
)
from .shortcuts import prompt, prompt_with_instructions, text

__all__ = [
    "Completo",
    "AsyncCompleto",
    "Conversation",
    "UserMessage",
    "DeveloperMessage",
    "AssistantMessage",
    "prompt",
    "text",
    "prompt_with_instructions",
    "Embedding",
]

__version__ = version("completo")
