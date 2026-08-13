import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.setrecursionlimit(200)

if "sentence_transformers" not in sys.modules:
    sys.modules["sentence_transformers"] = MagicMock()

from app.providers.embeddings.base import EmbeddingProvider  # noqa: E402
from app.providers.embeddings.bge import BgeEmbeddingProvider  # noqa: E402
from app.providers.embeddings.e5 import E5EmbeddingProvider  # noqa: E402
from app.providers.embeddings.nomic import NomicEmbeddingProvider  # noqa: E402
from app.providers.embeddings.ollama import OllamaEmbeddingProvider  # noqa: E402


class TestOllamaEmbeddingProvider:
    @pytest.mark.asyncio
    async def test_embed_single_text(self):
        provider = OllamaEmbeddingProvider(model="nomic-embed-text")

        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response

        with patch(
            "app.providers.embeddings.ollama.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await provider.embed(["hello world"])

        assert result == [[0.1, 0.2, 0.3]]
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self):
        provider = OllamaEmbeddingProvider(model="nomic-embed-text")

        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": [0.1, 0.2]}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response

        with patch(
            "app.providers.embeddings.ollama.httpx.AsyncClient",
            return_value=mock_client,
        ):
            result = await provider.embed(["text1", "text2"])

        assert len(result) == 2
        assert all(v == [0.1, 0.2] for v in result)
        assert mock_client.post.call_count == 2


class TestBgeEmbeddingProvider:
    @pytest.mark.asyncio
    async def test_embed(self):
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]

        with patch.object(
            sys.modules["sentence_transformers"],
            "SentenceTransformer",
            return_value=mock_model,
        ):
            provider = BgeEmbeddingProvider(
                model_name="BAAI/bge-m3", device="cpu", normalize=True
            )
            result = await provider.embed(["hello", "world"])

        assert result == [[0.1, 0.2], [0.3, 0.4]]
        mock_model.encode.assert_called_once_with(
            ["hello", "world"], normalize_embeddings=True
        )


class TestE5EmbeddingProvider:
    @pytest.mark.asyncio
    async def test_embed(self):
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.5, 0.6]]

        with patch.object(
            sys.modules["sentence_transformers"],
            "SentenceTransformer",
            return_value=mock_model,
        ):
            provider = E5EmbeddingProvider(
                model_name="intfloat/e5-large-v2", device="cpu", normalize=False
            )
            result = await provider.embed(["test"])

        assert result == [[0.5, 0.6]]
        mock_model.encode.assert_called_once_with(
            ["test"], normalize_embeddings=False
        )


class TestNomicEmbeddingProvider:
    @pytest.mark.asyncio
    async def test_embed(self):
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.7, 0.8]]

        with patch.object(
            sys.modules["sentence_transformers"],
            "SentenceTransformer",
            return_value=mock_model,
        ):
            provider = NomicEmbeddingProvider(
                model_name="nomic-ai/nomic-embed-text-v1.5",
                device="cpu",
                normalize=True,
            )
            result = await provider.embed(["query"])

        assert result == [[0.7, 0.8]]
        mock_model.encode.assert_called_once_with(
            ["query"], normalize_embeddings=True
        )


class TestEmbeddingProviderProtocol:
    def test_ollama_satisfies_protocol(self):
        provider = OllamaEmbeddingProvider(model="test")
        assert isinstance(provider, EmbeddingProvider)

    def test_bge_satisfies_protocol(self):
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1]]
        with patch.object(
            sys.modules["sentence_transformers"],
            "SentenceTransformer",
            return_value=mock_model,
        ):
            provider = BgeEmbeddingProvider()
        assert isinstance(provider, EmbeddingProvider)


class TestEmbeddingProviderLifecycle:
    def test_get_embedding_provider_caches_bge(self):
        import app.providers.embeddings as emb_module

        emb_module._cached_provider = None

        with patch.object(emb_module, "BgeEmbeddingProvider") as MockBge:
            MockBge.return_value = "cached_instance"
            first = emb_module.get_embedding_provider()
            second = emb_module.get_embedding_provider()
            assert first is second
            MockBge.assert_called_once()

    def test_get_embedding_provider_caches_ollama(self):
        import app.providers.embeddings as emb_module

        emb_module._cached_provider = None

        with patch.object(
            emb_module.settings.embedding, "provider", "ollama"
        ), patch.object(
            emb_module, "OllamaEmbeddingProvider"
        ) as MockOllama:
            MockOllama.return_value = "cached_ollama"
            first = emb_module.get_embedding_provider()
            second = emb_module.get_embedding_provider()
            assert first is second
            MockOllama.assert_called_once()
