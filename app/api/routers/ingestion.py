from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_dataset_or_404, get_db

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/{dataset_id}/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    dataset = await get_dataset_or_404(str(dataset_id), db)

    if dataset.connector_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset has no connector_type configured",
        )

    from app.worker.tasks import ingest_dataset as ingest_dataset_task

    task = ingest_dataset_task.delay(str(dataset_id))

    return {
        "dataset_id": str(dataset_id),
        "task_id": task.id,
        "status": "queued",
    }
