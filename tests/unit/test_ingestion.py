import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.connectors.markdown.loader import MarkdownConnector
from app.ingestion.cleaner import clean
from app.ingestion.pipeline import IngestionPipeline, IngestionResult
from app.ingestion.splitter import split


def _get_client(db_session):
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from app.api.deps import get_db
    from app.main import app

    sf = async_sessionmaker(db_session.bind, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with sf() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestMarkdownConnector:
    @pytest.fixture
    def tmp_data_dir(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "doc1.md").write_text(
                "# Hello World\n\nThis is content.",
                encoding="utf-8",
            )
            (root / "sub").mkdir()
            (root / "sub" / "doc2.md").write_text(
                "---\ntitle: Test Doc\nslug: test-doc\n---\nFrontmatter body",
                encoding="utf-8",
            )
            (root / "deep" / "nested" / "doc3.md").mkdir(parents=True)
            (root / "deep" / "nested" / "doc3.md").write_text(
                "# Deep Nested\n\nContent here.\n",
                encoding="utf-8",
            )
            yield root

    @pytest.mark.asyncio
    async def test_load_finds_all_markdown_files(self, tmp_data_dir):
        connector = MarkdownConnector()
        docs = await connector.load(
            str(tmp_data_dir),
            dataset_id="00000000-0000-0000-0000-000000000000",
            workspace_id="00000000-0000-0000-0000-000000000000",
        )
        assert len(docs) == 3
        filenames = {d["filename"] for d in docs}
        assert filenames == {"doc1.md", "doc2.md", "doc3.md"}

    @pytest.mark.asyncio
    async def test_load_extracts_metadata(self, tmp_data_dir):
        connector = MarkdownConnector()
        docs = await connector.load(
            str(tmp_data_dir),
            dataset_id="00000000-0000-0000-0000-000000000000",
            workspace_id="00000000-0000-0000-0000-000000000000",
        )

        for doc in docs:
            assert "path" in doc["metadata"]
            assert "directory" in doc["metadata"]
            assert "size_bytes" in doc["metadata"]
            assert doc["metadata"]["size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_frontmatter_parsing(self, tmp_data_dir):
        connector = MarkdownConnector()
        docs = await connector.load(
            str(tmp_data_dir),
            dataset_id="00000000-0000-0000-0000-000000000000",
            workspace_id="00000000-0000-0000-0000-000000000000",
        )
        doc2 = next(d for d in docs if d["filename"] == "doc2.md")
        assert doc2["metadata"]["frontmatter"] == {"title": "Test Doc", "slug": "test-doc"}

    @pytest.mark.asyncio
    async def test_no_frontmatter(self, tmp_data_dir):
        connector = MarkdownConnector()
        docs = await connector.load(
            str(tmp_data_dir),
            dataset_id="00000000-0000-0000-0000-000000000000",
            workspace_id="00000000-0000-0000-0000-000000000000",
        )
        doc1 = next(d for d in docs if d["filename"] == "doc1.md")
        assert "frontmatter" not in doc1["metadata"]

    @pytest.mark.asyncio
    async def test_missing_path_raises_error(self):
        connector = MarkdownConnector()
        with pytest.raises(FileNotFoundError):
            await connector.load(
                "/nonexistent/path",
                dataset_id="00000000-0000-0000-0000-000000000000",
                workspace_id="00000000-0000-0000-0000-000000000000",
            )

    @pytest.mark.asyncio
    async def test_dataset_workspace_passed_through(self, tmp_data_dir):
        connector = MarkdownConnector()
        ds_id = "11111111-0000-0000-0000-000000000000"
        ws_id = "22222222-0000-0000-0000-000000000000"
        docs = await connector.load(str(tmp_data_dir), dataset_id=ds_id, workspace_id=ws_id)
        for doc in docs:
            assert doc["dataset_id"] == ds_id
            assert doc["workspace_id"] == ws_id


class TestCleaner:
    def test_clean_normalizes_whitespace(self):
        assert clean("Hello   world\n\n\n\nFoo") == "Hello world\n\nFoo"

    def test_clean_carriage_returns(self):
        assert clean("Hello\r\nworld") == "Hello\nworld"

    def test_clean_empty(self):
        assert clean("") == ""

    def test_clean_strips_leading_trailing(self):
        assert clean("  hello  ") == "hello"


class TestSplitter:
    def test_split_basic(self):
        text = " ".join(str(i) for i in range(20))
        chunks = split(text, chunk_size=5, overlap=2)
        assert len(chunks) > 1

    def test_split_empty(self):
        assert split("", chunk_size=512, overlap=50) == []

    def test_split_short_text(self):
        assert split("hello world", chunk_size=100, overlap=10) == ["hello world"]

    def test_split_overlap(self):
        text = "word " * 20
        chunks = split(text.strip(), chunk_size=5, overlap=2)
        assert len(chunks) > 1
        assert chunks[0] != chunks[1]

    def test_split_calls_cleaner(self):
        text = "Hello   world  \n\n\n  Foo"
        chunks = split(text, chunk_size=100, overlap=0)
        assert chunks == ["Hello world\n\nFoo"]


class TestIngestionPipeline:
    @pytest.mark.asyncio
    async def test_pipeline_no_embedder(self):
        mock_connector = MagicMock()
        mock_connector.load = AsyncMock(
            return_value=[
                {
                    "text": "This is test document content for chunking.",
                    "source": "/fake/path/doc1.md",
                    "filename": "doc1.md",
                    "metadata": {"path": "doc1.md"},
                    "dataset_id": "00000000-0000-0000-0000-000000000000",
                    "workspace_id": "00000000-0000-0000-0000-000000000000",
                },
            ]
        )
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.commit = AsyncMock()

        pipeline = IngestionPipeline(session=mock_session, connector=mock_connector, embedder=None)
        result = await pipeline.run(
            path="/fake/path",
            dataset_id=uuid4(),
            workspace_id=uuid4(),
        )

        assert isinstance(result, IngestionResult)
        assert result.documents_loaded == 1
        assert result.chunks_created > 0
        assert result.embeddings_generated == 0

    @pytest.mark.asyncio
    async def test_pipeline_with_embedder(self):
        from app.providers.embeddings.base import EmbeddingProvider

        mock_provider = MagicMock(spec=EmbeddingProvider)
        mock_provider.embed = AsyncMock(return_value=[[0.1, 0.2, 0.3]])

        mock_connector = MagicMock()
        mock_connector.load = AsyncMock(
            return_value=[
                {
                    "text": "Test document about machine learning.",
                    "source": "/fake/path.md",
                    "filename": "doc.md",
                    "metadata": {"path": "doc.md"},
                    "dataset_id": "00000000-0000-0000-0000-000000000000",
                    "workspace_id": "00000000-0000-0000-0000-000000000000",
                },
            ]
        )

        mock_session = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.commit = AsyncMock()

        pipeline = IngestionPipeline(
            session=mock_session,
            connector=mock_connector,
            embedder=mock_provider,
        )

        result = await pipeline.run(
            path="/fake/path",
            dataset_id=uuid4(),
            workspace_id=uuid4(),
        )

        assert result.documents_loaded == 1
        assert result.chunks_created > 0
        assert result.embeddings_generated == result.chunks_created
        assert mock_provider.embed.called


class TestIngestionAPI:
    @pytest.mark.asyncio
    async def test_ingest_dataset_endpoint(self, db_session):
        from app.models.base import Dataset, Workspace

        client = _get_client(db_session)
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()

        dataset = Dataset(
            workspace_id=workspace.id,
            name="Test Dataset",
            connector_type="markdown",
            connector_config={"path": "data/docs"},
        )
        db_session.add(dataset)
        await db_session.flush()
        dataset_id = str(dataset.id)

        with patch("app.api.routers.ingestion.ingest_dataset_task") as mock_task:
            mock_task.delay.return_value = MagicMock(id="celery-task-id-123")
            response = await client.post(f"/datasets/{dataset_id}/ingest")

            assert response.status_code == 202
            data = response.json()
            assert data["dataset_id"] == dataset_id
            assert data["task_id"] == "celery-task-id-123"
            assert data["status"] == "queued"

        await client.aclose()

    @pytest.mark.asyncio
    async def test_ingest_dataset_not_found(self, db_session):
        client = _get_client(db_session)
        response = await client.post(f"/datasets/{uuid4()}/ingest")
        assert response.status_code == 404
        await client.aclose()

    @pytest.mark.asyncio
    async def test_ingest_dataset_no_connector_type(self, db_session):
        from app.models.base import Dataset, Workspace

        client = _get_client(db_session)
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()

        dataset = Dataset(
            workspace_id=workspace.id,
            name="No Connector",
            connector_type=None,
        )
        db_session.add(dataset)
        await db_session.flush()
        dataset_id = str(dataset.id)

        response = await client.post(f"/datasets/{dataset_id}/ingest")
        assert response.status_code == 400
        await client.aclose()


class TestCeleryTask:
    def test_task_is_registered(self):
        from app.worker.tasks import ingest_dataset

        assert ingest_dataset.name == "app.worker.tasks.ingest_dataset"

    def test_task_return_format(self):
        from app.worker.tasks import ingest_dataset

        assert ingest_dataset.__name__ == "ingest_dataset"
