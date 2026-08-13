from collections.abc import AsyncIterator

import httpx

from app.config import settings


class OllamaLLMProvider:
    def __init__(
        self,
        model: str,
        base_url: str = "",
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> None:
        self.model = model
        self.base_url = (base_url or settings.llm.base_url).rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, prompt: str, **kwargs) -> str:
        async with httpx.AsyncClient(timeout=settings.llm.request_timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", self.temperature),
                        "num_predict": kwargs.get("max_tokens", self.max_tokens),
                    },
                },
                timeout=settings.llm.request_timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=settings.llm.request_timeout) as client:
            async with (
                client.stream(
                    "post",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": kwargs.get("temperature", self.temperature),
                            "num_predict": kwargs.get("max_tokens", self.max_tokens),
                        },
                    },
                    timeout=settings.llm.request_timeout,
                ) as response
            ):
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
