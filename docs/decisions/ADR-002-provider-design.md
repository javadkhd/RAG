# Provider Design Decision

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
