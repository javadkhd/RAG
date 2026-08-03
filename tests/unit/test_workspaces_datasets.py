import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.main import app
from app.api.deps import get_db


class BaseTestClient:
    @pytest.fixture(autouse=True)
    def setup(self, db_engine):
        self.db_engine = db_engine
        self.session_factory = async_sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )
        self.client = self._build_client()

    def _build_client(self):
        async def override_get_db():
            async with self.session_factory() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)
        client = AsyncClient(transport=transport, base_url="http://test")
        return client


class TestWorkspaceEndpoints(BaseTestClient):
    async def test_create_workspace(self):
        response = await self.client.post(
            "/workspaces",
            json={
                "name": "Test Workspace",
                "description": "A test workspace",
                "extra_metadata": {"key": "value"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workspace"
        assert data["description"] == "A test workspace"
        assert data["extra_metadata"] == {"key": "value"}
        assert "id" in data
        assert "created_at" in data

    async def test_list_workspaces(self):
        await self.client.post("/workspaces", json={"name": "WS1"})
        await self.client.post("/workspaces", json={"name": "WS2"})

        response = await self.client.get("/workspaces")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [w["name"] for w in data]
        assert "WS1" in names
        assert "WS2" in names

    async def test_get_workspace(self):
        create_response = await self.client.post(
            "/workspaces", json={"name": "Get Test WS"}
        )
        workspace_id = create_response.json()["id"]

        response = await self.client.get(f"/workspaces/{workspace_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test WS"

    async def test_get_workspace_not_found(self):
        response = await self.client.get("/workspaces/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_update_workspace(self):
        create_response = await self.client.post(
            "/workspaces", json={"name": "Original Name"}
        )
        workspace_id = create_response.json()["id"]

        response = await self.client.patch(
            f"/workspaces/{workspace_id}",
            json={"name": "Updated Name", "description": "Updated desc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated desc"

    async def test_delete_workspace(self):
        create_response = await self.client.post(
            "/workspaces", json={"name": "To Delete"}
        )
        workspace_id = create_response.json()["id"]

        response = await self.client.delete(f"/workspaces/{workspace_id}")
        assert response.status_code == 204

        response = await self.client.get(f"/workspaces/{workspace_id}")
        assert response.status_code == 404

    async def test_delete_workspace_not_found(self):
        response = await self.client.delete(
            "/workspaces/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404


class TestDatasetEndpoints(BaseTestClient):
    async def _create_workspace(self):
        response = await self.client.post(
            "/workspaces", json={"name": "Dataset Test WS"}
        )
        return response.json()["id"]

    @pytest.fixture(autouse=True)
    async def setup(self, db_engine):
        self.db_engine = db_engine
        self.session_factory = async_sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )
        self.client = self._build_client()
        self.workspace_id = await self._create_workspace()

    async def test_create_dataset(self):
        response = await self.client.post(
            "/datasets",
            json={
                "workspace_id": self.workspace_id,
                "name": "Test Dataset",
                "connector_type": "markdown",
                "connector_config": {"path": "/data/test"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Dataset"
        assert data["connector_type"] == "markdown"
        assert data["workspace_id"] == self.workspace_id

    async def test_list_datasets(self):
        await self.client.post(
            "/datasets",
            json={
                "workspace_id": self.workspace_id,
                "name": "Dataset1",
            },
        )
        await self.client.post(
            "/datasets",
            json={
                "workspace_id": self.workspace_id,
                "name": "Dataset2",
            },
        )

        response = await self.client.get("/datasets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [d["name"] for d in data]
        assert "Dataset1" in names
        assert "Dataset2" in names

    async def test_list_datasets_by_workspace(self):
        await self.client.post(
            "/datasets",
            json={"workspace_id": self.workspace_id, "name": "WS Dataset"},
        )

        response = await self.client.get(
            "/datasets", params={"workspace_id": self.workspace_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "WS Dataset"

    async def test_get_dataset(self):
        create_response = await self.client.post(
            "/datasets",
            json={
                "workspace_id": self.workspace_id,
                "name": "Get Test Dataset",
            },
        )
        dataset_id = create_response.json()["id"]

        response = await self.client.get(f"/datasets/{dataset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test Dataset"

    async def test_get_dataset_not_found(self):
        response = await self.client.get("/datasets/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_update_dataset(self):
        create_response = await self.client.post(
            "/datasets",
            json={
                "workspace_id": self.workspace_id,
                "name": "Original Dataset",
            },
        )
        dataset_id = create_response.json()["id"]

        response = await self.client.patch(
            f"/datasets/{dataset_id}",
            json={"name": "Updated Dataset", "description": "New desc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Dataset"
        assert data["description"] == "New desc"

    async def test_delete_dataset(self):
        create_response = await self.client.post(
            "/datasets",
            json={
                "workspace_id": self.workspace_id,
                "name": "To Delete",
            },
        )
        dataset_id = create_response.json()["id"]

        response = await self.client.delete(f"/datasets/{dataset_id}")
        assert response.status_code == 204

        response = await self.client.get(f"/datasets/{dataset_id}")
        assert response.status_code == 404

    async def test_delete_dataset_not_found(self):
        response = await self.client.delete(
            "/datasets/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404
