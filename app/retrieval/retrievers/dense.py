from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Chunk
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.vectordb.base import VectorStore
from app.retrieval.base import Retriever


class DenseRetriever:
    def __init__(
        self,
        session: AsyncSession,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def search(self, query: str, top_k: int = 10, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        query_vector = (await self.embedding_provider.embed([query]))[0]
        vector_results = await self.vector_store.search(query_vector, top_k=top_k * 2, filters=filters)

        chunk_ids = [r["chunk_id"] for r in vector_results]
        if not chunk_ids:
            return []

        result = await self.session.execute(
            select(Chunk.id, Chunk.text, Chunk.workspace_id, Chunk.dataset_id, Chunk.document_id)
            .where(Chunk.id.in_(chunk_ids))
        )
        chunk_map = {str(row[0]): {"text": row[1], "workspace_id": row[2], "dataset_id": row[3], "document_id": row[4]} for row in result.all()}

        results = []
        for r in vector_results:
            chunk_id = r["chunk_id"]
            if chunk_id in chunk_map:
                results.append({
                    "chunk_id": chunk_id,
                    "text": chunk_map[chunk_id]["text"],
                    "score": r["score"],
                    "workspace_id": chunk_map[chunk_id]["workspace_id"],
                    "dataset_id": chunk_map[chunk_id]["dataset_id"],
                    "document_id": chunk_map[chunk_id]["document_id"],
                    "source": "dense",
                })
        return results[:top_k]
