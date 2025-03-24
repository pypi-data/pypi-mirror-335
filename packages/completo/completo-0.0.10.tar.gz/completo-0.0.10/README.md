<p align="center">
  <img src="https://github.com/rmasters/completo/blob/main/docs/logo.png?raw=true" alt="The Great Completo">
</p>
<p align="center">
  <strong>Completo</strong> provides a unified interface for interacting with LLMs.
</p>

## Work in progress

Completo is currently in active development. Current features include:
* [x] Synchronous and asynchronous interfaces 
* [x] Switch engines mid-conversation
* [x] Streaming responses
* [x] Pydantic models
* [ ] Tool use
* [ ] Model Context Protocol servers for tools
* [ ] Instructor integration
* Backend support:
  * [x] OpenAI
  * [x] Anthropic
  * [ ] Gemini
  * [ ] Ollama

## Installation

Use the [completo](https://pypi.org/project/completo/) package.

Currently targeting Python 3.13 only.

## Usage

### Simple interface

```python
from completo import Completo

llm = Completo(default_engine=SyncOpenAIEngine(), default_model="o3-mini")

response = str(llm.complete("Hello, world!"))  # => "Hey, how can I help you today?"
```

### Conversational interface

```python
from completo import Completo, Conversation, UserMessage, DeveloperMessage, AssistantMessage

llm = Completo(default_engine=SyncOpenAIEngine(), default_model="o3-mini")

convo = Conversation()
convo.messages.append(DeveloperMessage(content="Respond in a single word"))  # Short-hand text content
convo.messages.append(UserMessage(content=[TextContent(text="What is the capital of France?")]))  # Fully-formed content

response = llm.complete(convo)

assert response.content[0].text == str(response) == "Paris"
assert isinstance(convo.messages[0], DeveloperMessage)
assert isinstance(convo.messages[1], UserMessage)
assert isinstance(convo.messages[2], AssistantMessage)
```

### Async interfaces

```python
from completo import AsyncCompleto

llm = AsyncCompleto(default_engine=AsyncAnthropicEngine(), default_model="claude-3-5-sonnet-latest")

response = await llm.complete("Hello, world!")
```

### Streaming

```python
from completo import Completo
from completo.models.completions import CompletionDelta

llm = Completo(default_engine=SyncOpenAIEngine(), default_model="o3-mini")

response = llm.complete("Hello, world!")

for completion in response.stream():
    assert isinstance(completion, CompletionDelta)
    print(completion.content[0].text)
    # => "Hey"
    # => ", "
    # => "how"
    # => " can I"
    # => "help"
    # => " you"
    # => "today?"
```

#### Async streaming

```python
from completo import AsyncCompleto

llm = AsyncCompleto(default_engine=AsyncOpenAIEngine(), default_model="o3-mini")

response = await llm.complete("Hello, world!")

for completion in response.stream():
    assert isinstance(completion, CompletionDelta)
    print(completion.content[0].text)
    # => "Hey"
    # => ", "
    # => "how"
    # => " can I"
    # => "help"
    # => " you"
    # => "today?"
```

### Switching engines

```python
from completo import Completo

openai = SyncOpenAIEngine()
anthropic = SyncAnthropicEngine()

llm = Completo(default_engine=openai, default_model="o3-mini")

response = llm.complete("Which model are you executing on?")
print(response.content[0].text)  # => "o3-mini"

response = llm.complete("Which model are you executing on?", engine=anthropic, model="claude-3-5-sonnet-latest")
print(response.content[0].text)  # => "claude-3-5-sonnet-latest"
```
