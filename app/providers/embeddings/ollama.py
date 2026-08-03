import asyncio
from collections.abc import Sequence
from typing import Any

import httpx

from app.providers.embeddings.base import EmbeddingProvider


class OllamaEmbeddingProvider:
    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        async with httpx.AsyncClient() as client:
            tasks = [
                client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=60.0,
                )
                for text in texts
            ]
            responses = await asyncio.gather(*tasks)
            embeddings = []
            for response in responses:
                response.raise_for_status()
                data = response.json()
                embeddings.append(data["embedding"])
            return embeddings
