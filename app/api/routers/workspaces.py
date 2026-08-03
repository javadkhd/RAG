from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceList,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.workspace import WorkspaceService
from app.repositories.workspace import WorkspaceRepository

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def get_workspace_service(db: AsyncSession = Depends(get_db)) -> WorkspaceService:
    return WorkspaceService(repo=WorkspaceRepository(session=db))


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceResponse:
    workspace = await service.create_workspace(
        name=payload.name,
        description=payload.description,
        extra_metadata=payload.extra_metadata,
    )
    return WorkspaceResponse.model_validate(workspace)


@router.get("", response_model=list[WorkspaceList])
async def list_workspaces(
    service: WorkspaceService = Depends(get_workspace_service),
) -> list[WorkspaceList]:
    workspaces = await service.list_workspaces()
    return [WorkspaceList.model_validate(w) for w in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceResponse:
    workspace = await service.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return WorkspaceResponse.model_validate(workspace)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    payload: WorkspaceUpdate,
    service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceResponse:
    workspace = await service.update_workspace(
        workspace_id=workspace_id,
        name=payload.name,
        description=payload.description,
        extra_metadata=payload.extra_metadata,
    )
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return WorkspaceResponse.model_validate(workspace)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    service: WorkspaceService = Depends(get_workspace_service),
) -> None:
    deleted = await service.delete_workspace(workspace_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return None
