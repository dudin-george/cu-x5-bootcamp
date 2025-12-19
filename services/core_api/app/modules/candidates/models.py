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

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Telegram username"
    )

    surname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Фамилия кандидата"
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя кандидата"
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Номер телефона"
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Email адрес"
    )

    resume_link: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Ссылка на резюме (PDF)"
    )

    priority1: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Первый приоритет трека (название)"
    )

    priority2: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Второй приоритет трека (название)"
    )

    course: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Курс обучения (например '4 курс')"
    )

    university: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Название университета"
    )

    specialty: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Специальность"
    )

    employment_hours: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Количество часов для работы"
    )

    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Город"
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Источник (откуда узнал о стажировке)"
    )

    birth_year: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Год рождения"
    )

    citizenship: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Гражданство"
    )

    tech_stack: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Технологический стек"
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
        return f"<Candidate(id={self.id}, surname={self.surname}, name={self.name})>"
