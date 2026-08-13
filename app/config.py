import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import EMBEDDING_DIMENSIONS


def _load_yaml(filename: str) -> dict[str, Any]:
    config_path = Path(__file__).parent.parent / "config" / filename
    if not config_path.exists():
        return {}
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class DatabaseSettings(BaseModel):
    url: str = "postgresql+asyncpg://rag:ragpass@localhost:5432/ragdb"
    echo: bool = False
    hide_parameters: bool = True
    pool_size: int = 5
    max_overflow: int = 10


class RedisSettings(BaseModel):
    url: str = "redis://redis:6379/0"


class CelerySettings(BaseModel):
    broker_url: str = "redis://redis:6379/1"
    result_backend: str = "redis://redis:6379/2"


class LLMSettings(BaseModel):
    provider: str = "ollama"
    model: str = "qwen2.5:0.5b"
    base_url: str = "http://ollama:11434"
    api_key: str = ""
    temperature: float = 0.1
    max_tokens: int = 4096
    request_timeout: float = 120.0


class EmbeddingSettings(BaseModel):
    provider: str = "bge_m3"
    model_name: str = "BAAI/bge-m3"
    base_url: str = "http://localhost:11434"
    device: str = "cpu"
    normalize: bool = True
    dimensions: int = EMBEDDING_DIMENSIONS
    request_timeout: float = 60.0


class RetrievalSettings(BaseModel):
    dense_weight: float = 0.6
    bm25_weight: float = 0.4
    top_k: int = 10
    rerank_top_k: int = 5
    similarity_threshold: float = 0.7


class RerankerSettings(BaseModel):
    cross_encoder_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class IngestionSettings(BaseModel):
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_workers: int = 4
    default_doc_path: str = "data/docs"


class StorageSettings(BaseModel):
    upload_dir: str = "./storage/uploads"


