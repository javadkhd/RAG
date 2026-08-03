from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Workspace


class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, name: str, description: Optional[str], extra_metadata: Optional[dict[str, Any]]) -> Workspace:
        workspace = Workspace(
            name=name,
            description=description,
            extra_metadata=extra_metadata,
        )
        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: UUID) -> Optional[Workspace]:
        result = await self.session.execute(
            select(Workspace).where(Workspace.id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Workspace]:
        result = await self.session.execute(
            select(Workspace).order_by(Workspace.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        workspace_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Workspace]:
        workspace = await self.get_by_id(workspace_id)
        if not workspace:
            return None

        if name is not None:
            workspace.name = name
        if description is not None:
            workspace.description = description
        if extra_metadata is not None:
            workspace.extra_metadata = extra_metadata
        workspace.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def delete(self, workspace_id: UUID) -> bool:
        workspace = await self.get_by_id(workspace_id)
        if not workspace:
            return False
        await self.session.delete(workspace)
        await self.session.commit()
        return True
