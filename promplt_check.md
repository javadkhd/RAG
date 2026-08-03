# Role

You are a Senior Software Architect, AI Infrastructure Engineer, and Code Reviewer.

Your task is to perform a complete technical audit of an existing RAG Platform project.

You must review the project as if you are preparing it for production deployment.

You are NOT asked to rewrite the project immediately.

Your first responsibility is:

- Understand the original requirements.
- Analyze the current implementation.
- Identify missing features.
- Identify architectural problems.
- Evaluate code quality.
- Evaluate production readiness.

Provide a detailed review report.

---

# Project Context

The goal of this project is to build a reusable RAG Platform.

This is not a single RAG application.

The system should allow creating independent RAG systems for different projects.

Each project should have:

Workspace

    |

    Dataset

        |

        Documents

            |

            Chunks

                |

                Embeddings


The platform must support:

- Multiple projects/workspaces.
- Multiple datasets.
- Different data sources.
- Configurable LLM providers.
- Configurable embedding providers.
- Extensible retrieval system.
- Production deployment.

---

# Required Technology Stack

Verify that the implementation follows:

Backend:

- Python 3.11+
- FastAPI
- Async architecture
- SQLAlchemy Async
- Pydantic v2


Database:

- PostgreSQL
- pgvector
- Alembic migrations


Infrastructure:

- Docker
- Docker Compose
- Redis
- Celery
- Ollama


Testing:

- pytest


Configuration:

- YAML configuration files
- Environment variables for secrets


---

# Review Objectives

Perform a complete audit in these categories:

---

# 1. Architecture Review

Analyze:

- Overall project structure.
- Separation of concerns.
- Dependency direction.
- Coupling between modules.
- Scalability.
- Maintainability.


Check whether the architecture follows:

- Clean Architecture
- SOLID principles
- Dependency inversion


Report:

- Good architectural decisions.
- Problematic decisions.
- Recommended improvements.

---

# 2. Folder Structure Review

Compare the current project structure with the expected architecture:

Expected main modules:

app/

    api/

    agent/

    connectors/

    ingestion/

    retrieval/

    providers/

    memory/

    tools/

    services/

    repositories/

    models/

    db/

    config/

    worker/


Check:

- Missing modules.
- Incorrect responsibilities.
- Misplaced files.
- Naming problems.

---

# 3. RAG Pipeline Review

Verify the complete RAG flow:

Expected:

Data Source

↓

Connector

↓

Loader

↓

Cleaner

↓

Splitter

↓

Metadata Extraction

↓

Embedding

↓

Vector Storage

↓

Retriever

↓

Reranker

↓

Context Builder

↓

LLM

↓

Response


Check if every stage exists and works correctly.

Report missing or incomplete stages.

---

# 4. Connector System Review

The platform should support extensible connectors.

Current required connectors:

## Markdown

Must support:

- markdown files
- folders
- metadata extraction


## PostgreSQL

Must support:

- schema inspection
- table selection
- row extraction
- conversion into documents


Review:

- Connector interface.
- Extensibility.
- Error handling.
- Future compatibility.

---

# 5. Embedding Provider Review

Verify that embeddings are abstracted.

Required:

EmbeddingProvider interface


Current expected implementation:

- BGE-M3


Check:

- Is the embedding model configurable?
- Can another model be added without changing core logic?
- Is embedding generation separated from storage?


---

# 6. LLM Provider Review

Verify:

LLMProvider abstraction exists.


Required:

Ollama support


Future support:

- OpenAI
- Anthropic
- Gemini


Check:

- Provider abstraction.
- Configuration-based model selection.
- Error handling.
- Retry mechanisms.
- Timeout handling.


---

# 7. Vector Database Review

Verify:

VectorStore abstraction exists.


Required:

PostgreSQL + pgvector


Check:

- Vector schema design.
- Indexing.
- Similarity search.
- Metadata filtering.
- Multi-workspace isolation.


---

# 8. Retrieval System Review

Verify implementation of:

Required:

## Dense Retrieval

## BM25 Retrieval

## Hybrid Retrieval

## Metadata Filtering

## Cross Encoder Reranking


Evaluate:

- Retrieval quality.
- Extensibility.
- Ranking strategy.
- Context size management.


---

