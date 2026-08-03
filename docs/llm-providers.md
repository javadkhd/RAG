# LLM Providers

## Provider Interface

All LLM providers implement the `LLMProvider` interface:

```python
class LLMProvider(Protocol):
    async def generate(self, prompt: str, **kwargs) -> str: ...
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]: ...
```

## Implemented Providers

### Ollama (Phase 1)
- Local and remote Ollama instances
- Supports any Ollama-compatible model
- Configuration:

```yaml
llm:
  provider: ollama
  model: llama3
  base_url: http://localhost:11434
  temperature: 0.1
  max_tokens: 4096
```

## Planned Providers

### OpenAI
```yaml
llm:
  provider: openai
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}
```

### Anthropic
```yaml
llm:
  provider: anthropic
  model: claude-3-5-sonnet-20241022
  api_key: ${ANTHROPIC_API_KEY}
```

### Gemini
```yaml
llm:
  provider: gemini
  model: gemini-pro
  api_key: ${GEMINI_API_KEY}
```

## Provider Selection

Providers are selected via configuration. The factory pattern resolves the correct implementation:

```python
def get_llm_provider(config: Settings) -> LLMProvider:
    if config.llm.provider == "ollama":
        return OllamaProvider(config.llm)
    elif config.llm.provider == "openai":
        return OpenAIProvider(config.llm)
    # ...
```
