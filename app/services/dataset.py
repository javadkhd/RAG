from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from app.models.base import Dataset
from app.repositories.dataset import DatasetRepository


class DatasetService:
    def __init__(self, repo: DatasetRepository) -> None:
        self.repo = repo

    async def create_dataset(
        self,
        workspace_id: UUID,
        name: str,
        description: Optional[str] = None,
        connector_type: Optional[str] = None,
        connector_config: Optional[dict[str, Any]] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Dataset:
        return await self.repo.create(
            workspace_id=workspace_id,
            name=name,
            description=description,
            connector_type=connector_type,
            connector_config=connector_config,
            extra_metadata=extra_metadata,
        )

    async def get_dataset(self, dataset_id: UUID) -> Optional[Dataset]:
        return await self.repo.get_by_id(dataset_id)

    async def list_datasets(self, workspace_id: Optional[UUID] = None) -> list[Dataset]:
        if workspace_id is not None:
            return await self.repo.list_by_workspace(workspace_id)
        return await self.repo.list_all()

    async def update_dataset(
        self,
        dataset_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        connector_type: Optional[str] = None,
        connector_config: Optional[dict[str, Any]] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Dataset]:
        return await self.repo.update(
            dataset_id=dataset_id,
            name=name,
            description=description,
            connector_type=connector_type,
            connector_config=connector_config,
            extra_metadata=extra_metadata,
        )

    async def delete_dataset(self, dataset_id: UUID) -> bool:
        return await self.repo.delete(dataset_id)
