"""Recruiter models."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.tasks.models import RecruiterTask


class Recruiter(Base):
    """Recruiter model."""

    __tablename__ = "recruiters"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        comment="Ory Identity ID рекрутера",
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="ФИО рекрутера",
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
    assigned_tasks: Mapped[list["RecruiterTask"]] = relationship(
        "RecruiterTask",
        back_populates="recruiter",
    )

    def __repr__(self) -> str:
        """String representation.

        Returns:
            str: Recruiter representation.
        """
        return f"<Recruiter(id={self.id}, full_name={self.full_name})>"
