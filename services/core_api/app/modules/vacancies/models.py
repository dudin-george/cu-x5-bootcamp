"""Vacancies module database models."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums import CandidatePoolStatus, VacancyStatus

if TYPE_CHECKING:
    from app.modules.candidates.models import Candidate
    from app.modules.hiring_managers.models import HiringManager


class Track(Base):
    """Track (direction) model representing internship programs."""

    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный ID трека"
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Название трека (например, 'Python Backend', 'Frontend')"
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Описание трека"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Трек активен и доступен для подачи заявок"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда трек был создан"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда трек последний раз обновлялся"
    )

    # Relationships
    vacancies: Mapped[list["Vacancy"]] = relationship(
        "Vacancy",
        back_populates="track",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Track.

        Returns:
            str: Track representation.
        """
        return f"<Track(id={self.id}, name={self.name})>"


class Vacancy(Base):
    """Vacancy model representing open positions."""

    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный ID вакансии"
    )

    track_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tracks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на трек"
    )

    hiring_manager_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hiring_managers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на hiring manager который создал вакансию"
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Описание позиции"
    )

    status: Mapped[VacancyStatus] = mapped_column(
        Enum(VacancyStatus, name="vacancy_status"),
        default=VacancyStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Статус вакансии: draft, active, aborted"
    )

    next_interview_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата ближайшего собеседования"
    )

    next_interview_link: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Ссылка на собеседование (Calendly/Meet)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда вакансия была создана"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда вакансия последний раз обновлялась"
    )

    # Relationships
    track: Mapped["Track"] = relationship(
        "Track",
        back_populates="vacancies",
    )

    hiring_manager: Mapped["HiringManager"] = relationship(
        "HiringManager",
        back_populates="vacancies",
    )

    candidate_pools: Mapped[list["CandidatePool"]] = relationship(
        "CandidatePool",
        back_populates="vacancy",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Vacancy.

        Returns:
            str: Vacancy representation.
        """
        return f"<Vacancy(id={self.id}, track_id={self.track_id}, status={self.status.value})>"


class CandidatePool(Base):
    """Candidate pool model - журнал движения кандидата по воронке конкретной вакансии."""

    __tablename__ = "candidate_pools"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Уникальный UUID записи в пуле"
    )

    vacancy_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на вакансию"
    )

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на кандидата"
    )

    status: Mapped[CandidatePoolStatus] = mapped_column(
        Enum(CandidatePoolStatus, name="candidate_pool_status"),
        nullable=False,
        index=True,
        comment="Текущий статус кандидата в воронке"
    )

    interview_scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата и время назначенного интервью"
    )

    interview_link: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Ссылка на интервью (Calendly/Meet)"
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Заметки HM о кандидате"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда кандидат попал в этот статус"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда запись последний раз обновлялась"
    )

    # Relationships
    vacancy: Mapped["Vacancy"] = relationship(
        "Vacancy",
        back_populates="candidate_pools",
    )

    candidate: Mapped["Candidate"] = relationship(
        "Candidate",
        back_populates="pools",
    )

    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint("vacancy_id", "candidate_id", name="uq_vacancy_candidate"),
        Index("idx_vacancy_status", "vacancy_id", "status"),
    )

    def __repr__(self) -> str:
        """String representation of CandidatePool.

        Returns:
            str: CandidatePool representation.
        """
        return f"<CandidatePool(vacancy_id={self.vacancy_id}, candidate_id={self.candidate_id}, status={self.status.value})>"


class InterviewFeedback(Base):
    """Interview feedback model - фидбек HM после проведенного интервью."""

    __tablename__ = "interview_feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Уникальный UUID фидбека"
    )

    pool_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("candidate_pools.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Ссылка на запись в candidate pool"
    )

    feedback_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Комментарий HM после интервью"
    )

    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Решение: reject_globally, reject_team, freeze, to_finalist"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда фидбек был создан"
    )

    def __repr__(self) -> str:
        """String representation of InterviewFeedback.

        Returns:
            str: InterviewFeedback representation.
        """
        return f"<InterviewFeedback(pool_id={self.pool_id}, decision={self.decision})>"
