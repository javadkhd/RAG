.PHONY: help dev test lint clean install migrations upgrade install-dev docker-up docker-down docker-logs docker-build docker-build-api docker-build-worker docker-rebuild docker-clean docker-prune

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
	@echo "  make docker-up      Start Docker services"
	@echo "  make docker-down    Stop Docker services"
	@echo "  make docker-logs    Show Docker logs"
	@echo "  make docker-build   Build all Docker images"
	@echo "  make docker-build-api   Build API image only"
	@echo "  make docker-build-worker  Build Worker image only"
	@echo "  make docker-rebuild Rebuild images with no cache"
	@echo "  make docker-clean   Remove containers and images"
	@echo "  make docker-prune   Remove unused Docker resources"


PYTHON := python3


install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev,embeddings,reranker]"
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
	$(PYTHON) -m alembic -c config/alembic.ini revision --autogenerate -m "$$msg"

upgrade:
	$(PYTHON) -m alembic -c config/alembic.ini upgrade head
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

docker-build:
	docker compose build

docker-build-api:
	docker compose build --target runtime-api api

docker-build-worker:
	docker compose build --target runtime-worker worker

docker-rebuild:
	docker compose build --no-cache

docker-clean:
	docker compose down -v --rmi local

docker-prune:
	docker system prune -f --volumes
