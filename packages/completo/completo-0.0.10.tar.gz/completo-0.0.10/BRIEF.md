Goal: provide the one true LLM abstraction library, with a common interface

Requirements:
-   Provides a backend-agnostic Python interface
-   Asynchronous-first, strongly-typed, with a sync interface
-   Supports streaming completions, via AsyncIterator
-   Supports tool-calling
-   Supports interfacing with the model context protocol
-   Uses vendor packages, like openai, anthropic, and google-generativeai
-   Enables replaying messages from one backend to another - e.g. switching
    backend mid-conversation
-   Integration with Instructor
-   Strong multi-modal support
    -   Not all backends need to support all modes. For example, audio inputs
        could be handled by Whisper, AssemblyAI.
-   Gracefully expose metadata like models available, and costings of prompts
-   Expose conversational information like tool-calls, reasoning completions

TODO:
-   [ ] Setup package
-   [ ] Provide two classes, one for async usage, the other for sync
-   [ ] Support openai and anthropic first
