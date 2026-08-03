# API Reference

## Base URL
```
http://localhost:8000
```

## Health

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### GET /
Root endpoint with platform info.

## Workspaces

### POST /workspaces
Create a new workspace.

**Request:**
```json
{
  "name": "Ecommerce Project",
  "description": "Product knowledge base",
  "metadata": {}
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Ecommerce Project",
  "description": "Product knowledge base",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### GET /workspaces
List all workspaces.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Ecommerce Project",
    "description": "Product knowledge base"
  }
]
```

### GET /workspaces/{workspace_id}
Get workspace details.

## Datasets

### POST /datasets
Create a new dataset.

**Request:**
```json
{
  "workspace_id": "uuid",
  "name": "Product Documentation",
  "connector_type": "markdown",
  "connector_config": {"path": "/data/products"}
}
```

### GET /datasets
List all datasets (optionally filtered by workspace).

**Query Parameters:**
- `workspace_id`: UUID (optional)

### GET /datasets/{dataset_id}
Get dataset details.

## Documents

### POST /documents/upload
Upload documents to a dataset.

**Request:** `multipart/form-data`
- `files`: List of files
- `dataset_id`: UUID
- `metadata`: JSON (optional)

**Response:**
```json
[
  {
    "id": "uuid",
    "filename": "manual.md",
    "status": "pending"
  }
]
```

## Ingestion

### POST /datasets/{dataset_id}/ingest
Trigger ingestion for a dataset.

**Response:**
```json
{
  "task_id": "celery-task-id",
  "status": "queued"
}
```

### GET /datasets/{dataset_id}/ingest/{task_id}
Check ingestion task status.

## Chat

### POST /chat
Send a message to the RAG system.

**Request:**
```json
{
  "workspace_id": "uuid",
  "dataset_id": "uuid",
  "message": "How do I configure the payment gateway?"
}
```

**Response:**
```json
{
  "answer": "To configure the payment gateway, follow these steps...",
  "sources": [
    {
      "document_id": "uuid",
      "filename": "payment_guide.md",
      "text": "The payment gateway is configured by...",
      "score": 0.92
    }
  ]
}
```

### POST /chat/stream
Streaming chat endpoint (SSE).

## Conversations

### GET /conversations
List conversations in a workspace.

### GET /conversations/{conversation_id}/messages
Get messages in a conversation.

## Tasks

### POST /tasks
Create a task.

### GET /tasks
List tasks in a workspace.

### PATCH /tasks/{task_id}
Update task status.
