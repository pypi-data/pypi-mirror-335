import json
from pathlib import Path
from typing import Annotated

from anthropic import AsyncAnthropic
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import AsyncOpenAI
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from completo.backends.anthropic.engine import AsyncAnthropicEngine
from completo.backends.openai.engine import AsyncOpenAIEngine
from completo.interfaces import AsyncCompleto
from completo.models.messages import (
    AssistantMessage,
    Conversation,
    ToolResultMessage,
    UserMessage,
)
from completo.models.tools import ToolCall, ToolCallResult
from completo.shortcuts import text


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_api_key: SecretStr
    anthropic_api_key: SecretStr


app = FastAPI(
    title="Completo Demo",
    description="A demonstration of the Completo package",
)

app_root = Path(__file__).parent

tpl = Jinja2Templates(directory=str(app_root / "templates"))


Scalar = int | float | str | bool | None
Jsonable = Scalar | dict | list


def pydantic_json(value: BaseModel | Jsonable, _as_json: bool = True) -> str | Jsonable:
    if isinstance(value, BaseModel):
        return value.model_dump_json() if _as_json else value.model_dump()

    if isinstance(value, dict):
        dict_data = {k: pydantic_json(v, False) for k, v in value.items()}
        return json.dumps(dict_data) if _as_json else dict_data

    if isinstance(value, list):
        list_data = [pydantic_json(v, False) for v in value]
        return json.dumps(list_data) if _as_json else list_data

    return json.dumps(value) if _as_json else value


tpl.env.filters["json"] = pydantic_json

app.mount("/static", StaticFiles(directory=app_root / "static"), name="static")

settings = Settings()  # type: ignore[call-arg]

completo = AsyncCompleto(
    default_engine=AsyncOpenAIEngine(
        AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value()),
    ),
    default_completions_model="gpt-4o-mini",
)

# TODO: Get backends from the engine
backends = {
    "openai": AsyncOpenAIEngine(
        AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value()),
    ),
    "anthropic": AsyncAnthropicEngine(
        AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value()),
    ),
}


@app.get("/")
async def chat(request: Request):
    return tpl.TemplateResponse(request, "index.html")


class Payload(BaseModel):
    conversation: Conversation
    new_message: str
    backend: str
    model: str


@app.get("/messages")
async def conversation(request: Request):
    convo = Conversation(
        messages=[
            UserMessage(content=[text("What time is it?")]),
            AssistantMessage(
                backend_name="OpenAI",
                model_name="gpt-4o-mini",
                content=[],
                tool_calls=[
                    (
                        tool_call := ToolCall(
                            id="tool-call-0001",
                            function="get_time_in_timezone",
                            arguments={"timezone": "Europe/London"},
                        )
                    ),
                ],
            ),
            ToolResultMessage(
                content=[],
                tool_call=ToolCallResult(
                    tool_call=tool_call,
                    content="The time in London is 10:00 AM.",
                    is_error=False,
                ),
            ),
            AssistantMessage(
                content=[text("It is currently 10:00 AM in London.")],
                backend_name="openai",
                model_name="gpt-4o-mini",
            ),
        ]
    )
    return tpl.TemplateResponse(
        request,
        "partials/chat.html",
        {
            "backends": {name: engine.get_name() for name, engine in backends.items()},
            "conversation": convo,
        },
    )


@app.post("/messages")
async def complete(request: Request, payload: Payload):
    await completo.complete(payload.conversation)

    return tpl.TemplateResponse(
        request,
        "partials/chat.html",
        {
            "backends": {name: engine.get_name() for name, engine in backends.items()},
            "conversation": payload.conversation,
        },
    )


@app.get("/models")
async def backend_models(request: Request, backend: Annotated[str, Query()]):
    # TODO: Get models from the engine
    # backends[backend].get_models()
    if backend == "openai":
        models = [
            "gpt-4o-mini",
            "gpt-4o",
        ]
    elif backend == "anthropic":
        models = [
            "claude-3-5-sonnet-latest",
            "claude-3-haiku-latest",
        ]
    else:
        models = []

    return tpl.TemplateResponse(
        request,
        "partials/chat-model-options.html",
        {
            "models": models,
        },
    )
