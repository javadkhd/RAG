from app.config import (
    ApiSettings,
    DatabaseSettings,
    EmbeddingSettings,
    LLMSettings,
    RedisSettings,
    Settings,
    WorkerSettings,
)


def test_settings_load_development(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings.load("development")
    assert settings.app.name == "RAG Platform"
    assert settings.server.port == 8000


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
    settings = Settings.load("development")
    assert "testdb" in settings.database.url


def test_database_settings_defaults():
    db = DatabaseSettings()
    assert db.url == "postgresql+asyncpg://rag:ragpass@localhost:5432/ragdb"
    assert db.echo is False
    assert db.hide_parameters is True
    assert db.pool_size == 5


def test_redis_settings_defaults():
    redis = RedisSettings()
    assert redis.url == "redis://redis:6379/0"


def test_api_settings_defaults():
    api = ApiSettings()
    assert api.cors_origins == ["*"]
    assert api.rate_limit_max_requests == 100
    assert api.rate_limit_window_seconds == 60
    assert api.health_check_timeout == 2.0


def test_llm_settings_defaults():
    llm = LLMSettings()
    assert llm.provider == "ollama"
    assert llm.request_timeout == 120.0


def test_embedding_settings_defaults():
    emb = EmbeddingSettings()
    assert emb.provider == "bge_m3"
    assert emb.request_timeout == 60.0


def test_worker_settings_defaults():
    worker = WorkerSettings()
    assert worker.worker_prefetch_multiplier == 1
    assert worker.task_time_limit == 1800
    assert worker.task_soft_time_limit == 1740
    assert worker.concurrency == 1
    assert worker.loglevel == "info"
