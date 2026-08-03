from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from app.models.base import Task
from app.repositories.task import TaskRepository


class TaskService:
    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    async def create_task(
        self,
        workspace_id: UUID,
        title: str,
        description: Optional[str] = None,
        status: str = "pending",
        priority: str = "medium",
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Task:
        return await self.repo.create(
            workspace_id=workspace_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            extra_metadata=extra_metadata,
        )

    async def get_task(self, task_id: UUID) -> Optional[Task]:
        return await self.repo.get_by_id(task_id)

    async def list_tasks(self, workspace_id: UUID) -> list[Task]:
        return await self.repo.list_by_workspace(workspace_id)

    async def update_task(
        self,
        task_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        extra_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Task]:
        return await self.repo.update(
            task_id=task_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            extra_metadata=extra_metadata,
        )

    async def delete_task(self, task_id: UUID) -> bool:
        return await self.repo.delete(task_id)
