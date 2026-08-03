from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.deps import get_db
from app.providers.llm import get_llm_provider
from app.providers.embeddings import get_embedding_provider
from app.providers.vectordb.pgvector import PgVectorStore
from app.retrieval.retrievers.dense import DenseRetriever
from app.retrieval.retrievers.bm25 import BM25Retriever
from app.retrieval.retrievers.hybrid import HybridRetriever
from app.services.chat import ChatService


def _get_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client


def _build_chat_service(db_session):
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Mocked answer"

    mock_embedding = AsyncMock()
    mock_embedding.embed.return_value = [[0.1, 0.2]]

    mock_vector_store = AsyncMock()
    mock_vector_store.search.return_value = [
        {
            "chunk_id": str(uuid4()),
            "text": "Mocked context",
            "score": 0.9,
            "workspace_id": str(uuid4()),
            "dataset_id": str(uuid4()),
            "document_id": str(uuid4()),
        }
    ]

    dense = DenseRetriever(db_session, mock_embedding, mock_vector_store)
    bm25 = BM25Retriever(db_session)
    hybrid = HybridRetriever(dense, bm25)
    return ChatService(session=db_session, llm_provider=mock_llm, retriever=hybrid)


class TestChatAPI:
    @pytest.mark.asyncio
    async def test_chat_endpoint(self, db_session):
        from app.models.base import Workspace

        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()
        workspace_id = workspace.id

        client = _get_client(db_session)
        chat_service = _build_chat_service(db_session)

        def factory(db):
            return chat_service

        app.state.chat_service_factory = factory

        response = await client.post(
            "/chat",
            json={
                "workspace_id": str(workspace_id),
                "dataset_id": str(uuid4()),
                "message": "What is RAG?",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "conversation_id" in data
        assert "message_id" in data


class TestConversationsAPI:
    @pytest.mark.asyncio
    async def test_create_and_list_conversations(self, db_session):
        from app.models.base import Workspace

        client = _get_client(db_session)
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()
        workspace_id = str(workspace.id)

        response = await client.post(
            "/conversations",
            json={"workspace_id": workspace_id, "title": "Test Chat"},
        )
        assert response.status_code == 201
        conversation_id = response.json()["id"]

        response = await client.get(f"/conversations?workspace_id={workspace_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == conversation_id
