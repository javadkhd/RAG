from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Embedding
from app.providers.vectordb.base import VectorStore


class PgVectorStore:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, chunk_id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        embedding = Embedding(
            chunk_id=chunk_id,
            workspace_id=metadata["workspace_id"],
            dataset_id=metadata["dataset_id"],
            model=metadata.get("model", "unknown"),
            dimensions=len(vector),
            vector=vector,
        )
        self.session.add(embedding)
        await self.session.flush()

    async def search(self, vector: list[float], top_k: int = 10, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        from pgvector.sqlalchemy import Vector as PgVector

        query = select(
            Embedding.chunk_id,
            Embedding.workspace_id,
            Embedding.dataset_id,
            Embedding.model,
            Embedding.vector.cosine_distance(vector).label("distance"),
        )

        if filters:
            if "workspace_id" in filters:
                query = query.where(Embedding.workspace_id == filters["workspace_id"])
            if "dataset_id" in filters:
                query = query.where(Embedding.dataset_id == filters["dataset_id"])

        query = query.order_by("distance").limit(top_k)
        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "chunk_id": row.chunk_id,
                "workspace_id": row.workspace_id,
                "dataset_id": row.dataset_id,
                "model": row.model,
                "score": 1 - row.distance,
            }
            for row in rows
        ]

    async def delete(self, chunk_id: str) -> None:
        result = await self.session.execute(
            select(Embedding).where(Embedding.chunk_id == chunk_id)
        )
        embedding = result.scalar_one_or_none()
        if embedding:
            await self.session.delete(embedding)
            await self.session.flush()
