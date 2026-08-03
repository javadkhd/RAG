from app.config import settings
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.embeddings.bge import BgeEmbeddingProvider
from app.providers.embeddings.e5 import E5EmbeddingProvider
from app.providers.embeddings.nomic import NomicEmbeddingProvider
from app.providers.embeddings.ollama import OllamaEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.embedding.provider
    if provider == "ollama":
        return OllamaEmbeddingProvider(
            model=settings.embedding.model_name,
            base_url=settings.llm.base_url,
        )
    elif provider == "bge_m3":
        return BgeEmbeddingProvider(
            model_name=settings.embedding.model_name,
            device=settings.embedding.device,
            normalize=settings.embedding.normalize,
        )
    elif provider == "e5":
        return E5EmbeddingProvider(
            model_name=settings.embedding.model_name,
            device=settings.embedding.device,
            normalize=settings.embedding.normalize,
        )
    elif provider == "nomic":
        return NomicEmbeddingProvider(
            model_name=settings.embedding.model_name,
            device=settings.embedding.device,
            normalize=settings.embedding.normalize,
        )
    raise ValueError(f"Unknown embedding provider: {provider}")
