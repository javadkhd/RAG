from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Task


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        workspace_id: UUID,
        title: str,
        description: Optional[str],
        status: str,
        priority: str,
        extra_metadata: Optional[dict[str, Any]],
    ) -> Task:
        task = Task(
            workspace_id=workspace_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            extra_metadata=extra_metadata,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: UUID) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .where(Task.workspace_id == workspace_id)
            .order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[Task]:
        result = await self.session.execute(
            select(Task).order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        task_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if extra_metadata is not None:
            task.extra_metadata = extra_metadata
        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: UUID) -> bool:
        task = await self.get_by_id(task_id)
        if not task:
            return False
        await self.session.delete(task)
        await self.session.commit()
        return True

    async def count_by_workspace(self, workspace_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).where(Task.workspace_id == workspace_id)
        )
        return result.scalar_one()
