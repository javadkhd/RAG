from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from app.models.base import Workspace
from app.repositories.workspace import WorkspaceRepository


class WorkspaceService:
    def __init__(self, repo: WorkspaceRepository) -> None:
        self.repo = repo

    async def create_workspace(
        self,
        name: str,
        description: Optional[str] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Workspace:
        return await self.repo.create(
            name=name,
            description=description,
            extra_metadata=extra_metadata,
        )

    async def get_workspace(self, workspace_id: UUID) -> Optional[Workspace]:
        return await self.repo.get_by_id(workspace_id)

    async def list_workspaces(self) -> list[Workspace]:
        return await self.repo.list_all()

    async def update_workspace(
        self,
        workspace_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Workspace]:
        return await self.repo.update(
            workspace_id=workspace_id,
            name=name,
            description=description,
            extra_metadata=extra_metadata,
        )

    async def delete_workspace(self, workspace_id: UUID) -> bool:
        return await self.repo.delete(workspace_id)
