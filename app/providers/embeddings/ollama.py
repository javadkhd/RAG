import asyncio
from collections.abc import Sequence

import httpx

from app.config import settings


class OllamaEmbeddingProvider:
    def __init__(self, model: str, base_url: str = "") -> None:
        self.model = model
        self.base_url = (base_url or settings.embedding.base_url).rstrip("/")

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=settings.embedding.request_timeout) as client:
            tasks = [
                client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=settings.embedding.request_timeout,
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