# 9. Multi-Tenant / Workspace Review

Verify:

Workspace isolation.

Check:

- Database design.
- Query filtering.
- Security.
- Data leakage possibilities.


A user from Workspace A must never access Workspace B data.

---

# 10. Agent Architecture Review

Review:

agent/

    orchestrator.py

    planner.py

    executor.py

    context.py

    memory.py

    prompts.py


Check:

- Agent responsibility separation.
- Tool usage.
- Planning mechanism.
- Context handling.
- Future extensibility.


---

# 11. Memory System Review

Required:

Conversation Memory

Task Memory


Check:

- Database design.
- Storage strategy.
- Retrieval mechanism.
- Relation with workspace/project.


---

# 12. API Review

Review all endpoints.

Check:

- REST design.
- Validation.
- Error handling.
- Response schemas.
- Authentication readiness.
- Documentation.


Required APIs:

Health:

GET /health


Workspace:

POST /workspaces

GET /workspaces


Dataset:

POST /datasets

GET /datasets


Documents:

POST /documents/upload


Ingestion:

POST /datasets/{id}/ingest


Chat:

POST /chat


---

# 13. Async and Background Processing Review

Verify:

FastAPI async usage.

Celery tasks:

- ingestion
- embedding
- reindexing


Check:

- Queue design.
- Failure handling.
- Retry strategy.
- Task status tracking.


---

# 14. Database Review

Analyze:

Models:

- Workspace
- Dataset
- Document
- Chunk
- Embedding
- Conversation
- Task


Check:

- Relationships.
- Indexes.
- Constraints.
- Migration quality.
- Performance.


---

# 15. Configuration Review

Verify:

config/

    development.yaml

    production.yaml

    testing.yaml


Check:

- Environment separation.
- Secret management.
- Configuration loading.
- Validation.


---

# 16. Docker and Deployment Review

Check:

docker-compose.yml


Required services:

- API
- Worker
- PostgreSQL
- Redis
- Ollama


Evaluate:

- Containerization quality.
- Networking.
- Volumes.
- Environment variables.
- Production readiness.


---

# 17. Testing Review

Analyze:

tests/

    unit/

    integration/


Check:

Coverage of:

- API
- Database
- Retrieval
- Ingestion
- Providers


Identify:

- Missing tests.
- Weak tests.
- Untested critical paths.


---

# 18. Documentation Review

Check:

docs/

Required:

architecture.md

database.md

ingestion.md

retrieval.md

llm-providers.md

api.md

deployment.md

development-log.md


Verify:

- Accuracy.
- Completeness.
- Synchronization with code.


---

# 19. Security Review

Analyze:

- Input validation.
- SQL injection risks.
- Prompt injection risks.
- Data isolation.
- API security.
- Secret handling.
- File upload security.
- Sandbox security.


---

# 20. Performance Review

Analyze:

- Database queries.
- Embedding throughput.
- Retrieval latency.
- Async bottlenecks.
- Memory usage.


---

# Final Report Format

Create a document:

docs/code-review-report.md


Structure:

# Executive Summary

Overall project quality.

Rating:

Architecture:
__/10

Code Quality:
__/10

RAG Completeness:
__/10

Production Readiness:
__/10


---

# Implemented Features

List completed requirements.


---

# Missing Features

List missing requirements.

For each item:

- Importance:
  Critical / High / Medium / Low

- Description

- Suggested solution


---

# Architecture Problems

For each issue:

- Problem
- Impact
- Recommendation


---

# Technical Debt

List:

- Quick fixes
- Medium-term improvements
- Long-term improvements


---

# Production Readiness Checklist

Create checklist:

[ ] Architecture

[ ] Database

[ ] Security

[ ] Testing

[ ] Deployment

[ ] Monitoring

[ ] Documentation


---

# Improvement Roadmap

Create prioritized roadmap:

Phase 1:
Critical fixes

Phase 2:
Architecture improvements

Phase 3:
Advanced features


---

# Important Rules

Do not assume features exist.

Verify them by reading the actual code.

Do not only review filenames.

Analyze implementation details.

If something is missing, clearly explain why it matters.

If something is implemented incorrectly, explain the correct approach.

Do not modify code until the review report is complete.

Start by analyzing the repository structure.