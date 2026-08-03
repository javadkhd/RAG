from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.providers.vectordb.base import VectorStore
from app.providers.vectordb.pgvector import PgVectorStore


class TestPgVectorStore:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_add(self, mock_session):
        store = PgVectorStore(session=mock_session)
        await store.add(
            chunk_id="chunk-1",
            vector=[0.1, 0.2, 0.3],
            metadata={"workspace_id": "ws-1", "dataset_id": "ds-1", "model": "test"},
        )
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_search(self, mock_session):
        mock_row = MagicMock()
        mock_row.chunk_id = "chunk-1"
        mock_row.workspace_id = "ws-1"
        mock_row.dataset_id = "ds-1"
        mock_row.model = "test"
        mock_row.distance = 0.1

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        store = PgVectorStore(session=mock_session)
        results = await store.search([0.1, 0.2, 0.3], top_k=5)

        assert len(results) == 1
        assert results[0]["chunk_id"] == "chunk-1"
        assert results[0]["score"] == 0.9
        assert results[0]["model"] == "test"

    @pytest.mark.asyncio
    async def test_search_with_filters(self, mock_session):
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        store = PgVectorStore(session=mock_session)
        await store.search(
            [0.1, 0.2, 0.3],
            top_k=5,
            filters={"workspace_id": "ws-1", "dataset_id": "ds-1"},
        )

        query = str(mock_session.execute.call_args[0][0])
        assert "workspace_id" in query
        assert "dataset_id" in query

    @pytest.mark.asyncio
    async def test_delete(self, mock_session):
        mock_embedding = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_embedding
        mock_session.execute.return_value = mock_result

        store = PgVectorStore(session=mock_session)
        await store.delete("chunk-1")

        mock_session.delete.assert_called_once_with(mock_embedding)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        store = PgVectorStore(session=mock_session)
        await store.delete("nonexistent")

        mock_session.delete.assert_not_called()


class TestVectorStoreProtocol:
    def test_pgvector_satisfies_protocol(self):
        mock_session = AsyncMock()
        store = PgVectorStore(session=mock_session)
        assert isinstance(store, VectorStore)
