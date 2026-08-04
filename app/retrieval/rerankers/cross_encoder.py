from typing import Any

from app.retrieval.base import Reranker


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            # from cross_encoder import CrossEncoder
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
        return self._model

    async def rerank(self, query: str, results: list[dict[str, Any]], top_k: int = 10) -> list[dict[str, Any]]:
        if not results:
            return []
        model = self._get_model()
        pairs = [(query, r["text"]) for r in results]
        scores = model.predict(pairs)
        for r, s in zip(results, scores):
            r["score"] = float(s)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
