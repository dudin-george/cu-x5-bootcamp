"""Task service layer."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.recruiters.models import Recruiter
from app.modules.tasks.models import RecruiterTask, TaskType
from app.modules.tasks.schemas import RecruiterTaskCreate
from app.shared.enums import TaskStatus


class TaskTypeService:
    """Service for managing task types."""

    @staticmethod
    async def get_task_type_by_code(
        db: AsyncSession,
        code: str,
    ) -> TaskType | None:
        """Get task type by code.

        Args:
            db: Database session.
            code: Task type code.

        Returns:
            TaskType | None: Task type if found.
        """
        result = await db.execute(
            select(TaskType).where(TaskType.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_task_types(
        db: AsyncSession,
        is_active: bool | None = None,
    ) -> list[TaskType]:
        """Get all task types.

        Args:
            db: Database session.
            is_active: Filter by active status.

        Returns:
            list[TaskType]: List of task types.
        """
        query = select(TaskType)
        if is_active is not None:
            query = query.where(TaskType.is_active == is_active)

        result = await db.execute(query.order_by(TaskType.name))
        return list(result.scalars().all())


class TaskService:
    """Service for managing recruiter tasks."""

    @staticmethod
    async def create_task(
        db: AsyncSession,
        data: RecruiterTaskCreate,
    ) -> RecruiterTask:
        """Create a new task.

        Args:
            db: Database session.
            data: Task creation data.

        Returns:
            RecruiterTask: Created task.
        """
        task = RecruiterTask(
            task_type_id=data.task_type_id,
            title=data.title,
            description=data.description,
            context=data.context,
            status=TaskStatus.POOL,  # Всегда создается в общем пуле
            assigned_to=None,  # Изначально не назначена
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_task_by_id(
        db: AsyncSession,
        task_id: uuid.UUID,
    ) -> RecruiterTask | None:
        """Get task by ID with relationships.

        Args:
            db: Database session.
            task_id: Task UUID.

        Returns:
            RecruiterTask | None: Task if found.
        """
        result = await db.execute(
            select(RecruiterTask)
            .options(
                joinedload(RecruiterTask.task_type),
                joinedload(RecruiterTask.recruiter),
            )
            .where(RecruiterTask.id == task_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tasks_by_status(
        db: AsyncSession,
        status: TaskStatus,
        recruiter_id: int | None = None,
    ) -> list[RecruiterTask]:
        """Get tasks by status.

        Args:
            db: Database session.
            status: Task status.
            recruiter_id: Filter by recruiter (for IN_PROGRESS, COMPLETED, REJECTED).

        Returns:
            list[RecruiterTask]: List of tasks.
        """
        query = (
            select(RecruiterTask)
            .options(
                joinedload(RecruiterTask.task_type),
                joinedload(RecruiterTask.recruiter),
            )
            .where(RecruiterTask.status == status)
        )

        # Для статусов кроме POOL фильтруем по рекрутеру
        if status != TaskStatus.POOL and recruiter_id is not None:
            query = query.where(RecruiterTask.assigned_to == recruiter_id)

        query = query.order_by(RecruiterTask.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def assign_task_to_recruiter(
        db: AsyncSession,
        task: RecruiterTask,
        recruiter_id: int,
    ) -> RecruiterTask:
        """Assign task to recruiter (POOL -> IN_PROGRESS).

        Args:
            db: Database session.
            task: Task to assign.
            recruiter_id: Recruiter ID.

        Returns:
            RecruiterTask: Updated task.
        """
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_to = recruiter_id
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def complete_task(
        db: AsyncSession,
        task: RecruiterTask,
    ) -> RecruiterTask:
        """Complete task (IN_PROGRESS -> COMPLETED).

        Args:
            db: Database session.
            task: Task to complete.

        Returns:
            RecruiterTask: Updated task.
        """
        now = datetime.now(timezone.utc)
        task.status = TaskStatus.COMPLETED
        task.completed_at = now
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def reject_task(
        db: AsyncSession,
        task: RecruiterTask,
    ) -> RecruiterTask:
        """Reject task (IN_PROGRESS -> REJECTED).

        Args:
            db: Database session.
            task: Task to reject.

        Returns:
            RecruiterTask: Updated task.
        """
        now = datetime.now(timezone.utc)
        task.status = TaskStatus.REJECTED
        task.completed_at = now
        await db.commit()
        await db.refresh(task)
        return task
