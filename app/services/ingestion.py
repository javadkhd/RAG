from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.base import Dataset


class IngestionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dataset(self, dataset_id: UUID) -> Dataset | None:
        result = await self.session.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        return result.scalar_one_or_none()

    async def ingest_dataset(self, dataset_id: UUID) -> dict[str, Any]:
        from app.connectors.markdown.loader import MarkdownConnector
        from app.ingestion.pipeline import IngestionPipeline, IngestionResult
        from app.providers.embeddings import get_embedding_provider

        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")

        connector_type = dataset.connector_type or "markdown"
        connector_config = dataset.connector_config or {}

        if connector_type == "markdown":
            path = connector_config.get("path", settings.ingestion.default_doc_path)
            connector = MarkdownConnector()
        else:
            raise ValueError(f"Unsupported connector type: {connector_type}")

        embedding_provider = get_embedding_provider()
        pipeline = IngestionPipeline(
            session=self.session,
            connector=connector,
            embedder=embedding_provider,
        )

        result: IngestionResult = await pipeline.run(
            path=path,
            dataset_id=dataset.id,
            workspace_id=dataset.workspace_id,
        )

        await self.session.commit()

        return {
            "dataset_id": str(dataset.id),
            "documents_loaded": result.documents_loaded,
            "chunks_created": result.chunks_created,
            "embeddings_generated": result.embeddings_generated,
            "errors": result.errors,
            "status": "completed" if not result.errors else "completed_with_errors",
        }
