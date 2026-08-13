from app.config import DatabaseSettings, RedisSettings, Settings


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
