from collections.abc import AsyncIterator
from typing import Any

from app.providers.llm.base import LLMProvider


class GeminiLLMProvider:
    def __init__(self, model: str, api_key: str, temperature: float = 0.1, max_tokens: int = 4096) -> None:
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, prompt: str, **kwargs) -> str:
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": kwargs.get("temperature", self.temperature),
                "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
            },
        )
        return response.text

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": kwargs.get("temperature", self.temperature),
                "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
            },
            stream=True,
        )
        for chunk in response:
            yield chunk.text
