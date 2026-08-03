from typing import Any

from app.ingestion.indexer import Indexer


class Embedder:
    def __init__(self, provider) -> None:
        self.provider = provider

    async def embed_chunks(self, chunks: list[Any]) -> None:
        texts = [chunk.text for chunk in chunks]
        vectors = await self.provider.embed(texts)
        for chunk, vector in zip(chunks, vectors):
            chunk.embedding = vector
