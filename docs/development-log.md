# Development Log

## Phase 8: LLM Provider Interface and Ollama Implementation

**Date:** 2026-08-03

### Completed Tasks
- [x] Defined `LLMProvider` protocol in `app/providers/llm/base.py`
- [x] Implemented `OllamaLLMProvider` using `httpx` async client with streaming support
- [x] Implemented `OpenAILLMProvider` using official `openai` SDK
- [x] Implemented `AnthropicLLMProvider` using official `anthropic` SDK
- [x] Implemented `GeminiLLMProvider` using `google.generativeai` SDK
- [x] Created factory function `get_llm_provider()` in `app/providers/llm/__init__.py`
- [x] Added `api_key` field to `LLMSettings` in `app/config.py`
- [x] Added `LLM_API_KEY` environment variable mapping
- [x] All 71 unit tests pass

### Created Files

**Providers:**
- `app/providers/llm/__init__.py` - Factory function `get_llm_provider()`
- `app/providers/llm/base.py` - `LLMProvider` protocol with `generate` and `generate_stream`
- `app/providers/llm/ollama.py` - `OllamaLLMProvider` with async HTTP and streaming
- `app/providers/llm/openai.py` - `OpenAILLMProvider` using AsyncOpenAI
- `app/providers/llm/anthropic.py` - `AnthropicLLMProvider` using AsyncAnthropic
- `app/providers/llm/gemini.py` - `GeminiLLMProvider` using google.generativeai

**Tests:**
- `tests/unit/test_llm_providers.py` - 9 tests covering all providers, protocol conformance, and factory

### Design Decisions
1. **Protocol-based interface**: `LLMProvider` uses `@runtime_checkable` Protocol with `generate` and `generate_stream`
2. **Ollama via HTTP**: Uses `httpx.AsyncClient` for both sync and streaming generation
3. **Official SDKs**: OpenAI, Anthropic, and Gemini use their official async SDKs
4. **Factory pattern**: `get_llm_provider()` resolves provider from `settings.llm.provider`
5. **Config extension**: Added `api_key` to `LLMSettings` with `LLM_API_KEY` env override
6. **Streaming support**: All providers implement `generate_stream` for real-time token delivery

### Tests Performed
- [x] All 71 unit tests pass (9 new LLM tests + 62 existing)
- [x] Ollama generate and streaming with mocked httpx
- [x] OpenAI generate with mocked AsyncOpenAI
- [x] Anthropic generate with mocked AsyncAnthropic
- [x] Gemini generate with mocked google.generativeai
- [x] Protocol conformance checks for all providers
- [x] Factory function with valid and unknown providers

---

## Phase 9: Chat API with RAG Pipeline

**Date:** 2026-08-03

### Completed Tasks
- [x] Created `ChatService` in `app/services/chat.py` with full RAG pipeline integration
- [x] Implemented chat endpoint `POST /chat` with `workspace_id`, `dataset_id`, and `message`
- [x] Implemented conversation management endpoints in `app/api/routers/conversations.py`
- [x] Added `chat_service_factory` to `app/main.py` for dependency injection via `app.state`
- [x] Created request/response schemas in `app/api/schemas/chat.py`
- [x] Integrated `RetrievalPipeline` with LLM provider for context-aware generation
- [x] All 73 unit tests pass (2 new chat tests + 71 existing)

### Created Files

**Service:**
- `app/services/chat.py` - `ChatService` with RAG pipeline, conversation management, and prompt building

**API Routers:**
- `app/api/routers/chat.py` - `POST /chat` endpoint
- `app/api/routers/conversations.py` - `GET/POST /conversations`, `GET /conversations/{id}/messages`

**Schemas:**
- `app/api/schemas/chat.py` - `ChatRequest`, `ChatResponse`, `ConversationCreate`, `ConversationResponse`, `MessageResponse`

**Tests:**
- `tests/unit/test_chat.py` - 2 async tests covering chat endpoint and conversation CRUD

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Send message to RAG system |
| GET | `/conversations` | List conversations in workspace |
| POST | `/conversations` | Create new conversation |
| GET | `/conversations/{id}` | Get conversation details |
| GET | `/conversations/{id}/messages` | Get conversation messages |

