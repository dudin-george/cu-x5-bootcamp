"""Hiring Managers module database models."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.vacancies.models import Vacancy


class HiringManager(Base):
    """Hiring Manager model representing managers who create vacancies."""

    __tablename__ = "hiring_managers"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Уникальный UUID менеджера"
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
        comment="Telegram user ID"
    )

    calendly_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="ID в системе Calendly"
    )

    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя"
    )

    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Фамилия"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда профиль был создан"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда профиль последний раз обновлялся"
    )

    # Relationships
    vacancies: Mapped[list["Vacancy"]] = relationship(
        "Vacancy",
        back_populates="hiring_manager",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of HiringManager.

        Returns:
            str: HiringManager representation.
        """
        return f"<HiringManager(id={self.id}, name={self.first_name} {self.last_name})>"
