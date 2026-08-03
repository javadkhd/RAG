from collections.abc import Sequence
from typing import Any

from app.providers.embeddings.base import EmbeddingProvider


class E5EmbeddingProvider:
    def __init__(self, model_name: str = "intfloat/e5-large-v2", device: str = "cpu", normalize: bool = True) -> None:
        self.model_name = model_name
        self.device = device
        self.normalize = normalize
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        model = self._get_model()
        embeddings = model.encode(list(texts), normalize_embeddings=self.normalize)
        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()
        return list(embeddings)
