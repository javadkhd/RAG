from typing import Any

from app.retrieval.base import Retriever


class HybridRetriever:
    def __init__(self, dense: Retriever, bm25: Retriever, dense_weight: float = 0.6, bm25_weight: float = 0.4) -> None:
        self.dense = dense
        self.bm25 = bm25
        self.dense_weight = dense_weight
        self.bm25_weight = bm25_weight

    async def search(self, query: str, top_k: int = 10, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        dense_results = await self.dense.search(query, top_k=top_k * 2, filters=filters)
        bm25_results = await self.bm25.search(query, top_k=top_k * 2, filters=filters)

        dense_scores = {r["chunk_id"]: r["score"] for r in dense_results}
        bm25_scores = {r["chunk_id"]: r["score"] for r in bm25_results}
        chunk_data = {r["chunk_id"]: r for r in dense_results + bm25_results}

        all_chunk_ids = set(dense_scores) | set(bm25_scores)
        max_dense = max(dense_scores.values()) if dense_scores else 1.0
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0

        scored = []
        for chunk_id in all_chunk_ids:
            d_score = dense_scores.get(chunk_id, 0.0) / max_dense
            b_score = bm25_scores.get(chunk_id, 0.0) / max_bm25
            combined = self.dense_weight * d_score + self.bm25_weight * b_score
            entry = chunk_data[chunk_id]
            scored.append({**entry, "score": combined, "source": "hybrid"})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
