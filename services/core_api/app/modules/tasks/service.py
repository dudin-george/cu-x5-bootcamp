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
            status=TaskStatus.BACKLOG,  # Всегда создается в бэклоге
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
        recruiter_id: uuid.UUID | None = None,
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
        if status != TaskStatus.BACKLOG and recruiter_id is not None:
            query = query.where(RecruiterTask.assigned_to == recruiter_id)

        query = query.order_by(RecruiterTask.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def assign_task_to_recruiter(
        db: AsyncSession,
        task: RecruiterTask,
        recruiter_id: uuid.UUID,
    ) -> RecruiterTask:
        """Assign task to recruiter (BACKLOG -> IN_PROGRESS).

        Args:
            db: Database session.
            task: Task to assign.
            recruiter_id: Recruiter ID (Ory identity UUID).

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

        If task is vacancy_approval, activates the vacancy.

        Args:
            db: Database session.
            task: Task to complete.

        Returns:
            RecruiterTask: Updated task.
        """
        now = datetime.now(timezone.utc)
        task.status = TaskStatus.COMPLETED
        task.completed_at = now

        # Load task_type if not already loaded
        if not hasattr(task, "task_type") or task.task_type is None:
            await db.refresh(task, ["task_type"])

        # Handle vacancy approval automation
        if task.task_type.code == "vacancy_approval" and "vacancy_id" in task.context:
            from app.modules.vacancies.models import Vacancy
            from app.shared.enums import VacancyStatus

            vacancy_id = task.context["vacancy_id"]
            vacancy_result = await db.execute(
                select(Vacancy).where(Vacancy.id == vacancy_id)
            )
            vacancy = vacancy_result.scalar_one_or_none()
            if vacancy:
                vacancy.status = VacancyStatus.ACTIVE

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def reject_task(
        db: AsyncSession,
        task: RecruiterTask,
    ) -> RecruiterTask:
        """Reject task (IN_PROGRESS -> REJECTED).

        If task is vacancy_approval, aborts the vacancy.

        Args:
            db: Database session.
            task: Task to reject.

        Returns:
            RecruiterTask: Updated task.
        """
        now = datetime.now(timezone.utc)
        task.status = TaskStatus.REJECTED
        task.completed_at = now

        # Load task_type if not already loaded
        if not hasattr(task, "task_type") or task.task_type is None:
            await db.refresh(task, ["task_type"])

        # Handle vacancy approval automation
        if task.task_type.code == "vacancy_approval" and "vacancy_id" in task.context:
            from app.modules.vacancies.models import Vacancy
            from app.shared.enums import VacancyStatus

            vacancy_id = task.context["vacancy_id"]
            vacancy_result = await db.execute(
                select(Vacancy).where(Vacancy.id == vacancy_id)
            )
            vacancy = vacancy_result.scalar_one_or_none()
            if vacancy:
                vacancy.status = VacancyStatus.ABORTED

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def create_vacancy_approval_task(
        db: AsyncSession,
        vacancy_id: int,
        vacancy_description: str,
        track_name: str,
        hiring_manager_name: str,
    ) -> RecruiterTask:
        """Create vacancy approval task automatically when vacancy is created.

        Args:
            db: Database session.
            vacancy_id: Vacancy ID.
            vacancy_description: Vacancy description.
            track_name: Track name.
            hiring_manager_name: Hiring manager full name.

        Returns:
            RecruiterTask: Created task.
        """
        # Get vacancy_approval task type by code
        task_type = await TaskTypeService.get_task_type_by_code(db, "vacancy_approval")
        if not task_type:
            raise ValueError("Task type 'vacancy_approval' not found. Please seed task_types table.")

        task = RecruiterTask(
            task_type_id=task_type.id,
            title=f"Утверждение вакансии #{vacancy_id} ({track_name})",
            description=f"Требуется утвердить вакансию для трека '{track_name}', созданную нанимающим менеджером {hiring_manager_name}.",
            context={
                "vacancy_id": vacancy_id,
                "track_name": track_name,
                "hiring_manager_name": hiring_manager_name,
                "vacancy_description": vacancy_description,
            },
            status=TaskStatus.BACKLOG,
            assigned_to=None,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def update_task_status(
        db: AsyncSession,
        task: RecruiterTask,
        new_status: TaskStatus,
        recruiter_id: uuid.UUID,
    ) -> RecruiterTask:
        """Update task status (PATCH endpoint logic).

        Rules:
        - If new_status != BACKLOG: assign task to recruiter
        - If new_status == BACKLOG: unassign task (assigned_to = None)
        - If task is vacancy_approval and new_status is COMPLETED: activate vacancy
        - If task is vacancy_approval and new_status is REJECTED: abort vacancy

        Args:
            db: Database session.
            task: Task to update.
            new_status: New status.
            recruiter_id: Recruiter ID from Ory session.

        Returns:
            RecruiterTask: Updated task.
        """
        now = datetime.now(timezone.utc)
        task.status = new_status

        # Assign/unassign logic
        if new_status == TaskStatus.BACKLOG:
            task.assigned_to = None
            task.completed_at = None
        else:
            task.assigned_to = recruiter_id

        # Set completed_at for terminal statuses
        if new_status in (TaskStatus.COMPLETED, TaskStatus.REJECTED):
            task.completed_at = now

        # Load task_type if not already loaded
        if not hasattr(task, "task_type") or task.task_type is None:
            await db.refresh(task, ["task_type"])

        # Handle vacancy approval automation
        if task.task_type.code == "vacancy_approval" and "vacancy_id" in task.context:
            from app.modules.vacancies.models import Vacancy
            from app.shared.enums import VacancyStatus

            vacancy_id = task.context["vacancy_id"]
            vacancy_result = await db.execute(
                select(Vacancy).where(Vacancy.id == vacancy_id)
            )
            vacancy = vacancy_result.scalar_one_or_none()

            if vacancy:
                if new_status == TaskStatus.COMPLETED:
                    vacancy.status = VacancyStatus.ACTIVE
                elif new_status == TaskStatus.REJECTED:
                    vacancy.status = VacancyStatus.ABORTED

        await db.commit()
        await db.refresh(task)
        return task
