from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.schemas.dataset import (
    DatasetCreate,
    DatasetList,
    DatasetResponse,
    DatasetUpdate,
)
from app.services.dataset import DatasetService
from app.repositories.dataset import DatasetRepository

router = APIRouter(prefix="/datasets", tags=["datasets"])


def get_dataset_service(db: AsyncSession = Depends(get_db)) -> DatasetService:
    return DatasetService(repo=DatasetRepository(session=db))


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    payload: DatasetCreate,
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetResponse:
    dataset = await service.create_dataset(
        workspace_id=payload.workspace_id,
        name=payload.name,
        description=payload.description,
        connector_type=payload.connector_type,
        connector_config=payload.connector_config,
        extra_metadata=payload.extra_metadata,
    )
    return DatasetResponse.model_validate(dataset)


@router.get("", response_model=list[DatasetList])
async def list_datasets(
    workspace_id: str | None = Query(None),
    service: DatasetService = Depends(get_dataset_service),
) -> list[DatasetList]:
    datasets = await service.list_datasets(workspace_id=workspace_id)
    return [DatasetList.model_validate(d) for d in datasets]


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetResponse:
    dataset = await service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )
    return DatasetResponse.model_validate(dataset)


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    payload: DatasetUpdate,
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetResponse:
    dataset = await service.update_dataset(
        dataset_id=dataset_id,
        name=payload.name,
        description=payload.description,
        connector_type=payload.connector_type,
        connector_config=payload.connector_config,
        extra_metadata=payload.extra_metadata,
    )
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )
    return DatasetResponse.model_validate(dataset)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    service: DatasetService = Depends(get_dataset_service),
) -> None:
    deleted = await service.delete_dataset(dataset_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )
    return None
