# Ingestion Pipeline Audit Report

## Current State

The project has a partially implemented ingestion pipeline with scaffolding in place but several critical gaps. Below is the analysis.

## Existing Components (Working)

### Connectors
- `app/connectors/base.py` — `BaseConnector` ABC defining `load()` interface
- `app/connectors/markdown/loader.py` — `MarkdownConnector` that recursively scans `*.md` files, parses YAML frontmatter, extracts metadata (path, directory, size, frontmatter, filename, source)
- `app/connectors/postgres/` — `PostgresConnector` and `PostgresInspector` (working)

### Ingestion Core
- `app/ingestion/cleaner.py` — `clean()` normalizes whitespace and line endings
- `app/ingestion/splitter.py` — `split()` chunks text by token count with overlap
- `app/ingestion/indexer.py` — `Indexer` creates `Document`, `Chunk`, `Embedding` ORM objects and stores them
- `app/ingestion/pipeline.py` — `IngestionPipeline` orchestrates: load → index → count
- `app/ingestion/embedder.py` — `Embedder` wrapper (exists but unused)

### Providers
- `app/providers/embeddings/` — `EmbeddingProvider` Protocol + implementations (ollama, bge_m3, e5, nomic)
- `app/providers/vectordb/pgvector.py` — `PgVectorStore` for similarity search

### API
- CRUD routers for workspaces, datasets, tasks, conversations, chat
- `app/api/deps.py` — `get_db`, `get_dataset_or_404`, `get_workspace_or_404`

### Models
- `app/models/base.py` — All models: Workspace, Dataset, Document, Chunk, Embedding, Conversation, Message, Task

### Database
- `app/db/session.py` — Async engine factory with pool config
- `migrations/env.py` — Async migration support (but flawed)

## Issues Found

### 1. Circular Import in `app/worker/celery_app.py` (Critical)
```python
from app.worker.celery_app import celery_app
```
Imports from itself, causing `ImportError` when Celery starts.

### 2. Placeholder Celery Tasks (Critical)
`app/worker/tasks.py` tasks just return `{"status": "queued"}` — no actual ingestion logic.

### 3. Missing Ingestion API Endpoint (Critical)
`app/api/routers/ingestion.py` is empty. No `POST /datasets/{dataset_id}/ingest` endpoint.

### 4. Ingestion Router Not Registered (Critical)
`app/main.py` does not import or register the ingestion router.

### 5. Hardcoded Database URL in `config/alembic.ini` (Critical for Docker)
`sqlalchemy.url = postgresql+asyncpg://rag:ragpass@localhost:5432/ragdb` — inside Docker, `localhost` refers to the container itself, not PostgreSQL.

### 6. `migrations/env.py` Doesn't Use App Settings (High)
Does not import or use `app.config.settings` to resolve the database URL dynamically. Contains 45 lines of commented-out sync code.

### 7. IngestionPipeline Issues (High)
- Does not call `cleaner.clean()` before splitting — relies on splitter's internal call
- Uses hardcoded `chunk_size=512, overlap=50` in indexer instead of reading from `settings`
- Counts chunks by calling `split()` a second time instead of tracking actual created chunks
- `embedder` parameter in pipeline constructor is unused — indexer creates its own provider

### 8. Indexer Uses Hardcoded Model Name (Medium)
`Embedding` model field set to `"placeholder"` instead of the actual embedding model name from settings.

### 9. No Connector Factory (Medium)
No mechanism to instantiate the correct connector based on `connector_type` string from a Dataset.

### 10. Empty Files (Low)
- `app/worker/ingestion.py` — empty
- `app/worker/embeddings.py` — empty
- `app/connectors/markdown/parser.py` — empty
- `app/connectors/markdown/__init__.py` — empty
- `app/ingestion/metadata.py` — empty
- `app/ingestion/__init__.py` — empty
- `app/repositories/document.py`, `chunk.py`, `embedding.py` — empty
- `app/services/document.py`, `ingestion.py` — empty

## Required Changes

| # | File | Action | Priority |
|---|---|---|---|
| 1 | `app/worker/celery_app.py` | Fix circular import: `from app.worker import celery_app` | Critical |
| 2 | `app/worker/tasks.py` | Implement `ingest_dataset` with real async DB + pipeline logic | Critical |
| 3 | `app/worker/ingestion.py` | Implement ingestion orchestration logic | Critical |
| 4 | `app/api/routers/ingestion.py` | Implement `POST /datasets/{dataset_id}/ingest` endpoint | Critical |
| 5 | `app/main.py` | Register ingestion router | Critical |
| 6 | `migrations/env.py` | Use app settings for DB URL, remove commented code | Critical |
| 7 | `config/alembic.ini` | Remove hardcoded URL | High |
| 8 | `app/ingestion/pipeline.py` | Use settings, cleaner, accurate result tracking | High |
| 9 | `app/ingestion/indexer.py` | Use model name from settings | Medium |
| 10 | `app/ingestion/indexer.py` | Use settings for chunk_size/overlap | High |
| 11 | `data/` directory | Create with example markdown | Medium |
| 12 | `docker-compose.yml` | Add `./data:/app/data` volume mount | Medium |
| 13 | `.env.example` | Add `LLM_API_KEY` | Done |
| 14 | `docs/ingestion.md` | Update with data flow and configuration | Medium |
| 15 | `docs/deployment.md` | Update with migration instructions | Done |

## Implementation Plan

### Phase 1: Fix Critical Infrastructure (Tasks 1, 6, 7)
- Fix circular import in celery_app.py
- Update env.py to use app settings
- Remove hardcoded URL from alembic.ini

### Phase 2: Implement Worker Logic (Tasks 2, 3, 9)
- Implement worker/ingestion.py with dataset loading, connector creation, pipeline execution
- Implement ingest_dataset Celery task with proper DB session management
- Fix indexer to use settings for model name and chunk config

### Phase 3: Implement API (Tasks 4, 5)
- Implement ingestion router with POST endpoint
- Register router in main.py

### Phase 4: Fix Pipeline (Task 8)
- Use settings for chunk_size/overlap
- Call cleaner before splitting
- Track actual chunks and embeddings

### Phase 5: Data Directory & Docker (Tasks 11, 12)
- Create data/docs/example.md
- Add volume mount to docker-compose.yml

### Phase 6: Documentation & Tests (Tasks 14, 16)
- Update docs/ingestion.md
- Add tests for new components

### Phase 7: Validation
- Run lint, typecheck, tests