import uuid

import pytest

from app.models.base import Workspace, Dataset, Document, Chunk


class TestWorkspaceModel:
    @pytest.mark.asyncio
    async def test_create_workspace(self, db_session):
        workspace = Workspace(
            name="Test Workspace",
            description="A test workspace",
        )
        db_session.add(workspace)
        await db_session.commit()
        await db_session.refresh(workspace)

        assert workspace.id is not None
        assert workspace.name == "Test Workspace"
        assert workspace.description == "A test workspace"

    @pytest.mark.asyncio
    async def test_workspace_metadata(self, db_session):
        workspace = Workspace(
            name="Test Workspace",
            extra_metadata={"key": "value"},
        )
        db_session.add(workspace)
        await db_session.commit()
        await db_session.refresh(workspace)

        assert workspace.extra_metadata == {"key": "value"}


class TestDatasetModel:
    @pytest.mark.asyncio
    async def test_create_dataset(self, db_session):
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()

        dataset = Dataset(
            workspace_id=workspace.id,
            name="Test Dataset",
            connector_type="markdown",
        )
        db_session.add(dataset)
        await db_session.commit()
        await db_session.refresh(dataset)

        assert dataset.id is not None
        assert dataset.workspace_id == workspace.id
        assert dataset.name == "Test Dataset"
        assert dataset.connector_type == "markdown"


class TestDocumentModel:
    @pytest.mark.asyncio
    async def test_create_document(self, db_session):
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()

        dataset = Dataset(workspace_id=workspace.id, name="Test DS")
        db_session.add(dataset)
        await db_session.flush()

        document = Document(
            workspace_id=workspace.id,
            dataset_id=dataset.id,
            source="/path/to/file.md",
            filename="file.md",
            content_type="text/markdown",
            size_bytes=1024,
        )
        db_session.add(document)
        await db_session.commit()
        await db_session.refresh(document)

        assert document.id is not None
        assert document.status == "pending"
        assert document.source == "/path/to/file.md"


class TestChunkModel:
    @pytest.mark.asyncio
    async def test_create_chunk(self, db_session):
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()

        dataset = Dataset(workspace_id=workspace.id, name="Test DS")
        db_session.add(dataset)
        await db_session.flush()

        document = Document(
            workspace_id=workspace.id,
            dataset_id=dataset.id,
            source="/path/to/file.md",
        )
        db_session.add(document)
        await db_session.flush()

        chunk = Chunk(
            workspace_id=workspace.id,
            dataset_id=dataset.id,
            document_id=document.id,
            chunk_index=0,
            text="This is a test chunk.",
            token_count=5,
        )
        db_session.add(chunk)
        await db_session.commit()
        await db_session.refresh(chunk)

        assert chunk.id is not None
        assert chunk.chunk_index == 0
        assert chunk.text == "This is a test chunk."
        assert chunk.token_count == 5
