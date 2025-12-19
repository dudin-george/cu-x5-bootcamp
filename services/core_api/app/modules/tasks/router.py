"""Task API router."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentRecruiterId
from app.modules.recruiters.service import RecruiterService
from app.modules.tasks.schemas import (
    AssignTaskRequest,
    CompleteTaskRequest,
    RecruiterTaskCreate,
    RecruiterTaskResponse,
    RejectTaskRequest,
    TasksListResponse,
    UpdateTaskStatusRequest,
)
from app.modules.tasks.service import TaskService
from app.shared.enums import TaskStatus

router = APIRouter()


def format_task_response(task) -> RecruiterTaskResponse:
    """Format task for response (simplified for kanban cards).

    Args:
        task: RecruiterTask model.

    Returns:
        RecruiterTaskResponse: Formatted task.
    """
    return RecruiterTaskResponse(
        id=task.id,
        task_type_name=task.task_type.name,
        status=task.status,
        title=task.title,
        description=task.description,
        context=task.context,
    )


@router.get(
    "/",
    response_model=TasksListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all tasks for current recruiter",
    description="Получить все задачи для текущего рекрутера: BACKLOG (все) + задачи назначенные на этого рекрутера.",
)
async def get_tasks(
    recruiter_id: CurrentRecruiterId,
    db: AsyncSession = Depends(get_db),
) -> TasksListResponse:
    """Get all tasks for current recruiter.

    Returns all tasks in BACKLOG + all tasks assigned to current recruiter
    (regardless of status).

    Args:
        recruiter_id: Current recruiter ID from Ory session.
        db: Database session.

    Returns:
        TasksListResponse: List of tasks.
    """
    # Get all BACKLOG tasks (available to all recruiters)
    backlog_tasks = await TaskService.get_tasks_by_status(
        db, TaskStatus.BACKLOG, None
    )

    # Get all tasks assigned to this recruiter (IN_PROGRESS, COMPLETED, REJECTED)
    assigned_tasks_in_progress = await TaskService.get_tasks_by_status(
        db, TaskStatus.IN_PROGRESS, recruiter_id
    )
    assigned_tasks_completed = await TaskService.get_tasks_by_status(
        db, TaskStatus.COMPLETED, recruiter_id
    )
    assigned_tasks_rejected = await TaskService.get_tasks_by_status(
        db, TaskStatus.REJECTED, recruiter_id
    )

    # Combine all tasks
    all_tasks = (
        backlog_tasks
        + assigned_tasks_in_progress
        + assigned_tasks_completed
        + assigned_tasks_rejected
    )

    return TasksListResponse(
        tasks=[format_task_response(task) for task in all_tasks]
    )


@router.post(
    "/",
    response_model=RecruiterTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Создать новую задачу (для тестирования, в будущем будет создаваться автоматически)",
)
async def create_task(
    data: RecruiterTaskCreate,
    db: AsyncSession = Depends(get_db),
) -> RecruiterTaskResponse:
    """Create task.

    Args:
        data: Task creation data.
        db: Database session.

    Returns:
        RecruiterTaskResponse: Created task.
    """
    task = await TaskService.create_task(db, data)
    # Reload with relationships
    task = await TaskService.get_task_by_id(db, task.id)
    return format_task_response(task)


@router.post(
    "/{task_id}/assign",
    response_model=RecruiterTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign task to recruiter",
    description="Взять задачу из общего пула в исполнение (POOL -> IN_PROGRESS)",
)
async def assign_task(
    task_id: uuid.UUID,
    request: AssignTaskRequest,
    db: AsyncSession = Depends(get_db),
) -> RecruiterTaskResponse:
    """Assign task to recruiter.

    Args:
        task_id: Task UUID.
        request: Assignment request with recruiter_id.
        db: Database session.

    Returns:
        RecruiterTaskResponse: Updated task.

    Raises:
        HTTPException: If task not found, not in POOL, or recruiter not found.
    """
    # Get task
    task = await TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Check task is in BACKLOG
    if task.status != TaskStatus.BACKLOG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task must be in BACKLOG status, currently {task.status}",
        )

    # Check recruiter exists
    recruiter = await RecruiterService.get_recruiter_by_id(db, request.recruiter_id)
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recruiter {request.recruiter_id} not found",
        )

    # Assign task
    task = await TaskService.assign_task_to_recruiter(db, task, request.recruiter_id)
    # Reload with relationships
    task = await TaskService.get_task_by_id(db, task.id)
    return format_task_response(task)


@router.post(
    "/{task_id}/complete",
    response_model=RecruiterTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete task",
    description="Выполнить задачу (IN_PROGRESS -> COMPLETED)",
)
async def complete_task(
    task_id: uuid.UUID,
    request: CompleteTaskRequest,
    db: AsyncSession = Depends(get_db),
) -> RecruiterTaskResponse:
    """Complete task.

    Args:
        task_id: Task UUID.
        request: Complete request (currently empty).
        db: Database session.

    Returns:
        RecruiterTaskResponse: Updated task.

    Raises:
        HTTPException: If task not found or not in IN_PROGRESS.
    """
    # Get task
    task = await TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Check task is in IN_PROGRESS
    if task.status != TaskStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task must be in IN_PROGRESS status, currently {task.status}",
        )

    # Complete task
    task = await TaskService.complete_task(db, task)
    # Reload with relationships
    task = await TaskService.get_task_by_id(db, task.id)
    return format_task_response(task)


@router.post(
    "/{task_id}/reject",
    response_model=RecruiterTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject task",
    description="Отклонить задачу (IN_PROGRESS -> REJECTED)",
)
async def reject_task(
    task_id: uuid.UUID,
    request: RejectTaskRequest,
    db: AsyncSession = Depends(get_db),
) -> RecruiterTaskResponse:
    """Reject task.

    Args:
        task_id: Task UUID.
        request: Reject request (currently empty).
        db: Database session.

    Returns:
        RecruiterTaskResponse: Updated task.

    Raises:
        HTTPException: If task not found or not in IN_PROGRESS.
    """
    # Get task
    task = await TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Check task is in IN_PROGRESS
    if task.status != TaskStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task must be in IN_PROGRESS status, currently {task.status}",
        )

    # Reject task
    task = await TaskService.reject_task(db, task)
    # Reload with relationships
    task = await TaskService.get_task_by_id(db, task.id)
    return format_task_response(task)


@router.patch(
    "/{task_id}",
    response_model=RecruiterTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task status",
    description="Обновить статус задачи. Если новый статус != BACKLOG, задача назначается на текущего рекрутера. Если BACKLOG - задача освобождается.",
)
async def update_task_status(
    task_id: uuid.UUID,
    request: UpdateTaskStatusRequest,
    recruiter_id: CurrentRecruiterId,
    db: AsyncSession = Depends(get_db),
) -> RecruiterTaskResponse:
    """Update task status.

    Logic:
    - If new_status != BACKLOG: assign task to current recruiter
    - If new_status == BACKLOG: unassign task (assigned_to = None)
    - If task is vacancy_approval and new_status is COMPLETED: activate vacancy
    - If task is vacancy_approval and new_status is REJECTED: abort vacancy

    Args:
        task_id: Task UUID.
        request: Update request with new status.
        recruiter_id: Current recruiter ID from Ory session.
        db: Database session.

    Returns:
        RecruiterTaskResponse: Updated task.

    Raises:
        HTTPException: If task not found.
    """
    # Get task
    task = await TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Update task status
    task = await TaskService.update_task_status(db, task, request.status, recruiter_id)

    # Reload with relationships
    task = await TaskService.get_task_by_id(db, task.id)
    return format_task_response(task)
