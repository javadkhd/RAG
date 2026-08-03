.PHONY: help dev test lint clean install migrations upgrade install-dev

help:
	@echo "RAG Platform Makefile"
	@echo ""
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install dev dependencies"
	@echo "  make dev          Start development server with hot reload"
	@echo "  make worker       Start Celery worker"
	@echo "  make test         Run tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo "  make lint         Run ruff linter"
	@echo "  make format       Format code with ruff"
	@echo "  make typecheck    Run mypy type checker"
	@echo "  make migrations   Create new alembic migration"
	@echo "  make upgrade      Apply database migrations"
	@echo "  make clean        Clean cache and build artifacts"
	@echo "  make docker-up    Start Docker services"
	@echo "  make docker-down  Stop Docker services"
	@echo "  make docker-logs  Show Docker logs"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,embeddings,reranker]"
	pre-commit install

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	celery -A app.worker.celery_app worker --loglevel=info

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=term-missing -v

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/

typecheck:
	mypy app/

migrations:
	@read -p "Migration message: " msg; \
	alembic -c config/alembic.ini revision --autogenerate -m "$$msg"

upgrade:
	alembic -c config/alembic.ini upgrade head

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	rm -rf storage/test_uploads

docker-up:
	docker compose up -d postgres redis ollama
	@echo "Waiting for services to be healthy..."
	@sleep 10
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
