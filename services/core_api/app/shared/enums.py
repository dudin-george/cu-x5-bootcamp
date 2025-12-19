"""Shared enums for the recruitment system."""

from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""

    CANDIDATE = "candidate"
    RECRUITER = "recruiter"


class VacancyStatus(str, Enum):
    """Vacancy status enumeration."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ABORTED = "ABORTED"


class CandidatePoolStatus(str, Enum):
    """Candidate pool status enumeration - статусы движения кандидата по воронке."""

    VIEWED = "VIEWED"
    SELECTED = "SELECTED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEWED = "INTERVIEWED"
    FINALIST = "FINALIST"
    OFFER_SENT = "OFFER_SENT"
    REJECTED = "REJECTED"


class TaskStatus(str, Enum):
    """Task status enumeration - статусы задач в канбане рекрутера."""

    BACKLOG = "BACKLOG"  # Общий бэклог (не назначена)
    IN_PROGRESS = "IN_PROGRESS"  # В работе у конкретного рекрутера
    COMPLETED = "COMPLETED"  # Выполнена
    REJECTED = "REJECTED"  # Отклонена
