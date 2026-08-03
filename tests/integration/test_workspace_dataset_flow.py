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


class TestIntegrationWorkspaceDataset:
    @pytest.mark.asyncio
    async def test_create_workspace_and_dataset(self, db_session):
        client = _get_client(db_session)
        ws_resp = await client.post("/workspaces", json={"name": "Integration WS"})
        assert ws_resp.status_code == 201
        workspace_id = ws_resp.json()["id"]

        ds_resp = await client.post("/datasets", json={"workspace_id": workspace_id, "name": "Integration DS"})
        assert ds_resp.status_code == 201
        dataset_id = ds_resp.json()["id"]

        list_resp = await client.get(f"/datasets?workspace_id={workspace_id}")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1
        assert list_resp.json()[0]["id"] == dataset_id
