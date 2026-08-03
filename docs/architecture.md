# RAG Platform Architecture

## Overview

The RAG Platform is a production-ready, modular Retrieval-Augmented Generation framework designed to support multiple independent projects (workspaces) with isolated knowledge bases.

## Core Principles

1. **Clean Architecture**: Strict separation between API, business logic, data access, and external providers
2. **Modular Design**: Every external dependency has an abstraction layer for easy swapping
3. **Workspace Isolation**: Each project operates in its own isolated workspace
4. **Provider Agnostic**: LLMs, embeddings, and vector stores are pluggable
5. **Async First**: All I/O operations are asynchronous for high throughput

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 API Layer                                   │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │ Workspaces   │  │ Datasets     │  │ Documents    │  │ Chat         │   │
│   │ Endpoints    │  │ Endpoints    │  │ Endpoints    │  │ Endpoints    │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Business Logic                                   │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │ Agent        │  │ Orchestrator │  │ Planner      │  │ Memory       │   │
│   │ Orchestrator │  │              │  │              │  │ System       │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Core Services                                    │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │ Ingestion    │  │ Retrieval    │  │ Reranking    │  │ Chat         │   │
│   │ Pipeline     │  │ Pipeline     │  │              │  │ Service      │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Provider Abstractions                                │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │ LLMProvider  │  │ Embedding    │  │ VectorStore  │  │ Connector    │   │
│   │              │  │ Provider     │  │              │  │              │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Infrastructure                                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │ PostgreSQL   │  │ pgvector     │  │ Redis        │  │ Celery       │   │
│   │ + pgvector   │  │              │  │              │  │ Worker       │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Workspace Architecture

Each workspace is an isolated RAG system:

```
Workspace: "Ecommerce Project"
├── Dataset: "Product Documentation"
│   ├── Documents: product_manual.md, api_docs.md
│   ├── Chunks: 120 chunks
│   └── Embeddings: 120 vectors (bge_m3)
├── Dataset: "Technical Manuals"
│   ├── Documents: manual_1.pdf, manual_2.md
│   ├── Chunks: 85 chunks
│   └── Embeddings: 85 vectors (bge_m3)
└── Conversation Memory
    ├── Conversation: "Product Support"
    │   ├── Message: "How do I configure X?"
    │   └── Message: "You can configure X by..."
    └── Task Memory
        └── Task: "Onboard new support agent"
```

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `app/api/` | FastAPI route definitions, request/response schemas |
| `app/agent/` | Agent orchestration, planning, execution |
| `app/connectors/` | Data source connectors (Markdown, PostgreSQL, etc.) |
| `app/ingestion/` | Document processing pipeline (clean, split, embed) |
| `app/retrieval/` | Dense, BM25, hybrid retrieval, reranking |
| `app/providers/` | LLM, embedding, vector store provider interfaces |
| `app/memory/` | Conversation and task memory management |
| `app/tools/` | Internal tools (filesystem, git, postgres, search) |
| `app/services/` | Business logic and use cases |
| `app/repositories/` | Data access layer |
| `app/models/` | SQLAlchemy ORM models |
| `app/db/` | Database connection and session management |
| `app/worker/` | Celery async task definitions |
| `app/config/` | Configuration management |
| `app/utils/` | Shared utilities |

## Data Flow

### Ingestion Pipeline
```
Connector → Loader → Cleaner → Splitter → Metadata → Embedding → VectorStore
```

### Chat Pipeline
```
User Query → Embedding → Vector Search → BM25 Search → Hybrid Merge → Rerank → LLM
```

## Key Design Decisions

1. **PostgreSQL + pgvector**: Single database for both metadata and vectors reduces operational complexity
2. **Async SQLAlchemy**: Non-blocking database access for high concurrency
3. **Pydantic Settings**: Type-safe configuration with env var overrides
4. **Celery**: Reliable async processing for long-running ingestion tasks
5. **Provider Interfaces**: All external services accessed through abstract interfaces

## Scalability Considerations

- **Horizontal**: Stateless API workers can scale behind a load balancer
- **Vertical**: PostgreSQL + pgvector handles millions of vectors
- **Future Vector DB**: Provider abstraction allows migration to Qdrant/Milvus
- **Caching**: Redis for query caching and session storage
