import asyncio
import logging

from celery import shared_task

from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="app.worker.tasks.ingest_dataset")
def ingest_dataset(self, dataset_id: str) -> dict:
    async def _run() -> dict:
        from app.db.session import create_worker_session_factory

        session_factory, engine = create_worker_session_factory()
        try:
            async with session_factory() as session:
                service = IngestionService(session=session)
                return await service.ingest_dataset(dataset_id)
        finally:
            await engine.dispose()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("Ingestion failed for dataset %s: %s", dataset_id, exc)
        raise


@shared_task(bind=True, name="app.worker.tasks.generate_embeddings")
def generate_embeddings(self, dataset_id: str) -> dict:
    async def _run() -> dict:
        from uuid import UUID

        from sqlalchemy import select

        from app.db.session import create_worker_session_factory
        from app.models.base import Dataset

        session_factory, engine = create_worker_session_factory()
        try:
            async with session_factory() as session:
                result = await session.execute(
                    select(Dataset).where(Dataset.id == UUID(dataset_id))
                )
                dataset = result.scalar_one_or_none()
                if not dataset:
                    return {
                        "dataset_id": dataset_id,
                        "status": "error",
                        "error": "Dataset not found",
                    }
                return {"dataset_id": dataset_id, "status": "queued"}
        finally:
            await engine.dispose()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("Embedding generation failed for dataset %s: %s", dataset_id, exc)
        raise
