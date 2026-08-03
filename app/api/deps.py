from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


async def get_workspace_or_404(
    workspace_id: str,
    db: AsyncSession,
) -> "Workspace":
    from app.models.base import Workspace
    from sqlalchemy import select

    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return workspace


async def get_dataset_or_404(
    dataset_id: str,
    db: AsyncSession,
) -> "Dataset":
    from app.models.base import Dataset
    from sqlalchemy import select

    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )
    return dataset
