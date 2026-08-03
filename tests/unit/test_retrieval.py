from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.retrieval.base import Reranker, Retriever
from app.retrieval.filters.metadata import apply_filters
from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.rerankers.cross_encoder import CrossEncoderReranker
from app.retrieval.retrievers.bm25 import BM25Retriever
from app.retrieval.retrievers.dense import DenseRetriever
from app.retrieval.retrievers.hybrid import HybridRetriever


class TestDenseRetriever:
    @pytest.mark.asyncio
    async def test_search(self):
        mock_session = AsyncMock()
        mock_embedding_provider = AsyncMock()
        mock_embedding_provider.embed.return_value = [[0.1, 0.2]]
        mock_vector_store = AsyncMock()
        mock_vector_store.search.return_value = [
            {"chunk_id": "chunk-1", "score": 0.9, "workspace_id": "ws-1", "dataset_id": "ds-1"}
        ]

        mock_result = MagicMock()
        mock_result.all.return_value = [("chunk-1", "text content", "ws-1", "ds-1", "doc-1")]
        mock_session.execute.return_value = mock_result

        retriever = DenseRetriever(mock_session, mock_embedding_provider, mock_vector_store)
        results = await retriever.search("test query", top_k=5)

        assert len(results) == 1
        assert results[0]["chunk_id"] == "chunk-1"
        assert results[0]["text"] == "text content"
        assert results[0]["source"] == "dense"
        mock_embedding_provider.embed.assert_called_once_with(["test query"])
        mock_vector_store.search.assert_called_once()


class TestBM25Retriever:
    @pytest.mark.asyncio
    async def test_search(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("chunk-1", "hello world", "ws-1", "ds-1", "doc-1"),
            ("chunk-2", "hello there", "ws-1", "ds-1", "doc-2"),
        ]
        mock_session.execute.return_value = mock_result

        retriever = BM25Retriever(mock_session)
        results = await retriever.search("hello", top_k=5)

        assert len(results) > 0
        assert all("score" in r for r in results)
        assert all(r["source"] == "bm25" for r in results)

    @pytest.mark.asyncio
    async def test_search_empty(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        retriever = BM25Retriever(mock_session)
        results = await retriever.search("hello", top_k=5)
        assert results == []


class TestHybridRetriever:
    @pytest.mark.asyncio
    async def test_search(self):
        mock_dense = AsyncMock(spec=Retriever)
        mock_dense.search.return_value = [
            {"chunk_id": "c1", "text": "dense text", "score": 0.9, "workspace_id": "ws-1", "dataset_id": "ds-1", "document_id": "doc-1"}
        ]
        mock_bm25 = AsyncMock(spec=Retriever)
        mock_bm25.search.return_value = [
            {"chunk_id": "c2", "text": "bm25 text", "score": 5.0, "workspace_id": "ws-1", "dataset_id": "ds-1", "document_id": "doc-2"}
        ]

        retriever = HybridRetriever(mock_dense, mock_bm25, dense_weight=0.6, bm25_weight=0.4)
        results = await retriever.search("test", top_k=5)

        assert len(results) == 2
        assert all(r["source"] == "hybrid" for r in results)
        assert results[0]["score"] != results[1]["score"]


class TestCrossEncoderReranker:
    @pytest.mark.asyncio
    async def test_rerank(self):
        import sys
        from unittest.mock import MagicMock

        mock_model = MagicMock()
        mock_model.predict.return_value = [0.3, 0.9]

        if "cross_encoder" not in sys.modules:
            sys.modules["cross_encoder"] = MagicMock()

        with patch.object(sys.modules["cross_encoder"], "CrossEncoder", return_value=mock_model):
            reranker = CrossEncoderReranker(model_name="test-model")
            results = await reranker.rerank("query", [
                {"chunk_id": "c1", "text": "low relevance"},
                {"chunk_id": "c2", "text": "high relevance"},
            ], top_k=1)

        assert len(results) == 1
        assert results[0]["chunk_id"] == "c2"
        assert results[0]["score"] == 0.9


class TestMetadataFilters:
    def test_apply_filters_no_filters(self):
        query = MagicMock()
        filtered = apply_filters(query)
        assert filtered is query

    def test_apply_filters_with_workspace_id(self):
        from app.models.base import Chunk
        from sqlalchemy import select

        query = select(Chunk)
        filtered = apply_filters(query, filters={"workspace_id": "ws-1"})
        assert filtered is not query


class TestRetrievalPipeline:
    @pytest.mark.asyncio
    async def test_retrieve_without_reranker(self):
        mock_retriever = AsyncMock(spec=Retriever)
        mock_retriever.search.return_value = [
            {"chunk_id": "c1", "text": "text", "score": 0.8},
        ]

        pipeline = RetrievalPipeline(mock_retriever, top_k=5, similarity_threshold=0.5)
        results = await pipeline.retrieve("query")

        assert len(results) == 1
        mock_retriever.search.assert_called_once_with("query", top_k=5, filters=None)

    @pytest.mark.asyncio
    async def test_retrieve_with_reranker(self):
        mock_retriever = AsyncMock(spec=Retriever)
        mock_retriever.search.return_value = [
            {"chunk_id": "c1", "text": "text", "score": 0.8},
            {"chunk_id": "c2", "text": "text2", "score": 0.7},
        ]
        mock_reranker = AsyncMock(spec=Reranker)
        mock_reranker.rerank.return_value = [{"chunk_id": "c2", "text": "text2", "score": 0.9}]

        pipeline = RetrievalPipeline(mock_retriever, reranker=mock_reranker, top_k=10, rerank_top_k=1)
        results = await pipeline.retrieve("query")

        assert len(results) == 1
        mock_reranker.rerank.assert_called_once()

    @pytest.mark.asyncio
    async def test_similarity_threshold(self):
        mock_retriever = AsyncMock(spec=Retriever)
        mock_retriever.search.return_value = [
            {"chunk_id": "c1", "text": "text", "score": 0.5},
            {"chunk_id": "c2", "text": "text2", "score": 0.9},
        ]

        pipeline = RetrievalPipeline(mock_retriever, top_k=10, similarity_threshold=0.7)
        results = await pipeline.retrieve("query")

        assert len(results) == 1
        assert results[0]["chunk_id"] == "c2"