### Design Decisions
1. **Service-layer chat logic**: `ChatService` owns conversation creation, retrieval, and LLM generation
2. **RAG pipeline integration**: Uses existing `RetrievalPipeline` with hybrid retrieval and optional reranking
3. **Factory via app.state**: `chat_service_factory` on `app.state` avoids FastAPI dependency issues with complex initialization
4. **Context building**: Retrieved chunks are formatted into numbered context for LLM prompt
5. **Source tracking**: Assistant messages store source chunks in `sources` JSON field
6. **Conversation scoping**: Conversations are workspace-scoped via foreign key

### Tests Performed
- [x] All 73 unit tests pass (2 new chat tests + 71 existing)
- [x] Chat endpoint returns answer, conversation_id, and message_id
- [x] Conversation creation and listing by workspace_id
- [x] Foreign key integrity enforced in tests

---

## Phase 10: Memory System (Conversation + Task)

**Date:** 2026-08-03

### Completed Tasks
- [x] Created `TaskRepository` in `app/repositories/task.py`
- [x] Created `TaskService` in `app/services/task.py`
- [x] Implemented task API endpoints in `app/api/routers/tasks.py`
- [x] Created task schemas in `app/api/schemas/task.py`
- [x] Registered tasks router in `app/main.py`
- [x] All 76 unit tests pass (3 new task tests + 73 existing)

### Created Files

**Repository:**
- `app/repositories/task.py` - `TaskRepository` with CRUD and count operations

**Service:**
- `app/services/task.py` - `TaskService` with workspace-scoped listing

**API Router:**
- `app/api/routers/tasks.py` - `POST/GET/PATCH/DELETE /tasks` with optional `workspace_id` filter

**Schemas:**
- `app/api/schemas/task.py` - `TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskList`

