# Ingestion Pipeline

## Architecture

```
┌─────────────┐     ┌─────────┐     ┌────────┐     ┌──────────┐     ┌──────────────────┐     ┌──────────────┐
│  Markdown   │     │         │     │        │     │  Chunking │     │  Embedding      │     │  pgvector    │
│  Files      │────>│ Loader  │────>│ Cleaner │────>│  Splitter │────>│  Generation     │────>│  Storage     │
│  (.md)      │     │ (Conn.) │     │         │     │          │     │  (Provider)     │     │  (vectors)   │
└─────────────┘     └─────────┘     └────────┘     └──────────┘     └──────────────────┘     └──────────────┘
                            │                              │                    │                    │
                            └──────────────────────────────┴────────────────────┴────────────────────┘
                                                                                   ┌──────────┐
                                                                                   │ Database │
                                                                                   │ (async)  │
                                                                                   └──────────┘
```

## Data Flow

```
1. User places markdown files in data/docs/
2. User creates a workspace (POST /workspaces)
3. User creates a dataset with connector_type="markdown" and connector_config={"path": "data/docs"} (POST /datasets)
4. User triggers ingestion (POST /datasets/{id}/ingest)
5. API queues a Celery task and returns task_id
6. Worker picks up the task:
   a. Loads dataset from database
   b. Creates MarkdownConnector with path from connector_config
   c. Runs IngestionPipeline:
      - Loads documents via connector
      - Cleans text (whitespace normalization)
      - Splits into chunks (configurable size/overlap)
      - Stores chunks in documents/chunks tables
      - Generates embeddings via configured provider
      - Stores embeddings in embeddings table (pgvector)
7. User can now chat with RAG using the ingested data
```

## Components

### Connectors

#### Markdown Connector (`app/connectors/markdown/loader.py`)

- Reads `.md` files recursively from a directory path
- Supports UTF-8 encoding
- Extracts YAML-like frontmatter from file headers
- Preserves metadata:
  - `path` — relative path within the source directory
  - `directory` — parent directory relative to source
  - `size_bytes` — file size in bytes
  - `filename` — file name
  - `frontmatter` — parsed frontmatter key-value pairs

#### PostgreSQL Connector (`app/connectors/postgres/loader.py`)

- Reads table schemas
- Converts rows to text documents
- Supports selective table inclusion

### Ingestion Pipeline (`app/ingestion/pipeline.py`)

Orchestrates the ingestion flow:

1. **Load** — Calls connector's `load()` method to get documents
2. **Index** — Hands documents to `Indexer` for processing:
   - Creates `Document` records
   - Cleans text via `Cleaner`
   - Splits into chunks via `Splitter`
   - Creates `Chunk` records
   - Generates embeddings via `EmbeddingProvider`
   - Creates `Embedding` records with pgvector vectors
3. **Result** — Returns `IngestionResult` with counts and any errors

### Cleaner (`app/ingestion/cleaner.py`)

- Normalizes line endings (CRLF → LF)
- Collapses excessive whitespace
- Strips leading/trailing whitespace

### Splitter (`app/ingestion/splitter.py`)

- Splits text by word tokens
- Configurable `chunk_size` (default: 512 tokens)
- Configurable `overlap` (default: 50 tokens)
- Creates overlapping chunks for context continuity

### Embedder

Uses the configured `EmbeddingProvider` to convert text chunks to vectors:

- **Ollama** (`OllamaEmbeddingProvider`) — HTTP API to Ollama
- **BGE-M3** (`BgeEmbeddingProvider`) — Local `sentence-transformers` model
- **E5** (`E5EmbeddingProvider`) — Local `sentence-transformers` model
- **Nomic** (`NomicEmbeddingProvider`) — Local `sentence-transformers` model

### Database Storage

All data is stored in PostgreSQL with pgvector extension:

| Table | Description |
|-------|-------------|
| `workspaces` | Isolated project containers |
| `datasets` | Collections of documents within workspaces |
| `documents` | Source files with metadata |
| `chunks` | Text chunks with document references |
| `embeddings` | Vector embeddings linked to chunks |

## Worker Processing

Ingestion runs asynchronously in Celery workers:

1. API endpoint queues `ingest_dataset` task
2. Celery worker picks up the task
3. Worker initializes database connection
4. `IngestionService.ingest_dataset()` loads dataset, creates connector, runs pipeline
5. Results returned to Celery result backend

## Configuration

Configuration comes from `.env` file and YAML configs:

| Setting | Env Var | Default | Description |
|---------|---------|---------|-------------|
| Chunking | — | 512 | Token count per chunk |
| Overlap | — | 50 | Token overlap between chunks |
| Embedding provider | `EMBEDDING_PROVIDER` | `bge_m3` | ollama, bge_m3, e5, nomic |
| Embedding model | `EMBEDDING_MODEL_NAME` | `BAAI/bge-m3` | Model identifier |
| Embedding device | `EMBEDDING_DEVICE` | `cpu` | cpu or cuda |
| LLM model | `LLM_MODEL` | `llama3` | Model for Ollama provider |

## Multi-Tenant Isolation

All data is isolated by `workspace_id` and `dataset_id`:

- Documents belong to a workspace and dataset
- Chunks reference their document and dataset
- Embeddings are filtered by workspace_id and dataset_id during retrieval