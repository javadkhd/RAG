from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Dataset, Workspace


class DatasetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        workspace_id: UUID,
        name: str,
        description: Optional[str],
        connector_type: Optional[str],
        connector_config: Optional[dict[str, Any]],
        extra_metadata: Optional[dict[str, Any]],
    ) -> Dataset:
        dataset = Dataset(
            workspace_id=workspace_id,
            name=name,
            description=description,
            connector_type=connector_type,
            connector_config=connector_config,
            extra_metadata=extra_metadata,
        )
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)
        return dataset

    async def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        result = await self.session.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: UUID) -> list[Dataset]:
        result = await self.session.execute(
            select(Dataset)
            .where(Dataset.workspace_id == workspace_id)
            .order_by(Dataset.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[Dataset]:
        result = await self.session.execute(
            select(Dataset).order_by(Dataset.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        dataset_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        connector_type: Optional[str] = None,
        connector_config: Optional[dict[str, Any]] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Dataset]:
        dataset = await self.get_by_id(dataset_id)
        if not dataset:
            return None

        if name is not None:
            dataset.name = name
        if description is not None:
            dataset.description = description
        if connector_type is not None:
            dataset.connector_type = connector_type
        if connector_config is not None:
            dataset.connector_config = connector_config
        if extra_metadata is not None:
            dataset.extra_metadata = extra_metadata
        dataset.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(dataset)
        return dataset

    async def delete(self, dataset_id: UUID) -> bool:
        dataset = await self.get_by_id(dataset_id)
        if not dataset:
            return False
        await self.session.delete(dataset)
        await self.session.commit()
        return True

    async def count_by_workspace(self, workspace_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).where(Dataset.workspace_id == workspace_id)
        )
        return result.scalar_one()
