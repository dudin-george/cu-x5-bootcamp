"""Task admin router - temporary endpoints for seeding data."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.tasks.models import TaskType
from app.modules.tasks.schemas import TaskTypeCreate, TaskTypeResponse
from app.modules.tasks.service import TaskTypeService

router = APIRouter()


@router.post(
    "/task-types",
    response_model=TaskTypeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task type",
    description="Создать новый тип задачи (временная ручка для seed данных)",
)
async def create_task_type(
    data: TaskTypeCreate,
    db: AsyncSession = Depends(get_db),
) -> TaskTypeResponse:
    """Create task type.

    Args:
        data: Task type creation data.
        db: Database session.

    Returns:
        TaskTypeResponse: Created task type.
    """
    # Check if code already exists
    existing = await TaskTypeService.get_task_type_by_code(db, data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task type with code '{data.code}' already exists",
        )

    task_type = TaskType(
        code=data.code,
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    db.add(task_type)
    await db.commit()
    await db.refresh(task_type)

    return TaskTypeResponse.model_validate(task_type)


@router.get(
    "/task-types",
    response_model=list[TaskTypeResponse],
    status_code=status.HTTP_200_OK,
    summary="List task types",
    description="Получить все типы задач",
)
async def list_task_types(
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[TaskTypeResponse]:
    """List all task types.

    Args:
        is_active: Filter by active status.
        db: Database session.

    Returns:
        list[TaskTypeResponse]: List of task types.
    """
    task_types = await TaskTypeService.get_all_task_types(db, is_active)
    return [TaskTypeResponse.model_validate(tt) for tt in task_types]