class LoggingSettings(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class ApiSettings(BaseModel):
    cors_origins: list[str] = ["*"]
    rate_limit_max_requests: int = 100
    rate_limit_window_seconds: int = 60
    health_check_timeout: float = 2.0


class WorkerSettings(BaseModel):
    worker_prefetch_multiplier: int = 1
    task_time_limit: int = 30 * 60
    task_soft_time_limit: int = 29 * 60
    concurrency: int = 1
    loglevel: str = "info"


class AppSettings(BaseModel):
    name: str = "RAG Platform"
    version: str = "0.1.0"
    debug: bool = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app: AppSettings = Field(default_factory=AppSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    reranker: RerankerSettings = Field(default_factory=RerankerSettings)
    ingestion: IngestionSettings = Field(default_factory=IngestionSettings)
    worker: WorkerSettings = Field(default_factory=WorkerSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    @model_validator(mode="after")
    def _apply_env_overrides(self) -> "Settings":
        env_map = {
            "DATABASE_URL": ("database", "url"),
            "REDIS_URL": ("redis", "url"),
            "CELERY_BROKER_URL": ("celery", "broker_url"),
            "CELERY_RESULT_BACKEND": ("celery", "result_backend"),
            "LLM_PROVIDER": ("llm", "provider"),
            "LLM_MODEL": ("llm", "model"),
            "LLM_BASE_URL": ("llm", "base_url"),
            "LLM_API_KEY": ("llm", "api_key"),
            "LLM_REQUEST_TIMEOUT": ("llm", "request_timeout"),
            "EMBEDDING_PROVIDER": ("embedding", "provider"),
            "EMBEDDING_MODEL_NAME": ("embedding", "model_name"),
            "EMBEDDING_BASE_URL": ("embedding", "base_url"),
            "EMBEDDING_DEVICE": ("embedding", "device"),
            "EMBEDDING_REQUEST_TIMEOUT": ("embedding", "request_timeout"),
            "API_CORS_ORIGINS": ("api", "cors_origins"),
            "API_RATE_LIMIT_MAX_REQUESTS": ("api", "rate_limit_max_requests"),
            "API_RATE_LIMIT_WINDOW_SECONDS": ("api", "rate_limit_window_seconds"),
            "API_HEALTH_CHECK_TIMEOUT": ("api", "health_check_timeout"),
            "RERANKER_CROSS_ENCODER_MODEL_NAME": ("reranker", "cross_encoder_model_name"),
            "INGESTION_DEFAULT_DOC_PATH": ("ingestion", "default_doc_path"),
            "WORKER_PREFETCH_MULTIPLIER": ("worker", "worker_prefetch_multiplier"),
            "WORKER_TASK_TIME_LIMIT": ("worker", "task_time_limit"),
            "WORKER_TASK_SOFT_TIME_LIMIT": ("worker", "task_soft_time_limit"),
            "WORKER_CONCURRENCY": ("worker", "concurrency"),
            "WORKER_LOGLEVEL": ("worker", "loglevel"),
        }
        for env_key, (section, attr) in env_map.items():
            value = os.getenv(env_key)
            if value is not None:
                section_obj = getattr(self, section)
                if attr in ("cors_origins",):
                    setattr(section_obj, attr, [v.strip() for v in value.split(",")])
                else:
                    setattr(section_obj, attr, value)
        return self

    @classmethod
    def load(cls, env: str = "development") -> "Settings":
        yaml_data = _load_yaml(f"{env}.yaml")
        if not yaml_data:
            yaml_data = _load_yaml("development.yaml")

        settings = cls()
        if yaml_data:
            if "app" in yaml_data:
                settings.app = AppSettings(**yaml_data["app"])
            if "server" in yaml_data:
                settings.server = ServerSettings(**yaml_data["server"])
            if "api" in yaml_data:
                settings.api = ApiSettings(**yaml_data["api"])
            if "database" in yaml_data:
                settings.database = DatabaseSettings(**yaml_data["database"])
            if "redis" in yaml_data:
                settings.redis = RedisSettings(**yaml_data["redis"])
            if "celery" in yaml_data:
                settings.celery = CelerySettings(**yaml_data["celery"])
            if "llm" in yaml_data:
                settings.llm = LLMSettings(**yaml_data["llm"])
            if "embedding" in yaml_data:
                settings.embedding = EmbeddingSettings(**yaml_data["embedding"])
            if "retrieval" in yaml_data:
                settings.retrieval = RetrievalSettings(**yaml_data["retrieval"])
            if "reranker" in yaml_data:
                settings.reranker = RerankerSettings(**yaml_data["reranker"])
            if "ingestion" in yaml_data:
                settings.ingestion = IngestionSettings(**yaml_data["ingestion"])
            if "worker" in yaml_data:
                settings.worker = WorkerSettings(**yaml_data["worker"])
            if "storage" in yaml_data:
                settings.storage = StorageSettings(**yaml_data["storage"])
            if "logging" in yaml_data:
                settings.logging = LoggingSettings(**yaml_data["logging"])

        env_map = {
            "DATABASE_URL": ("database", "url"),
            "REDIS_URL": ("redis", "url"),
            "CELERY_BROKER_URL": ("celery", "broker_url"),
            "CELERY_RESULT_BACKEND": ("celery", "result_backend"),
            "LLM_PROVIDER": ("llm", "provider"),
            "LLM_MODEL": ("llm", "model"),
            "LLM_BASE_URL": ("llm", "base_url"),
            "LLM_API_KEY": ("llm", "api_key"),
            "LLM_REQUEST_TIMEOUT": ("llm", "request_timeout"),
            "EMBEDDING_PROVIDER": ("embedding", "provider"),
            "EMBEDDING_MODEL_NAME": ("embedding", "model_name"),
            "EMBEDDING_BASE_URL": ("embedding", "base_url"),
            "EMBEDDING_DEVICE": ("embedding", "device"),
            "EMBEDDING_REQUEST_TIMEOUT": ("embedding", "request_timeout"),
            "API_CORS_ORIGINS": ("api", "cors_origins"),
            "API_RATE_LIMIT_MAX_REQUESTS": ("api", "rate_limit_max_requests"),
            "API_RATE_LIMIT_WINDOW_SECONDS": ("api", "rate_limit_window_seconds"),
            "API_HEALTH_CHECK_TIMEOUT": ("api", "health_check_timeout"),
            "RERANKER_CROSS_ENCODER_MODEL_NAME": ("reranker", "cross_encoder_model_name"),
            "INGESTION_DEFAULT_DOC_PATH": ("ingestion", "default_doc_path"),
            "WORKER_PREFETCH_MULTIPLIER": ("worker", "worker_prefetch_multiplier"),
            "WORKER_TASK_TIME_LIMIT": ("worker", "task_time_limit"),
            "WORKER_TASK_SOFT_TIME_LIMIT": ("worker", "task_soft_time_limit"),
            "WORKER_CONCURRENCY": ("worker", "concurrency"),
            "WORKER_LOGLEVEL": ("worker", "loglevel"),
        }
        for env_key, (section, attr) in env_map.items():
            value = os.getenv(env_key)
            if value is not None:
                section_obj = getattr(settings, section)
                if attr in ("cors_origins",):
                    setattr(section_obj, attr, [v.strip() for v in value.split(",")])
                else:
                    setattr(section_obj, attr, value)

        return settings


settings = Settings.load()
