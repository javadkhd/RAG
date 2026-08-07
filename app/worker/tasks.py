import asyncio
import logging

from celery import shared_task

from app.db.session import db
from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)

_db_initialized = False


def _ensure_db_initialized() -> None:
    global _db_initialized
    if not _db_initialized:
        db.init()
        _db_initialized = True


@shared_task(bind=True, name="app.worker.tasks.ingest_dataset")
def ingest_dataset(self, dataset_id: str) -> dict:
    _ensure_db_initialized()

    async def _run() -> dict:
        async with db.async_session_factory() as session:
            service = IngestionService(session=session)
            return await service.ingest_dataset(dataset_id)

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("Ingestion failed for dataset %s: %s", dataset_id, exc)
        raise


@shared_task(bind=True, name="app.worker.tasks.generate_embeddings")
def generate_embeddings(self, dataset_id: str) -> dict:
    return {"dataset_id": dataset_id, "status": "queued"}
