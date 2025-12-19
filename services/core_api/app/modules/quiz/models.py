"""Quiz module database models."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.candidates.models import Candidate
    from app.modules.vacancies.models import Track


class QuizBlock(Base):
    """Quiz block model - блок вопросов (например, Algorithms, Python, etc.)."""

    __tablename__ = "quiz_blocks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный ID блока"
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Название блока (например, 'Algorithms', 'Python Basics')"
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Описание блока"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Блок активен и используется"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда блок был создан"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда блок последний раз обновлялся"
    )

    # Relationships
    questions: Mapped[list["QuizQuestion"]] = relationship(
        "QuizQuestion",
        back_populates="block",
        cascade="all, delete-orphan",
    )

    track_associations: Mapped[list["TrackQuizBlock"]] = relationship(
        "TrackQuizBlock",
        back_populates="block",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of QuizBlock.

        Returns:
            str: QuizBlock representation.
        """
        return f"<QuizBlock(id={self.id}, name={self.name})>"


class TrackQuizBlock(Base):
    """Association table - связь между треками и блоками квиза."""

    __tablename__ = "track_quiz_blocks"

    track_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tracks.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на трек"
    )

    block_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quiz_blocks.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на блок квиза"
    )

    questions_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        comment="Сколько вопросов из этого блока в квизе"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда связь была создана"
    )

    # Relationships
    track: Mapped["Track"] = relationship(
        "Track",
        foreign_keys=[track_id],
    )

    block: Mapped["QuizBlock"] = relationship(
        "QuizBlock",
        back_populates="track_associations",
    )

    def __repr__(self) -> str:
        """String representation of TrackQuizBlock.

        Returns:
            str: TrackQuizBlock representation.
        """
        return f"<TrackQuizBlock(track_id={self.track_id}, block_id={self.block_id})>"


class QuizQuestion(Base):
    """Quiz question model - вопрос для квиза."""

    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Уникальный UUID вопроса"
    )

    block_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quiz_blocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на блок"
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст вопроса"
    )

    option_a: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Вариант ответа A"
    )

    option_b: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Вариант ответа B"
    )

    option_c: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Вариант ответа C"
    )

    option_d: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Вариант ответа D"
    )

    correct_answer: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        comment="Правильный ответ (A, B, C, или D)"
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False,
        comment="Уровень сложности (easy, medium, hard)"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Вопрос активен и используется"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда вопрос был создан"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда вопрос последний раз обновлялся"
    )

    # Relationships
    block: Mapped["QuizBlock"] = relationship(
        "QuizBlock",
        back_populates="questions",
    )

    answers: Mapped[list["QuizAnswer"]] = relationship(
        "QuizAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "correct_answer IN ('A', 'B', 'C', 'D')",
            name="ck_correct_answer_valid"
        ),
        CheckConstraint(
            "difficulty IN ('easy', 'medium', 'hard')",
            name="ck_difficulty_valid"
        ),
        Index("idx_block_active", "block_id", "is_active"),
    )

    def __repr__(self) -> str:
        """String representation of QuizQuestion.

        Returns:
            str: QuizQuestion representation.
        """
        return f"<QuizQuestion(id={self.id}, block_id={self.block_id})>"


class QuizSession(Base):
    """Quiz session model - сессия прохождения квиза."""

    __tablename__ = "quiz_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Уникальный UUID сессии"
    )

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на кандидата"
    )

    track_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tracks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на трек"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="in_progress",
        nullable=False,
        index=True,
        comment="Статус: in_progress, completed, expired"
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда квиз был начат"
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Когда квиз истекает (started_at + 15 минут)"
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Когда квиз был завершен"
    )

    total_questions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Всего вопросов отвечено"
    )

    correct_answers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Количество правильных ответов"
    )

    wrong_answers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Количество неправильных ответов"
    )

    score: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Итоговый счет (процент правильных ответов)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда сессия была создана"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда сессия последний раз обновлялась"
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship(
        "Candidate",
        foreign_keys=[candidate_id],
    )

    track: Mapped["Track"] = relationship(
        "Track",
        foreign_keys=[track_id],
    )

    answers: Mapped[list["QuizAnswer"]] = relationship(
        "QuizAnswer",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'expired')",
            name="ck_status_valid"
        ),
        Index("idx_candidate", "candidate_id"),
        Index("idx_status", "status"),
        Index("idx_track", "track_id"),
    )

    def __repr__(self) -> str:
        """String representation of QuizSession.

        Returns:
            str: QuizSession representation.
        """
        return f"<QuizSession(id={self.id}, candidate_id={self.candidate_id}, status={self.status})>"


class QuizAnswer(Base):
    """Quiz answer model - ответ кандидата на вопрос."""

    __tablename__ = "quiz_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        comment="Уникальный UUID ответа"
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на сессию квиза"
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Ссылка на вопрос"
    )

    candidate_answer: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        comment="Ответ кандидата (A, B, C, или D)"
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Правильный ли ответ"
    )

    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Когда был дан ответ"
    )

    time_taken_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Сколько времени потрачено на ответ (в секундах)"
    )

    # Relationships
    session: Mapped["QuizSession"] = relationship(
        "QuizSession",
        back_populates="answers",
    )

    question: Mapped["QuizQuestion"] = relationship(
        "QuizQuestion",
        back_populates="answers",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "candidate_answer IN ('A', 'B', 'C', 'D')",
            name="ck_candidate_answer_valid"
        ),
        UniqueConstraint("session_id", "question_id", name="uq_session_question"),
        Index("idx_session", "session_id"),
    )

    def __repr__(self) -> str:
        """String representation of QuizAnswer.

        Returns:
            str: QuizAnswer representation.
        """
        return f"<QuizAnswer(session_id={self.session_id}, question_id={self.question_id}, is_correct={self.is_correct})>"
