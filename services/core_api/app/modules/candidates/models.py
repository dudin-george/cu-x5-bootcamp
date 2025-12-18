"""Candidates module database models."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.vacancies.models import CandidatePool


class Candidate(Base):
    """Candidate profile model."""

    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Уникальный UUID кандидата"
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
        comment="Telegram user ID"
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Полное имя кандидата"
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Номер телефона"
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Местоположение (город, страна)"
    )

    preferred_tracks: Mapped[list[int]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Список ID треков в порядке приоритета"
    )

    university: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Название университета"
    )

    course: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Курс обучения (1-6)"
    )

    achievements: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Достижения кандидата (олимпиады, проекты, etc.)"
    )

    domains: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Области интересов/доменов (ML, Web, Mobile, etc.)"
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
    pools: Mapped[list["CandidatePool"]] = relationship(
        "CandidatePool",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Candidate.

        Returns:
            str: Candidate representation.
        """
        return f"<Candidate(id={self.id}, full_name={self.full_name})>"
