# Deployment Guide

## Prerequisites

- Docker 24+ (with BuildKit enabled)
- Docker Compose 2+
- NVIDIA GPU (optional, for Ollama acceleration)

## Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/rag-platform.git
cd rag-platform

# Configure environment
cp .env.example .env

# Build and start all services
docker compose up -d

# Run migrations
docker compose exec api alembic upgrade head

# Access API
curl http://localhost:8000/health
```

## Build Process

The project uses a single shared Dockerfile with build targets:

- `runtime-api` — API service (uvicorn)
- `runtime-worker` — Celery worker service

### Building Individual Services

```bash
# Build all services
docker compose build

# Build API only
docker compose build --target runtime-api api

# Build Worker only
docker compose build --target runtime-worker worker

# Rebuild with no cache
docker compose build --no-cache
```

### Build Caching

The Dockerfile uses BuildKit cache mounts for pip, which persist downloaded wheels between builds. This significantly reduces rebuild time when only application code changes.

## Environment Variables

The project uses two layers of environment configuration:

1. **`.env` file** — Local development defaults (loaded automatically by Docker Compose and the application)
2. **`docker-compose.yml`** — Docker network-specific values that override `.env` where needed

This separation ensures that:
- Local development uses `localhost` for services
- Docker containers use service hostnames (`postgres`, `redis`, `ollama`) for internal communication

### Application Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://rag:ragpass@localhost:5432/ragdb` (Docker) |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/2` |
| `LLM_PROVIDER` | LLM provider name | `ollama` |
| `LLM_MODEL` | LLM model name | `llama3` |
| `LLM_BASE_URL` | LLM API URL | `http://ollama:11434` |
| `LLM_API_KEY` | LLM API key (if required by provider) | *(empty)* |
| `EMBEDDING_PROVIDER` | Embedding provider | `bge_m3` |
| `EMBEDDING_MODEL_NAME` | Embedding model identifier | `BAAI/bge-m3` |
| `EMBEDDING_DEVICE` | Embedding compute device | `cpu` |
| `SECRET_KEY` | Application secret | Required in production |

### Infrastructure Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `rag` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `ragpass` |
| `POSTGRES_DB` | PostgreSQL database name | `ragdb` |
| `POSTGRES_PORT` | PostgreSQL host port | `5432` |
| `REDIS_PORT` | Redis host port | `6379` |
| `OLLAMA_PORT` | Ollama host port | `11434` |
| `API_PORT` | API host port | `8000` |

## Database Migrations

The project uses Alembic for database migrations with async SQLAlchemy support.

### Running Migrations in Docker

```bash
# Apply all pending migrations
docker compose exec api alembic upgrade head

# Generate a new migration (inside the api container)
docker compose exec api alembic -c config/alembic.ini revision --autogenerate -m "description"

# View migration history
docker compose exec api alembic history
```

### Running Migrations Locally

```bash
# Ensure .env has the correct DATABASE_URL (default: localhost)
# Apply all pending migrations
alembic -c config/alembic.ini upgrade head

# Generate a new migration
alembic -c config/alembic.ini revision --autogenerate -m "description"
```

### Migration Configuration

- **`config/alembic.ini`** — Alembic configuration (logging, script location)
- **`migrations/env.py`** — Migration environment (reads database URL from app settings)
- **`migrations/versions/`** — Migration scripts

The `env.py` reads the database URL from the application settings, ensuring consistent configuration across local development and Docker environments.

## Production Checklist

- [ ] Set `debug: false` in production config
- [ ] Use strong `SECRET_KEY`
- [ ] Configure PostgreSQL backups
- [ ] Enable Redis persistence
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation
- [ ] Enable SSL/TLS
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Use managed vector database for >1M vectors
- [ ] Pin Ollama image version for reproducibility
- [ ] Review resource limits for your workload

## Scaling

### Horizontal API Scaling
```bash
docker compose up -d --scale api=4
```

### Worker Scaling
```bash
docker compose up -d --scale worker=4
```

### Database Scaling
- Use read replicas for read-heavy workloads
- Consider connection pooling (PgBouncer)
- Monitor slow queries

### Vector Search Scaling
- Use pgvector extension with IVFFlat indexes
- Consider Qdrant/Milvus for >10M vectors
