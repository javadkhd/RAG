# Database Design

## Schema Overview

### Workspace
Top-level isolation unit. All data belongs to a workspace.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Workspace name |
| description | TEXT | Optional description |
| metadata | JSONB | Flexible metadata |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Dataset
Logical grouping of documents within a workspace.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| workspace_id | UUID | FK to workspaces |
| name | VARCHAR(255) | Dataset name |
| description | TEXT | Optional description |
| connector_type | VARCHAR(100) | Source type (markdown, postgres, etc.) |
| connector_config | JSONB | Connector-specific configuration |
| metadata | JSONB | Flexible metadata |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Document
Individual source file/database table within a dataset.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| dataset_id | UUID | FK to datasets |
| workspace_id | UUID | FK to workspaces |
| source | VARCHAR(1024) | Full source path/identifier |
| filename | VARCHAR(255) | Original filename |
| content_type | VARCHAR(100) | MIME type |
| size_bytes | INTEGER | File size |
| metadata | JSONB | Flexible metadata |
| status | VARCHAR(50) | pending/processing/completed/failed |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Chunk
Text segment extracted from a document.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| document_id | UUID | FK to documents |
| dataset_id | UUID | FK to datasets |
| workspace_id | UUID | FK to workspaces |
| chunk_index | INTEGER | Order within document |
| text | TEXT | Chunk content |
| metadata | JSONB | Flexible metadata |
| token_count | INTEGER | Token count |
| created_at | TIMESTAMP | Creation timestamp |

### Embedding
Vector representation of a chunk.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| chunk_id | UUID | FK to chunks |
| workspace_id | UUID | FK to workspaces |
| dataset_id | UUID | FK to datasets |
| model | VARCHAR(255) | Embedding model name |
| dimensions | INTEGER | Vector dimensions |
| vector | VECTOR(1024) | The embedding vector |
| created_at | TIMESTAMP | Creation timestamp |

### Conversation
Chat session container.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| workspace_id | UUID | FK to workspaces |
| title | VARCHAR(255) | Conversation title |
| metadata | JSONB | Flexible metadata |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Message
Individual chat message.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| conversation_id | UUID | FK to conversations |
| role | VARCHAR(50) | user/assistant/system |
| content | TEXT | Message content |
| sources | JSONB | Retrieved sources |
| metadata | JSONB | Flexible metadata |
| created_at | TIMESTAMP | Creation timestamp |

### Task
Project task tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| workspace_id | UUID | FK to workspaces |
| title | VARCHAR(255) | Task title |
| description | TEXT | Task description |
| status | VARCHAR(50) | pending/in_progress/completed/cancelled |
| priority | VARCHAR(50) | low/medium/high |
| metadata | JSONB | Flexible metadata |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

## Indexes

- `workspaces.name` - Fast lookup by name
- `datasets.workspace_id` - All datasets in a workspace
- `documents.dataset_id` - All documents in a dataset
- `documents.workspace_id` - All documents in a workspace
- `chunks.document_id` - All chunks for a document
- `chunks.workspace_id` - All chunks in a workspace
- `embeddings.chunk_id` - Embedding lookup
- `embeddings.workspace_id` - All embeddings in a workspace
- `embeddings.dataset_id` - All embeddings in a dataset
- `conversations.workspace_id` - All conversations in a workspace
- `messages.conversation_id` - All messages in a conversation
- `tasks.workspace_id` - All tasks in a workspace

## pgvector Configuration

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Cosine similarity index for large datasets
CREATE INDEX ON embeddings 
USING ivfflat (vector vector_cosine_ops)
WITH (lists = 100);
```
