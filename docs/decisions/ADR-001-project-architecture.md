# Decision Records

## ADR-001: Project Architecture - Clean Architecture with Async SQLAlchemy

**Date:** 2026-08-03

**Status:** Accepted

**Context:**
We need to build a reusable RAG Platform that can serve multiple projects with isolated workspaces. The system must be modular, testable, and production-ready.

**Decision:**
Use Clean Architecture principles with the following layers:
- API Layer (FastAPI)
- Business Logic (Services)
- Data Access (Repositories)
- External Providers (Abstractions)
- Infrastructure (Database, Cache, Queue)

Database access will use SQLAlchemy 2.x Async with PostgreSQL + pgvector.

**Alternatives Considered:**
1. **Django ORM**: Too opinionated, harder to decouple
2. **Tortoise ORM**: Good async support but smaller ecosystem and less mature
3. **Prisma (Python)**: Limited async support, less flexible for complex queries
4. **MongoDB**: No native vector search, requires additional infrastructure

**Trade-offs:**
- **Pros**: Industry-standard tooling, excellent async support, mature ecosystem
- **Cons**: SQLAlchemy async is relatively new, some edge cases still being ironed out
- **Mitigation**: Use well-tested patterns, extensive testing

---

## ADR-002: Provider Design - Abstract Interfaces for All External Dependencies

**Date:** 2026-08-03

**Status:** Accepted

**Context:**
The RAG platform must support multiple LLM providers (Ollama, OpenAI, Anthropic, Gemini), multiple embedding models (BGE-M3, E5, Nomic, OpenAI), and potentially multiple vector stores (pgvector, Qdrant, Milvus).

**Decision:**
Define abstract base classes (Protocol/ABC) for all provider types:
- `LLMProvider`
- `EmbeddingProvider`
- `VectorStore`

Each provider has a concrete implementation that can be selected via configuration. New providers can be added without changing existing code.

**Alternatives Considered:**
1. **Direct Implementation**: No abstraction, call providers directly
   - Pro: Simpler initially
   - Con: Impossible to swap providers without changing business logic

2. **Factory Pattern Only**: Use factories but no common interface
   - Pro: Some flexibility
   - Con: Code duplication across implementations

3. **Plugin System**: Dynamic plugin loading
   - Pro: Maximum extensibility
   - Con: Too complex for Phase 1, adds unnecessary indirection

**Trade-offs:**
- **Pros**: Testability (easy mocking), extensibility (new providers without refactoring), consistency
- **Cons**: More initial code, slight overhead from indirection
- **Mitigation**: Keep interfaces minimal and focused, use Protocol for structural subtyping
