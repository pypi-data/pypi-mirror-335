from collections.abc import AsyncIterator, Iterator

from completo.models.embeddings import Embedding

from ..models.completions import Completion, CompletionDelta
from ..models.content import Content
from ..models.messages import AssistantMessage, Message


class SyncEngine:
    def complete(self, messages: list[Message], *, model: str) -> Completion:
        while True:
            completion: Completion
            for delta in self.stream(messages, model=model):
                completion = delta.full

            # TODO: Implement tool calls

            messages.append(
                AssistantMessage(
                    content=completion.content,
                    backend_name=self.get_name(),
                    model_name=model,
                )
            )
            return completion

    def stream(
        self, messages: list[Message], *, model: str
    ) -> Iterator[CompletionDelta]:
        completion = Completion(content=[])
        for contents in self._stream_deltas(messages, model=model):
            # Append to the previous content if it's the same type
            if completion.content and isinstance(
                completion.content[-1], type(contents[0])
            ):
                # TODO: Work out why isinstance is not sufficient
                completion.content[-1].append(contents[0])  # type: ignore[arg-type]
                # Add any additional content items
                completion.content.extend(contents[1:])
            else:
                # Otherwise, append the new content
                completion.content.extend(contents)

            yield CompletionDelta(full=completion, delta=contents)

    def embed(self, input_text: str, *, model: str) -> Embedding:
        return Embedding(
            input_text=input_text, embedding=self._embed(input_text, model=model)
        )

    def _embed(self, input_text: str, *, model: str) -> list[float]:
        raise NotImplementedError("Embeddings are not supported for this engine")

    def _stream_deltas(
        self, messages: list[Message], *, model: str
    ) -> Iterator[list[Content]]:
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError("Engine should provide a display name, e.g. 'OpenAI'")


class AsyncEngine:
    async def complete(self, messages: list[Message], *, model: str) -> Completion:
        while True:
            completion: Completion
            async for delta in self.stream(messages, model=model):
                completion = delta.full

            # TODO: Implement tool calls

            messages.append(
                AssistantMessage(
                    content=completion.content,
                    backend_name=self.get_name(),
                    model_name=model,
                )
            )
            return completion

    async def stream(
        self, messages: list[Message], *, model: str
    ) -> AsyncIterator[CompletionDelta]:
        completion = Completion(content=[])
        async for contents in self._stream_deltas(messages, model=model):
            # Append to the previous content if it's the same type
            if completion.content and isinstance(
                completion.content[-1], type(contents[0])
            ):
                # TODO: Work out why isinstance is not sufficient
                completion.content[-1].append(contents[0])  # type: ignore[arg-type]
                # Add any additional content items
                completion.content.extend(contents[1:])
            else:
                # Otherwise, append the new content
                completion.content.extend(contents)

            yield CompletionDelta(full=completion, delta=contents)

    async def embed(self, input_text: str, *, model: str) -> Embedding:
        return Embedding(
            input_text=input_text, embedding=await self._embed(input_text, model=model)
        )

    async def _embed(self, input_text: str, *, model: str) -> list[float]:
        raise NotImplementedError("Embeddings are not supported for this engine")

    async def _stream_deltas(
        self, messages: list[Message], *, model: str
    ) -> AsyncIterator[list[Content]]:
        raise NotImplementedError
        yield []

    def get_name(self) -> str:
        raise NotImplementedError("Engine should provide a display name, e.g. 'OpenAI'")
