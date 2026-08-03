from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from rank_bm25 import BM25Okapi

from app.models.base import Chunk
from app.retrieval.base import Retriever


class BM25Retriever:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._bm25: BM25Okapi | None = None
        self._chunk_ids: list[str] = []
        self._chunk_map: dict[str, dict[str, Any]] = {}

    async def _index(self, workspace_id: str | None = None, dataset_id: str | None = None) -> None:
        query = select(Chunk.id, Chunk.text, Chunk.workspace_id, Chunk.dataset_id, Chunk.document_id)
        if workspace_id:
            query = query.where(Chunk.workspace_id == workspace_id)
        if dataset_id:
            query = query.where(Chunk.dataset_id == dataset_id)

        result = await self.session.execute(query)
        rows = result.all()
        if not rows:
            self._bm25 = None
            self._chunk_ids = []
            self._chunk_map = {}
            return

        self._chunk_ids = [str(row[0]) for row in rows]
        self._chunk_map = {str(row[0]): {"text": row[1], "workspace_id": str(row[2]), "dataset_id": str(row[3]), "document_id": str(row[4])} for row in rows}
        tokenized = [row[1].split() for row in rows]
        self._bm25 = BM25Okapi(tokenized)

    async def search(self, query: str, top_k: int = 10, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        workspace_id = filters.get("workspace_id") if filters else None
        dataset_id = filters.get("dataset_id") if filters else None

        await self._index(workspace_id=workspace_id, dataset_id=dataset_id)
        if not self._bm25:
            return []

        tokenized_query = query.split()
        scores = self._bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            chunk_id = self._chunk_ids[idx]
            results.append({
                "chunk_id": chunk_id,
                "text": self._chunk_map[chunk_id]["text"],
                "score": float(scores[idx]),
                "workspace_id": self._chunk_map[chunk_id]["workspace_id"],
                "dataset_id": self._chunk_map[chunk_id]["dataset_id"],
                "document_id": self._chunk_map[chunk_id]["document_id"],
                "source": "bm25",
            })
        return results
