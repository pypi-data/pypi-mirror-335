import pytest

from completo.backends.anthropic.engine import AsyncAnthropicEngine
from completo.backends.engine import AsyncEngine
from completo.backends.openai.engine import AsyncOpenAIEngine
from completo.interfaces import AsyncCompleto
from completo.models.completions import Completion, CompletionDelta
from completo.models.content import TextContent
from completo.models.embeddings import Embedding
from completo.models.messages import Conversation, DeveloperMessage, UserMessage


def openai_async_engine() -> AsyncOpenAIEngine:
    return AsyncOpenAIEngine()


def anthropic_async_engine() -> AsyncAnthropicEngine:
    return AsyncAnthropicEngine()


@pytest.mark.parametrize(
    ["engine", "model"],
    [
        (openai_async_engine(), "gpt-4o-mini"),
        (anthropic_async_engine(), "claude-3-5-sonnet-latest"),
    ],
)
async def test_completion_from_empty_conversation(engine: AsyncEngine, model: str):
    llm = AsyncCompleto(
        default_engine=engine,
        default_completions_model=model,
    )

    completion = await llm.complete(
        Conversation(
            messages=[
                DeveloperMessage(
                    content=[
                        TextContent(
                            text="Only respond with 'Hello, world!'",
                        ),
                    ],
                ),
                UserMessage(
                    content=[
                        TextContent(
                            text="Hey",
                        ),
                    ],
                ),
            ]
        )
    )

    assert isinstance(completion, Completion)
    assert len(completion.content) == 1
    assert isinstance(completion.content[0], TextContent)
    assert completion.content[0].text == "Hello, world!"


@pytest.mark.parametrize(
    ["engine", "model", "expected_deltas"],
    [
        (
            openai_async_engine(),
            "gpt-4o-mini",
            [
                "Hello",
                ",",
                " world",
                "!",
            ],
        ),
        (anthropic_async_engine(), "claude-3-5-sonnet-latest", ["Hello, world!"]),
    ],
)
async def test_stream_completion_delta_from_empty_conversation(
    engine: AsyncEngine, model: str, expected_deltas: list[str]
):
    llm = AsyncCompleto(
        default_engine=engine,
        default_completions_model=model,
    )

    i = 0
    async for completion in llm.stream(
        Conversation(
            messages=[
                DeveloperMessage(
                    content=[TextContent(text="Only respond with 'Hello, world!'")]
                ),
                UserMessage(content=[TextContent(text="Hey")]),
            ]
        ),
    ):
        expected_delta = expected_deltas[i]
        expected_completion = "".join(expected_deltas[: i + 1])
        print(i, completion, expected_delta, expected_completion)

        assert len(completion.delta) == 1
        assert isinstance(completion.delta[0], TextContent)
        assert completion.delta[0].text == expected_delta

        assert isinstance(completion, CompletionDelta)
        assert len(completion.full.content) == 1
        assert isinstance(completion.full.content[0], TextContent)
        assert completion.full.content[0].text == expected_completion

        i += 1


@pytest.mark.parametrize(
    ["engine", "model"],
    [
        (openai_async_engine(), "text-embedding-3-small"),
    ],
)
async def test_generate_embeddings(engine: AsyncEngine, model: str):
    llm = AsyncCompleto(
        default_engine=engine,
        default_embeddings_model=model,
    )

    embedding = await llm.embed("Hello, world!")

    assert isinstance(embedding, Embedding)
    assert embedding.input_text == "Hello, world!"
    assert isinstance(embedding.embedding, list)
    assert all(isinstance(value, float) for value in embedding.embedding)
    assert len(embedding.embedding) > 0
