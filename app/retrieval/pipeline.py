from typing import Any

from app.retrieval.base import Reranker, Retriever
from app.retrieval.filters.metadata import apply_filters


class RetrievalPipeline:
    def __init__(
        self,
        retriever: Retriever,
        reranker: Reranker | None = None,
        top_k: int = 10,
        rerank_top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> None:
        self.retriever = retriever
        self.reranker = reranker
        self.top_k = top_k
        self.rerank_top_k = rerank_top_k
        self.similarity_threshold = similarity_threshold

    async def retrieve(self, query: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        results = await self.retriever.search(query, top_k=self.top_k, filters=filters)
        results = [r for r in results if r["score"] >= self.similarity_threshold]
        if self.reranker and results:
            results = await self.reranker.rerank(query, results, top_k=self.rerank_top_k)
        return results[:self.rerank_top_k if self.reranker else self.top_k]
