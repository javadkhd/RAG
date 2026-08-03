# Deployment Guide

## Prerequisites

- Docker 24+
- Docker Compose 2+
- NVIDIA GPU (optional, for Ollama acceleration)

## Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/rag-platform.git
cd rag-platform

# Configure environment
cp .env.example .env

# Start all services
docker compose up -d

# Run migrations
docker compose exec api alembic upgrade head

# Access API
curl http://localhost:8000/health
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://rag:ragpass@localhost:5432/ragdb` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/2` |
| `LLM_PROVIDER` | LLM provider name | `ollama` |
| `LLM_MODEL` | LLM model name | `llama3` |
| `LLM_BASE_URL` | LLM API URL | `http://localhost:11434` |
| `EMBEDDING_PROVIDER` | Embedding provider | `bge_m3` |
| `SECRET_KEY` | Application secret | Required in production |

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
