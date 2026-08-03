from collections.abc import AsyncIterator
from typing import Any

from app.providers.llm.base import LLMProvider


class AnthropicLLMProvider:
    def __init__(self, model: str, api_key: str, temperature: float = 0.1, max_tokens: int = 4096) -> None:
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, prompt: str, **kwargs) -> str:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=self.api_key)
        response = await client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=self.api_key)
        with client.messages.stream(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
