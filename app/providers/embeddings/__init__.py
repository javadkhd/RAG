import logging

from app.config import settings
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.embeddings.bge import BgeEmbeddingProvider
from app.providers.embeddings.e5 import E5EmbeddingProvider
from app.providers.embeddings.nomic import NomicEmbeddingProvider
from app.providers.embeddings.ollama import OllamaEmbeddingProvider

logger = logging.getLogger(__name__)

_cached_provider: EmbeddingProvider | None = None


def get_embedding_provider() -> EmbeddingProvider:
    global _cached_provider
    if _cached_provider is None:
        provider = settings.embedding.provider
        if provider == "ollama":
            _cached_provider = OllamaEmbeddingProvider(
                model=settings.embedding.model_name,
                base_url=settings.llm.base_url,
            )
        elif provider == "bge_m3":
            _cached_provider = BgeEmbeddingProvider(
                model_name=settings.embedding.model_name,
                device=settings.embedding.device,
                normalize=settings.embedding.normalize,
            )
            logger.info("Loading embedding model %s", settings.embedding.model_name)
        elif provider == "e5":
            _cached_provider = E5EmbeddingProvider(
                model_name=settings.embedding.model_name,
                device=settings.embedding.device,
                normalize=settings.embedding.normalize,
            )
            logger.info("Loading embedding model %s", settings.embedding.model_name)
        elif provider == "nomic":
            _cached_provider = NomicEmbeddingProvider(
                model_name=settings.embedding.model_name,
                device=settings.embedding.device,
                normalize=settings.embedding.normalize,
            )
            logger.info("Loading embedding model %s", settings.embedding.model_name)
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")
    return _cached_provider
