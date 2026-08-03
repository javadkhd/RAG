from app.config import settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.anthropic import AnthropicLLMProvider
from app.providers.llm.gemini import GeminiLLMProvider
from app.providers.llm.openai import OpenAILLMProvider
from app.providers.llm.ollama import OllamaLLMProvider


def get_llm_provider() -> LLMProvider:
    provider = settings.llm.provider
    if provider == "ollama":
        return OllamaLLMProvider(
            model=settings.llm.model,
            base_url=settings.llm.base_url,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
        )
    elif provider == "openai":
        return OpenAILLMProvider(
            model=settings.llm.model,
            api_key=settings.llm.api_key,
            base_url=settings.llm.base_url,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
        )
    elif provider == "anthropic":
        return AnthropicLLMProvider(
            model=settings.llm.model,
            api_key=settings.llm.api_key,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
        )
    elif provider == "gemini":
        return GeminiLLMProvider(
            model=settings.llm.model,
            api_key=settings.llm.api_key,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
        )
    raise ValueError(f"Unknown LLM provider: {provider}")