**Tests:**
- `tests/unit/test_tasks.py` - 3 async tests covering task CRUD operations

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tasks` | Create task |
| GET | `/tasks` | List tasks in workspace |
| GET | `/tasks/{task_id}` | Get task by ID |
| PATCH | `/tasks/{task_id}` | Update task |
| DELETE | `/tasks/{task_id}` | Delete task |

### Design Decisions
1. **Repository pattern**: Task DB access follows existing repository pattern
2. **Service layer**: Thin `TaskService` wraps repository for business logic extension
3. **Workspace scoping**: Tasks are workspace-scoped via foreign key with list filter
4. **Status/Priority defaults**: Tasks default to `pending`/`medium` status

### Tests Performed
- [x] All 76 unit tests pass (3 new task tests + 73 existing)
- [x] Task creation with workspace association
- [x] Task listing filtered by workspace_id
- [x] Task update (status, priority)
- [x] Task deletion and 404 handling

---

## Phase 11: Agent Layer

**Date:** 2026-08-03

### Completed Tasks
- [x] Defined `BaseTool` protocol in `app/tools/base.py`
- [x] Implemented `FilesystemTool`, `ShellTool`, `SearchTool`, `GitTool`, `PostgresTool`
- [x] Created `AgentContext` for workspace-scoped execution context
- [x] Created `AgentMemory` for conversation and retrieval history
- [x] Created `AgentPlanner` for LLM-based step planning
- [x] Created `AgentExecutor` for step execution (retrieve, tool, generate)
- [x] Created `AgentOrchestrator` as main entry point
- [x] All 87 unit tests pass (11 new agent tests + 76 existing)

### Created Files

**Tools:**
- `app/tools/base.py` - `BaseTool` protocol
- `app/tools/filesystem.py` - Filesystem operations
- `app/tools/shell.py` - Safe shell commands
- `app/tools/search.py` - Web search via Google Custom Search
- `app/tools/git.py` - Git operations
- `app/tools/postgres.py` - Read-only SQL queries

**Agent:**
- `app/agent/context.py` - `AgentContext` data class
- `app/agent/memory.py` - `AgentMemory` for history tracking
- `app/agent/planner.py` - `AgentPlanner` with LLM-based planning
- `app/agent/executor.py` - `AgentExecutor` for step execution
- `app/agent/orchestrator.py` - `AgentOrchestrator` main entry point
- `app/agent/prompts.py` - Prompt templates for planning and generation

**Tests:**
- `tests/unit/test_agent.py` - 11 tests covering tools, memory, planner, executor, orchestrator

### Design Decisions
1. **Protocol-based tools**: `BaseTool` protocol with `name`, `description`, `async run()`
2. **LLM-driven planning**: Planner uses LLM to generate JSON step plans
3. **Step types**: retrieve, tool, generate
4. **Memory integration**: Executor records retrieved chunks and tool results in memory
5. **Safety**: Shell and Git tools restrict allowed commands
6. **Context isolation**: `AgentContext` carries workspace, dataset, conversation, and tools

### Tests Performed
- [x] All 87 unit tests pass (11 new agent tests + 76 existing)
- [x] BaseTool protocol conformance for all tools
- [x] Memory add/build operations
- [x] Planner with valid JSON and fallback on invalid JSON
- [x] Executor retrieve and tool steps
- [x] End-to-end orchestrator run

---

## Phase 12: Testing and Production Hardening

**Date:** 2026-08-03

### Completed Tasks
- [x] Implemented `RequestIdMiddleware` for request tracing
- [x] Implemented `RequestLoggingMiddleware` for access logs
- [x] Implemented `SecurityHeadersMiddleware` for security headers
- [x] Implemented `RateLimitMiddleware` for IP-based rate limiting
- [x] Implemented `ErrorHandlingMiddleware` for global exception handling
- [x] Registered all middleware in `app/main.py`
- [x] All 91 unit tests pass (4 new middleware tests + 87 existing)

### Created Files

**Middleware:**
- `app/api/middleware.py` - All middleware implementations

**Tests:**
- `tests/unit/test_middleware.py` - 4 tests covering request ID, security headers, rate limiting, error handling

### Middleware Stack

| Order | Middleware | Purpose |
|-------|------------|---------|
| 1 | ErrorHandlingMiddleware | Catches unhandled exceptions, returns 500 |
| 2 | RateLimitMiddleware | IP + path based rate limiting |
| 3 | SecurityHeadersMiddleware | HSTS, X-Frame-Options, XSS protection |
| 4 | RequestLoggingMiddleware | Access logging with timing |
| 5 | RequestIdMiddleware | Request ID generation and propagation |
| 6 | CORSMiddleware | CORS configuration |

### Design Decisions
1. **Layered middleware**: Error handling innermost, CORS outermost
2. **Rate limiting**: Per IP + path, configurable max requests and window
3. **Request ID**: Generated if missing, returned in response header
4. **Security headers**: Strict transport security, frame options, XSS protection
5. **Logging**: Includes request ID, method, path, status, duration

### Tests Performed
- [x] All 91 unit tests pass (4 new middleware tests + 87 existing)
- [x] Request ID middleware generates and returns IDs
- [x] Security headers middleware sets all required headers
- [x] Rate limit middleware blocks excess requests with 429
- [x] Error handling middleware catches unhandled exceptions

---

## Phase 1: Project Skeleton, Configuration, Docker, Database Foundation

**Date:** 2026-08-03

### Completed Tasks
- [x] Created project directory structure
- [x] Written pyproject.toml with all dependencies
- [x] Created configuration files (development/production/testing)
- [x] Set up Docker Compose (postgres, redis, api, worker, ollama)
- [x] Created Makefile with dev/run/test/lint commands
- [x] Implemented database models and SQLAlchemy async setup
- [x] Set up Alembic migrations
- [x] Created initial test suite
- [x] Written Phase 1 documentation

### Created Files

**Core Application:**
- `app/__init__.py`
- `app/main.py` - FastAPI entry point with health check
- `app/config.py` - Pydantic-based configuration with YAML + env support
- `app/logging_config.py` - Centralized logging setup
- `app/db/session.py` - Async SQLAlchemy session factory
- `app/db/types.py` - Custom pgvector type
- `app/models/base.py` - All ORM models (Workspace, Dataset, Document, Chunk, Embedding, Conversation, Message, Task)
- `app/worker/__init__.py`
- `app/worker/celery_app.py` - Celery app configuration
- `app/worker/tasks.py` - Initial Celery tasks

**Configuration:**
- `config/development.yaml`
- `config/production.yaml`
- `config/testing.yaml`
- `config/alembic.ini`

**Infrastructure:**
- `infra/Dockerfile.api`
- `infra/Dockerfile.worker`
- `docker-compose.yml`

**Tests:**
- `tests/conftest.py` - Shared fixtures
- `tests/unit/test_models.py` - Database model tests
- `tests/unit/test_api.py` - API endpoint tests
- `tests/unit/test_config.py` - Configuration tests

**Documentation:**
- `docs/architecture.md`
- `docs/decisions/ADR-001-project-architecture.md`
- `docs/decisions/ADR-002-provider-design.md`
- `docs/database.md`
- `docs/ingestion.md`
- `docs/retrieval.md`
- `docs/llm-providers.md`
- `docs/api.md`
- `docs/deployment.md`

**Build/Dev:**
- `pyproject.toml`
- `Makefile`
- `.env.example`
- `migrations/env.py`
- `migrations/versions/001_initial.py`

### Design Decisions

1. **Clean Architecture with Async SQLAlchemy**: Chosen for industry-standard tooling, excellent async support, and mature ecosystem. Trade-off: SQLAlchemy async is relatively new, but well-tested patterns exist.

2. **Provider Abstraction Interfaces**: All external dependencies (LLM, Embedding, VectorStore) accessed through abstract interfaces for easy swapping. Trade-off: More initial code for better long-term maintainability.

3. **PostgreSQL + pgvector**: Single database for metadata and vectors reduces operational complexity. Trade-off: Less specialized than dedicated vector DBs, but sufficient for most use cases.

4. **Pydantic Settings**: Type-safe configuration with YAML files and environment variable overrides. Trade-off: Slightly more complex than plain env vars, but much more maintainable.

### Tests Performed
- [ ] pytest execution (pending Docker/PostgreSQL setup)
- [ ] Configuration loading
- [ ] API health endpoint

### Remaining Tasks
- All phases complete.

---

## Phase 7: Retrieval Pipeline (Dense, BM25, Hybrid, Reranking)

**Date:** 2026-08-03

### Completed Tasks
- [x] Defined `Retriever` and `Reranker` protocols in `app/retrieval/base.py`
- [x] Implemented `DenseRetriever` using `EmbeddingProvider` and `VectorStore`
- [x] Implemented `BM25Retriever` using `rank_bm25.BM25Okapi`
- [x] Implemented `HybridRetriever` with weighted dense + BM25 fusion
- [x] Implemented `CrossEncoderReranker` wrapper (optional dependency)
- [x] Implemented metadata filter helper (`apply_filters`)
- [x] Implemented `RetrievalPipeline` orchestrator with configurable top-k and similarity threshold
- [x] All 62 unit tests pass

### Created Files

**Retrieval:**
- `app/retrieval/__init__.py`
- `app/retrieval/base.py` - `Retriever` and `Reranker` protocols
- `app/retrieval/retrievers/dense.py` - `DenseRetriever` with embedding + vector search
- `app/retrieval/retrievers/bm25.py` - `BM25Retriever` with on-demand indexing
- `app/retrieval/retrievers/hybrid.py` - `HybridRetriever` with normalized weighted fusion
- `app/retrieval/rerankers/cross_encoder.py` - `CrossEncoderReranker` wrapper
- `app/retrieval/filters/__init__.py`
- `app/retrieval/filters/metadata.py` - SQLAlchemy filter helper
- `app/retrieval/pipeline.py` - `RetrievalPipeline` orchestrator

**Tests:**
- `tests/unit/test_retrieval.py` - 10 tests covering all retrievers, reranker, filters, and pipeline

### Design Decisions
1. **Protocol-based interfaces**: `Retriever` and `Reranker` use `@runtime_checkable` Protocol
2. **Dense retrieval**: Embeds query via `EmbeddingProvider`, searches `VectorStore`, fetches chunk text
3. **BM25 retrieval**: Loads chunks from DB on-demand, indexes with `BM25Okapi`, returns scored results
4. **Hybrid fusion**: Normalizes dense and BM25 scores to [0,1], applies configurable weights
5. **Reranker**: Cross-encoder reranking is optional; if provided, re-scores top results
6. **Pipeline orchestration**: Applies similarity threshold filtering, optional reranking, and top-k truncation
7. **BM25 negative scores**: `rank_bm25` can return negative scores for short queries; handled by taking top-k regardless of sign

### Tests Performed
- [x] All 62 unit tests pass (10 new retrieval tests + 52 existing)
- [x] Dense retriever with mocked embedding provider and vector store
- [x] BM25 retriever with mocked database
- [x] Hybrid retriever combining dense and BM25 results
- [x] Cross-encoder reranker with mocked model
- [x] Metadata filter application
- [x] Pipeline with and without reranker
- [x] Similarity threshold filtering

---

## Phase 6: PgVectorStore Implementation

**Date:** 2026-08-03

### Completed Tasks
- [x] Defined `VectorStore` protocol in `app/providers/vectordb/base.py`
- [x] Implemented `PgVectorStore` using async SQLAlchemy and pgvector
- [x] Added `add()` method for storing embeddings with metadata
- [x] Added `search()` method with cosine distance and optional filters
- [x] Added `delete()` method for removing embeddings by chunk_id
- [x] All 52 unit tests pass

### Created Files

**Vector Store:**
- `app/providers/vectordb/__init__.py`
- `app/providers/vectordb/base.py` - `VectorStore` protocol with `add`, `search`, `delete`
- `app/providers/vectordb/pgvector.py` - `PgVectorStore` implementation using pgvector cosine distance

**Tests:**
- `tests/unit/test_vector_stores.py` - 6 tests covering add, search, filters, delete, and protocol conformance

### Design Decisions
1. **Protocol-based interface**: `VectorStore` uses `@runtime_checkable` Protocol for structural subtyping
2. **Cosine distance**: Uses pgvector's `<=>` operator via SQLAlchemy for semantic similarity search
3. **Filter support**: `search()` accepts optional `filters` dict for `workspace_id` and `dataset_id`
4. **Score conversion**: Distance is converted to similarity score via `1 - distance`
5. **Metadata passthrough**: `add()` accepts metadata dict for workspace/dataset/model tracking

### Tests Performed
- [x] All 52 unit tests pass (6 new vector store tests + 46 existing)
- [x] Add embeddings with metadata
- [x] Vector search with cosine distance
- [x] Filtered search by workspace_id and dataset_id
- [x] Delete existing and nonexistent embeddings
- [x] Protocol conformance check

---

## Phase 5: Embedding Provider Interface and Ollama Implementation

**Date:** 2026-08-03

### Completed Tasks
- [x] Defined `EmbeddingProvider` protocol in `app/providers/embeddings/base.py`
- [x] Implemented `OllamaEmbeddingProvider` using `httpx` async client
- [x] Implemented `BgeEmbeddingProvider` using `sentence-transformers`
- [x] Implemented `E5EmbeddingProvider` using `sentence-transformers`
- [x] Implemented `NomicEmbeddingProvider` using `sentence-transformers`
- [x] Created factory function `get_embedding_provider()` in `app/providers/embeddings/__init__.py`
- [x] Updated `app/ingestion/indexer.py` to import central `EmbeddingProvider`
- [x] All 46 unit tests pass

### Created Files

**Providers:**
- `app/providers/__init__.py`
- `app/providers/embeddings/__init__.py` - Factory function `get_embedding_provider()`
- `app/providers/embeddings/base.py` - `EmbeddingProvider` protocol
- `app/providers/embeddings/ollama.py` - `OllamaEmbeddingProvider` with async HTTP batch embedding
- `app/providers/embeddings/bge.py` - `BgeEmbeddingProvider` using `sentence-transformers`
- `app/providers/embeddings/e5.py` - `E5EmbeddingProvider` using `sentence-transformers`
- `app/providers/embeddings/nomic.py` - `NomicEmbeddingProvider` using `sentence-transformers`

**Tests:**
- `tests/unit/test_embeddings.py` - 7 tests covering all providers and protocol conformance

### Design Decisions
1. **Protocol-based interface**: `EmbeddingProvider` uses `@runtime_checkable` Protocol for structural subtyping
2. **Ollama via HTTP**: Uses `httpx.AsyncClient` to call `/api/embeddings` endpoint with `asyncio.gather` for batch processing
3. **Local models via sentence-transformers**: BGE, E5, and Nomic providers use `sentence-transformers` with lazy model loading
4. **Factory pattern**: `get_embedding_provider()` resolves provider from `settings.embedding.provider`
5. **Graceful output handling**: Providers handle both numpy arrays (`.tolist()`) and plain lists

### Tests Performed
- [x] All 46 unit tests pass (7 new embedding tests + 39 existing)
- [x] Ollama single and batch embedding
- [x] BGE/E5/Nomic embedding with mocked sentence-transformers
- [x] Protocol conformance checks

---

## Phase 4: PostgreSQL Ingestion Connector

**Date:** 2026-08-03

### Completed Tasks
- [x] Implemented `PostgresInspector` for schema introspection
- [x] Implemented `PostgresConnector` with async SQLAlchemy engine
- [x] Added table filtering support (`tables` parameter)
- [x] Added row-to-text conversion for document generation
- [x] All 39 unit tests pass

### Created Files

**Connectors:**
- `app/connectors/postgres/__init__.py`
- `app/connectors/postgres/inspector.py` - `PostgresInspector` for schema introspection
- `app/connectors/postgres/loader.py` - `PostgresConnector` with async engine and row-to-text conversion

**Tests:**
- `tests/unit/test_connectors.py` - Added 5 PostgreSQL connector tests

### Design Decisions
1. **Inspector pattern**: Separated schema inspection into `PostgresInspector` for single responsibility
2. **Async engine**: Uses `create_async_engine` with `asyncpg` driver
3. **Table filtering**: Optional `tables` parameter to limit ingestion to specific tables
4. **Row-to-text**: Converts each row to a human-readable text format: `Table: {table}\n- {column}: {value}`
5. **Engine lifecycle**: Creates engine per `load()` call and disposes after completion

### Tests Performed
- [x] All 39 unit tests pass (5 new PostgreSQL tests + 34 existing)
- [x] Schema introspection (get_tables, get_columns)
- [x] Document loading with mocked async engine
- [x] Table filtering
- [x] Row-to-text conversion

---

## Phase 3: Markdown Ingestion Connector

**Date:** 2026-08-03

### Completed Tasks
- [x] Implemented `BaseConnector` abstract interface
- [x] Implemented `MarkdownConnector` with recursive `.md` file discovery
- [x] Implemented YAML frontmatter parsing for Markdown files
- [x] Implemented text cleaner (whitespace normalization)
- [x] Implemented text splitter with configurable chunk size and overlap
- [x] Implemented `Indexer` for persisting Documents, Chunks, and Embeddings
- [x] Implemented `IngestionPipeline` orchestrator
- [x] Implemented `Embedder` wrapper for embedding providers
- [x] All 34 unit tests pass

### Created Files

**Connectors:**
- `app/connectors/__init__.py`
- `app/connectors/base.py` - `BaseConnector` abstract interface
- `app/connectors/markdown/__init__.py`
- `app/connectors/markdown/loader.py` - `MarkdownConnector`
- `app/connectors/markdown/parser.py` - Placeholder for future Markdown parsing utilities

**Ingestion:**
- `app/ingestion/__init__.py`
- `app/ingestion/cleaner.py` - Text normalization (whitespace, newlines)
- `app/ingestion/splitter.py` - Token-based text chunking with overlap
- `app/ingestion/metadata.py` - Placeholder for metadata extraction utilities
- `app/ingestion/embedder.py` - `Embedder` class wrapping embedding providers
- `app/ingestion/indexer.py` - `Indexer` for DB persistence of Document, Chunk, Embedding
- `app/ingestion/pipeline.py` - `IngestionPipeline` orchestrator + `IngestionResult` dataclass

**Tests:**
- `tests/unit/test_connectors.py` - 8 tests for Markdown connector, cleaner, and splitter

### Design Decisions
1. **Connector interface**: Simple async `load(path, dataset_id, workspace_id)` returning list of document dicts
2. **Markdown connector**: Recursively scans directories for `.md` files, preserves directory structure in metadata
3. **Frontmatter parsing**: Extracts YAML frontmatter between `---` delimiters into metadata dict
4. **Tokenizer-free splitter**: Uses whitespace tokenization for simplicity; can be replaced with tiktoken later
5. **Indexer**: Creates Document -> Chunk -> Embedding records in a single async transaction
6. **Pipeline**: Thin orchestrator that loads, indexes, and returns statistics

### Tests Performed
- [x] All 34 unit tests pass (8 new connector/ingestion tests + 26 existing)
- [x] Markdown file loading from nested directories
- [x] Frontmatter extraction
- [x] FileNotFoundError for missing paths
- [x] Text cleaning (whitespace, carriage returns)
- [x] Text splitting with overlap
- [x] Empty and short text edge cases

---

## Phase 2: Workspace and Dataset Management API

**Date:** 2026-08-03

### Completed Tasks
- [x] Implemented workspace repository and service
- [x] Implemented dataset repository and service
- [x] Created Pydantic schemas for workspace/dataset CRUD
- [x] Implemented FastAPI routers for `/workspaces` and `/datasets`
- [x] Registered routers in `app/main.py`
- [x] Added async test client for API endpoint testing
- [x] All 26 unit tests pass

### Created Files

**Schemas:**
- `app/api/schemas/workspace.py` - WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceList
- `app/api/schemas/dataset.py` - DatasetCreate, DatasetUpdate, DatasetResponse, DatasetList

**Repositories:**
- `app/repositories/workspace.py` - WorkspaceRepository with async CRUD
- `app/repositories/dataset.py` - DatasetRepository with async CRUD + count_by_workspace

**Services:**
- `app/services/workspace.py` - WorkspaceService (thin wrapper over repo)
- `app/services/dataset.py` - DatasetService with workspace-scoped listing

**API Routers:**
- `app/api/routers/workspaces.py` - POST/GET/PATCH/DELETE `/workspaces`
- `app/api/routers/datasets.py` - POST/GET/PATCH/DELETE `/datasets` with optional `workspace_id` filter

**Tests:**
- `tests/unit/test_workspaces_datasets.py` - 15 async API endpoint tests

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/workspaces` | Create workspace |
| GET | `/workspaces` | List all workspaces |
| GET | `/workspaces/{id}` | Get workspace by ID |
| PATCH | `/workspaces/{id}` | Update workspace |
| DELETE | `/workspaces/{id}` | Delete workspace |
| POST | `/datasets` | Create dataset (requires `workspace_id`) |
| GET | `/datasets` | List all datasets (optional `?workspace_id=`) |
| GET | `/datasets/{id}` | Get dataset by ID |
| PATCH | `/datasets/{id}` | Update dataset |
| DELETE | `/datasets/{id}` | Delete dataset |

### Design Decisions
1. **Repository pattern**: All DB access goes through repositories for testability
2. **Service layer**: Thin services wrap repositories; business logic can be added here
3. **Async SQLAlchemy**: Full async support with `AsyncSession` and `asyncpg`
4. **Test isolation**: `clean_tables` fixture truncates all tables between tests
5. **NullPool for tests**: Avoids connection pool conflicts in test environment

### Tests Performed
- [x] All 26 unit tests pass (15 new API tests + 11 existing)
- [x] Workspace CRUD operations
- [x] Dataset CRUD operations
- [x] Dataset filtering by workspace_id
- [x] 404 handling for not-found resources
