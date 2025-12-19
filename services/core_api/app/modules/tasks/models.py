"""Task models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums import TaskStatus


class TaskType(Base):
    """Task type model - типы задач для рекрутеров."""

    __tablename__ = "task_types"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID типа задачи",
    )

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Код типа задачи (vacancy_approval, send_offer, etc.)",
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Название типа задачи",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Описание типа задачи",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активен ли тип задачи",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Дата создания",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Дата последнего обновления",
    )

    # Relationships
    tasks: Mapped[list["RecruiterTask"]] = relationship(
        "RecruiterTask",
        back_populates="task_type",
    )

    def __repr__(self) -> str:
        """String representation.

        Returns:
            str: TaskType representation.
        """
        return f"<TaskType(code={self.code}, name={self.name})>"


class RecruiterTask(Base):
    """Recruiter task model - задачи для рекрутеров в канбане."""

    __tablename__ = "recruiter_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="UUID задачи",
    )

    # Тип задачи
    task_type_id: Mapped[int] = mapped_column(
        ForeignKey("task_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID типа задачи",
    )

    # Статус (колонка в канбане)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status", create_type=True),
        default=TaskStatus.BACKLOG,
        nullable=False,
        index=True,
        comment="Статус задачи: BACKLOG, IN_PROGRESS, COMPLETED, REJECTED",
    )

    # Назначение рекрутеру (None = в бэклоге)
    # Note: Не связано FK, так как рекрутеры хранятся в Ory Kratos
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Ory Identity ID рекрутера, которому назначена задача (NULL = backlog)",
    )

    # Контекст задачи (гибкое JSONB поле)
    context: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Контекст задачи в формате JSON (например, {vacancy_id: 123})",
    )

    # Мета-информация
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Заголовок задачи",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Описание задачи",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Дата создания задачи",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Дата последнего обновления",
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата завершения задачи",
    )

    # Relationships
    task_type: Mapped["TaskType"] = relationship(
        "TaskType",
        back_populates="tasks",
    )

    def __repr__(self) -> str:
        """String representation.

        Returns:
            str: RecruiterTask representation.
        """
        return f"<RecruiterTask(id={self.id}, title={self.title}, status={self.status})>"
