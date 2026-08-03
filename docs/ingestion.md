# Ingestion Pipeline

## Pipeline Stages

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────────────┐    ┌──────────────┐    ┌─────────────────┐
│ Connector│ -> │ Loader  │ -> │ Cleaner │ -> │ Splitter/Chunker │ -> │ Metadata Ext │ -> │ Embedding Gen  │
└─────────┘    └─────────┘    └─────────┘    └──────────────────┘    └──────────────┘    └─────────────────┘
                                                                                                                 │
                                                                                                                 ▼
                                                                                                        ┌──────────────┐
                                                                                                        │ Vector Store │
                                                                                                        └──────────────┘
```

## Connectors

### Markdown Connector
- Reads `.md` files from directories
- Preserves directory structure as metadata
- Extracts frontmatter if present

### PostgreSQL Connector
- Reads table schemas
- Converts rows to text documents
- Supports selective table inclusion

## Loader
Reads raw data from connectors and produces `Document` objects with metadata.

## Cleaner
Removes noise and normalizes content:
- HTML stripping (for web content)
- Whitespace normalization
- Special character handling

## Splitter
Chunks documents into overlapping segments:
- Default chunk size: 512 tokens
- Default overlap: 50 tokens
- Respects sentence boundaries when possible

## Metadata Extraction
Adds contextual metadata to each chunk:
- Document ID
- Chunk index
- Source path
- File modification time
- Connector-specific metadata

## Embedding Generation
Converts text chunks to vector embeddings:
- Uses configured `EmbeddingProvider`
- Stores in `Embedding` table
- Batch processing for efficiency

## Async Processing
Long-running ingestion runs in Celery workers:
- Document loading
- Embedding generation
- Vector indexing
