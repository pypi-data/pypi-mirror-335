from collections.abc import AsyncIterator, Iterator
from typing import Generic, TypeVar

from completo.models.embeddings import Embedding

from .backends.engine import AsyncEngine, SyncEngine
from .models.completions import Completion, CompletionDelta
from .models.messages import AssistantMessage, Conversation, Message

EngineType = TypeVar("EngineType", SyncEngine, AsyncEngine)


class BaseCompleto(Generic[EngineType]):
    default_engine: EngineType
    default_completions_model: str | None
    default_embeddings_model: str | None

    def _get_engine(self, engine: EngineType | None = None) -> EngineType:
        e = engine or self.default_engine
        if not e:
            raise ValueError("No engine provided")
        return e

    def _get_completions_model(self, model: str | None = None) -> str:
        m = model or self.default_completions_model
        if not m:
            raise ValueError("No model provided")
        return m

    def _get_embeddings_model(self, model: str | None = None) -> str:
        m = model or self.default_embeddings_model
        if not m:
            raise ValueError("No model provided")
        return m


class SyncCompleto(BaseCompleto[SyncEngine]):
    default_engine: SyncEngine
    default_completions_model: str | None
    default_embeddings_model: str | None

    def __init__(
        self,
        default_engine: SyncEngine,
        default_completions_model: str | None = None,
        default_embeddings_model: str | None = None,
    ):
        self.default_engine = default_engine
        self.default_completions_model = default_completions_model
        self.default_embeddings_model = default_embeddings_model

    def complete(
        self,
        conversation: Conversation,
        engine: SyncEngine | None = None,
        model: str | None = None,
    ) -> Completion:
        engine_ = self._get_engine(engine)
        model_ = self._get_completions_model(model)

        return engine_.complete(conversation.messages, model=model_)

    def respond(
        self,
        conversation: Conversation,
        engine: SyncEngine | None = None,
        model: str | None = None,
    ) -> Message:
        engine_ = self._get_engine(engine)
        model_ = self._get_completions_model(model)

        return AssistantMessage(
            content=self.complete(conversation, engine_, model_).content,
            backend_name=engine_.get_name(),
            model_name=model_,
        )

    def stream(
        self,
        conversation: Conversation,
        engine: SyncEngine | None = None,
        model: str | None = None,
    ) -> Iterator[CompletionDelta]:
        engine_ = self._get_engine(engine)
        model_ = self._get_completions_model(model)

        yield from engine_.stream(conversation.messages, model=model_)

    def embed(
        self,
        input_text: str,
        engine: SyncEngine | None = None,
        model: str | None = None,
    ) -> Embedding:
        engine_ = self._get_engine(engine)
        model_ = self._get_embeddings_model(model)
        return engine_.embed(input_text, model=model_)


class AsyncCompleto(BaseCompleto[AsyncEngine]):
    default_engine: AsyncEngine
    default_completions_model: str | None
    default_embeddings_model: str | None

    def __init__(
        self,
        default_engine: AsyncEngine,
        default_completions_model: str | None = None,
        default_embeddings_model: str | None = None,
    ):
        self.default_engine = default_engine
        self.default_completions_model = default_completions_model
        self.default_embeddings_model = default_embeddings_model

    async def complete(
        self,
        conversation: Conversation,
        engine: AsyncEngine | None = None,
        model: str | None = None,
    ) -> Completion:
        engine_ = self._get_engine(engine)
        model_ = self._get_completions_model(model)

        return await engine_.complete(conversation.messages, model=model_)

    async def stream(
        self,
        conversation: Conversation,
        engine: AsyncEngine | None = None,
        model: str | None = None,
    ) -> AsyncIterator[CompletionDelta]:
        engine_ = self._get_engine(engine)
        model_ = self._get_completions_model(model)

        async for delta_completion in engine_.stream(
            conversation.messages, model=model_
        ):
            yield delta_completion

    async def respond(
        self,
        conversation: Conversation,
        engine: AsyncEngine | None = None,
        model: str | None = None,
    ) -> Message:
        engine_ = self._get_engine(engine)
        model_ = self._get_completions_model(model)

        return AssistantMessage(
            content=(await self.complete(conversation, engine_, model_)).content,
            backend_name=engine_.get_name(),
            model_name=model_,
        )

    async def embed(
        self,
        input_text: str,
        engine: AsyncEngine | None = None,
        model: str | None = None,
    ) -> Embedding:
        engine_ = self._get_engine(engine)
        model_ = self._get_embeddings_model(model)
        return await engine_.embed(input_text, model=model_)
