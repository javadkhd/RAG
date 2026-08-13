FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY README.md ./
COPY app/ ./app/
COPY config/ ./config/
COPY migrations/ ./migrations/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install .

FROM base AS runtime-base

ENV HOME=/home/appuser
RUN mkdir -p /app/data/huggingface /app/storage/uploads \
    && groupadd -g 999 appgroup \
    && useradd -u 999 -g 999 --create-home --home-dir /home/appuser --shell /bin/sh appuser \
    && chown -R appuser:appgroup /app

COPY --from=builder /install /usr/local
COPY --chown=appuser:appgroup . /app

USER appuser

FROM runtime-base AS runtime-api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

FROM runtime-base AS runtime-worker

CMD ["celery", "-A", "app.worker.celery_app", "worker", "--loglevel=info", "--concurrency=1"]