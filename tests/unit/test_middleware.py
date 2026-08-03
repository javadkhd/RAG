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


class TestMiddleware:
    @pytest.mark.asyncio
    async def test_request_id_middleware(self, db_session):
        client = _get_client(db_session)
        response = await client.get("/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    @pytest.mark.asyncio
    async def test_security_headers_middleware(self, db_session):
        client = _get_client(db_session)
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers

    @pytest.mark.asyncio
    async def test_rate_limit_middleware(self, db_session):
        from fastapi import FastAPI
        from starlette.middleware.base import BaseHTTPMiddleware

        from app.api.middleware import RateLimitMiddleware

        test_app = FastAPI()

        class _CaptureMiddleware(RateLimitMiddleware):
            async def dispatch(self, request, call_next):
                response = await super().dispatch(request, call_next)
                self.last_response = response
                return response

        test_app.add_middleware(_CaptureMiddleware, max_requests=5, window_seconds=60)

        @test_app.get("/health")
        async def health():
            return {"status": "ok"}

        async def override_get_db():
            yield db_session

        test_app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=test_app)
        client = AsyncClient(transport=transport, base_url="http://test")

        for _ in range(5):
            response = await client.get("/health")
            assert response.status_code == 200

        response = await client.get("/health")
        assert response.status_code == 429
        assert response.json()["detail"] == "Rate limit exceeded. Please try again later."

    @pytest.mark.asyncio
    async def test_error_handling_middleware(self, db_session):
        client = _get_client(db_session)
        response = await client.get("/nonexistent")
        assert response.status_code == 404
