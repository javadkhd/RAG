# RAG Platform - Getting Started

## Prerequisites

- Python 3.11 or 3.12
- Docker and Docker Compose
- Make
- (Optional) Ollama for local LLM inference

## Step 1: Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd RAG

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make install-dev
```

## Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional, defaults work for local dev)
# DATABASE_URL=postgresql+asyncpg://rag:ragpass@localhost:5432/ragdb
# REDIS_URL=redis://localhost:6379/0
# LLM_PROVIDER=ollama
# LLM_MODEL=llama3
```

## Step 3: Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, and Ollama
make docker-up

# Verify services are running
docker compose ps
```

You should see:
- `rag_postgres` - PostgreSQL with pgvector extension
- `rag_redis` - Redis for caching and Celery broker
- `rag_ollama` - Ollama LLM server

## Step 4: Run Database Migrations

```bash
# Apply database schema
make upgrade
```

## Step 5: Start the API Server

```bash
# Development mode with hot reload
make dev

# Or manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Step 6: Start the Celery Worker

Open a new terminal:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Start worker
make worker
```

## Step 7: Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","version":"0.1.0"}
```

## Using the API

### 1. Create a Workspace

A workspace is an isolated project container.

```bash
curl -X POST http://localhost:8000/workspaces \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Knowledge base for documentation",
    "metadata": {}
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Project",
  "description": "Knowledge base for documentation",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 2. Create a Dataset

A dataset is a collection of documents within a workspace.

```bash
curl -X POST http://localhost:8000/datasets \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Product Documentation",
    "connector_type": "markdown",
    "connector_config": {"path": "./data/docs"}
  }'
```

### 3. Chat with RAG

Send a message and get an answer based on your knowledge base.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
    "dataset_id": "<dataset-id>",
    "message": "How do I configure the payment gateway?",
    "top_k": 5,
    "similarity_threshold": 0.7
  }'
```

Response:
```json
{
  "answer": "To configure the payment gateway, follow these steps...",
  "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
  "message_id": "770e8400-e29b-41d4-a716-446655440002",
  "sources": [
    {
      "chunk_id": "880e8400-e29b-41d4-a716-446655440003",
      "text": "The payment gateway is configured by...",
      "score": 0.92
    }
  ]
}
```

### 4. Create a Task

Tasks help you track work related to a workspace.

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Review API documentation",
    "description": "Check the REST API endpoints",
    "priority": "high",
    "status": "pending"
  }'
```

### 5. List Conversations

```bash
curl "http://localhost:8000/conversations?workspace_id=550e8400-e29b-41d4-a716-446655440000"
```

### 6. Get Conversation Messages

```bash
curl "http://localhost:8000/conversations/<conversation-id>/messages"
```

## API Endpoints Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API info |
| POST | `/workspaces` | Create workspace |
| GET | `/workspaces` | List all workspaces |
| GET | `/workspaces/{id}` | Get workspace |
| PATCH | `/workspaces/{id}` | Update workspace |
| DELETE | `/workspaces/{id}` | Delete workspace |
| POST | `/datasets` | Create dataset |
| GET | `/datasets` | List all datasets |
| GET | `/datasets/{id}` | Get dataset |
| PATCH | `/datasets/{id}` | Update dataset |
| DELETE | `/datasets/{id}` | Delete dataset |
| POST | `/chat` | Send message to RAG system |
| POST | `/conversations` | Create conversation |
| GET | `/conversations` | List conversations |
| GET | `/conversations/{id}` | Get conversation |
| GET | `/conversations/{id}/messages` | Get messages |
| POST | `/tasks` | Create task |
| GET | `/tasks` | List tasks |
| GET | `/tasks/{id}` | Get task |
| PATCH | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |

## Using the Agent Layer

The agent layer provides tool-using capabilities:

```python
from app.agent.orchestrator import AgentOrchestrator
from app.agent.context import AgentContext
from app.tools.search import SearchTool
from app.tools.filesystem import FilesystemTool

# Initialize tools
tools = [
    SearchTool(api_key="your-api-key", engine_id="your-engine-id"),
    FilesystemTool()
]

# Create orchestrator
orchestrator = AgentOrchestrator(
    llm=llm_provider,
    retriever=retrieval_pipeline,
    tools=tools
)

# Run agent
context = AgentContext(
    workspace_id="<workspace-id>",
    dataset_id="<dataset-id>"
)

answer = await orchestrator.run(
    context=context,
    query="Search for recent AI news and summarize"
)
```

## Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/unit/test_chat.py -v

# Run integration tests only
pytest tests/integration/ -v
```

## Development Commands

```bash
make lint         # Run ruff linter
make format       # Format code with ruff
make typecheck    # Run mypy type checker
make clean        # Clean cache and build artifacts
make migrations   # Create new alembic migration
make upgrade      # Apply database migrations
```

## Configuration

Edit `config/development.yaml` for local settings:

```yaml
app:
  name: "RAG Platform"
  version: "0.1.0"
  debug: true

llm:
  provider: "ollama"  # Options: ollama, openai, anthropic, gemini
  model: "llama3"
  base_url: "http://localhost:11434"

embedding:
  provider: "bge_m3"
  model_name: "BAAI/bge-m3"
  device: "cpu"

retrieval:
  dense_weight: 0.6
  bm25_weight: 0.4
  top_k: 10
  similarity_threshold: 0.7
```

## Using Different LLM Providers

### OpenAI

```bash
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o
export LLM_API_KEY=your-openai-api-key
```

### Anthropic

```bash
export LLM_PROVIDER=anthropic
export LLM_MODEL=claude-3-sonnet-20240229
export LLM_API_KEY=your-anthropic-api-key
```

### Gemini

```bash
export LLM_PROVIDER=gemini
export LLM_MODEL=gemini-pro
export LLM_API_KEY=your-gemini-api-key
```

## Production Deployment

```bash
# Build and start all services
docker compose up -d

# View logs
make docker-logs

# Stop services
make docker-down
```

## Troubleshooting

**Port already in use:**
```bash
# Change ports in docker-compose.yml or kill process
lsof -ti:8000 | xargs kill -9
```

**Database connection issues:**
```bash
# Check PostgreSQL is running
docker compose ps postgres

# View logs
docker compose logs postgres
```

**Ollama not responding:**
```bash
# Check Ollama service
curl http://localhost:11434/

# Pull a model
docker compose exec ollama ollama pull llama3
```

**Celery worker not starting:**
```bash
# Check Redis connection
redis-cli ping

# View worker logs
docker compose logs worker
```

## Project Structure

```
RAG/
├── app/
│   ├── agent/           # Agent orchestration layer
│   ├── api/             # FastAPI routes and middleware
│   ├── connectors/      # Data source connectors
│   ├── ingestion/       # Document processing pipeline
│   ├── memory/          # Conversation and task memory
│   ├── providers/       # LLM, embedding, vector store providers
│   ├── retrieval/       # Dense, BM25, hybrid retrieval
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic
│   └── tools/           # Agent tools (search, git, filesystem)
├── config/              # YAML configuration files
├── docs/                # Documentation
├── infra/               # Dockerfiles
├── tests/               # Unit and integration tests
├── docker-compose.yml   # Service orchestration
├── Makefile            # Development commands
└── .env.example        # Environment template
```

## Next Steps

1. Add documents to your dataset via the ingestion pipeline
2. Configure embedding and LLM providers for your use case
3. Explore the agent layer for complex multi-step reasoning
4. Set up authentication and authorization for production
5. Configure monitoring and logging

## Support

For issues and questions, check the documentation in `docs/` or open an issue in the repository.
