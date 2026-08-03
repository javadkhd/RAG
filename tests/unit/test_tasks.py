from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.deps import get_db


def _get_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client


class TestTasksAPI:
    @pytest.mark.asyncio
    async def test_create_and_list_tasks(self, db_session):
        from app.models.base import Workspace

        client = _get_client(db_session)
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()
        workspace_id = str(workspace.id)

        response = await client.post(
            "/tasks",
            json={
                "workspace_id": workspace_id,
                "title": "Test Task",
                "description": "Test description",
                "status": "pending",
                "priority": "high",
            },
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        response = await client.get(f"/tasks?workspace_id={workspace_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == task_id

    @pytest.mark.asyncio
    async def test_update_task(self, db_session):
        from app.models.base import Workspace

        client = _get_client(db_session)
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()
        workspace_id = str(workspace.id)

        response = await client.post(
            "/tasks",
            json={
                "workspace_id": workspace_id,
                "title": "Original Task",
                "status": "pending",
            },
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        response = await client.patch(
            f"/tasks/{task_id}",
            json={"status": "completed", "priority": "low"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["priority"] == "low"

    @pytest.mark.asyncio
    async def test_delete_task(self, db_session):
        from app.models.base import Workspace

        client = _get_client(db_session)
        workspace = Workspace(name="Test WS")
        db_session.add(workspace)
        await db_session.flush()
        workspace_id = str(workspace.id)

        response = await client.post(
            "/tasks",
            json={
                "workspace_id": workspace_id,
                "title": "Task to delete",
            },
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        response = await client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204

        response = await client.get(f"/tasks/{task_id}")
        assert response.status_code == 404
