from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.schemas.task import TaskCreate, TaskList, TaskResponse, TaskUpdate
from app.services.task import TaskService
from app.repositories.task import TaskRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(repo=TaskRepository(session=db))


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await service.create_task(
        workspace_id=payload.workspace_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        extra_metadata=payload.extra_metadata,
    )
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskList])
async def list_tasks(
    workspace_id: str,
    service: TaskService = Depends(get_task_service),
) -> list[TaskList]:
    tasks = await service.list_tasks(workspace_id=workspace_id)
    return [TaskList.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await service.update_task(
        task_id=task_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        extra_metadata=payload.extra_metadata,
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> None:
    deleted = await service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return None
