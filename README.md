# RAG Platform

A production-ready modular RAG (Retrieval-Augmented Generation) Platform built with Python 3.11, FastAPI, Celery, PostgreSQL, and pgvector.

## Quick Start

### 1. Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, and Ollama via Docker Compose
docker compose up -d
```

### 2. Run Database Migrations

```bash
docker compose exec api alembic upgrade head
```

### 3. Add Markdown Documents

Place markdown files in the `data/docs/` directory:

```bash
data/
  docs/
    example.md
    subdirectory/
      another.md
```

### 4. Create a Workspace and Dataset

```bash
# Create workspace
curl -X POST http://localhost:8000/workspaces \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Knowledge base"}'

# Create dataset with markdown connector
curl -X POST http://localhost:8000/datasets \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace-id>",
    "name": "Documentation",
    "connector_type": "markdown",
    "connector_config": {"path": "data/docs"}
  }'
```

### 5. Trigger Ingestion

```bash
curl -X POST http://localhost:8000/datasets/<dataset-id>/ingest
```

### 6. Query the RAG

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "<workspace-id>",
    "dataset_id": "<dataset-id>",
    "message": "How do I configure payments?",
    "top_k": 5,
    "similarity_threshold": 0.7
  }'
```

## Architecture

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions.

## Documentation

- [Ingestion Pipeline](docs/ingestion.md)
- [Docker Infrastructure](docs/docker-review.md)
- [Deployment Guide](docs/deployment.md)
- [Architecture](docs/architecture.md)

## License

MIT
