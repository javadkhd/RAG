from celery import Celery

from app.config import settings

celery_app = Celery(
    "rag_platform",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.worker.task_time_limit,
    task_soft_time_limit=settings.worker.task_soft_time_limit,
    worker_prefetch_multiplier=settings.worker.worker_prefetch_multiplier,
    worker_max_tasks_per_child=1000,
)
