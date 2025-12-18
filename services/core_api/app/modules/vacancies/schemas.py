"""Vacancies module Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.enums import CandidatePoolStatus, VacancyStatus


# Track Schemas
class TrackCreate(BaseModel):
    """Schema for creating a new track."""

    name: str = Field(..., min_length=1, max_length=255, description="Название трека")
    description: str | None = Field(None, description="Описание трека")
    is_active: bool = Field(True, description="Активен ли трек")


class TrackUpdate(BaseModel):
    """Schema for updating a track."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Название трека")
    description: str | None = Field(None, description="Описание трека")
    is_active: bool | None = Field(None, description="Активен ли трек")


class TrackResponse(BaseModel):
    """Schema for track response."""

    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Vacancy Schemas
class VacancyCreate(BaseModel):
    """Schema for creating a new vacancy."""

    track_id: int = Field(..., description="ID трека")
    hiring_manager_id: uuid.UUID = Field(..., description="UUID hiring manager")
    description: str = Field(..., min_length=1, description="Описание позиции")


class VacancyUpdate(BaseModel):
    """Schema for updating a vacancy."""

    description: str | None = Field(None, min_length=1, description="Описание позиции")
    next_interview_at: datetime | None = Field(None, description="Дата ближайшего собеседования")
    next_interview_link: str | None = Field(None, max_length=500, description="Ссылка на собеседование")


class VacancyResponse(BaseModel):
    """Schema for vacancy response."""

    id: int
    track_id: int
    hiring_manager_id: uuid.UUID
    description: str
    status: VacancyStatus
    next_interview_at: datetime | None
    next_interview_link: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# CandidatePool Schemas
class CandidatePoolCreate(BaseModel):
    """Schema for adding candidate to vacancy pool.

    Workflow статусов:
    1. VIEWED - кандидат просмотрен
    2. SELECTED - кандидат выбран для интервью
    3. INTERVIEW_SCHEDULED - интервью назначено
    4. INTERVIEWED - интервью проведено
    5. FINALIST - финалист
    6. OFFER_SENT - оффер отправлен
    7. REJECTED - отклонен (может быть на любом этапе)
    """

    candidate_id: uuid.UUID = Field(..., description="UUID кандидата")
    status: CandidatePoolStatus = Field(
        default=CandidatePoolStatus.VIEWED,
        description=(
            "Статус кандидата в воронке. Возможные значения:\n"
            "- VIEWED: просмотрен\n"
            "- SELECTED: выбран для интервью\n"
            "- INTERVIEW_SCHEDULED: интервью назначено\n"
            "- INTERVIEWED: интервью проведено\n"
            "- FINALIST: финалист\n"
            "- OFFER_SENT: оффер отправлен\n"
            "- REJECTED: отклонен"
        ),
        examples=["VIEWED", "SELECTED", "INTERVIEW_SCHEDULED"]
    )
    notes: str | None = Field(None, description="Заметки HM о кандидате")


class CandidatePoolUpdate(BaseModel):
    """Schema for updating candidate pool entry."""

    status: CandidatePoolStatus | None = Field(
        None,
        description=(
            "Новый статус кандидата. Возможные значения:\n"
            "- VIEWED: просмотрен\n"
            "- SELECTED: выбран для интервью\n"
            "- INTERVIEW_SCHEDULED: интервью назначено\n"
            "- INTERVIEWED: интервью проведено\n"
            "- FINALIST: финалист\n"
            "- OFFER_SENT: оффер отправлен\n"
            "- REJECTED: отклонен"
        ),
        examples=["INTERVIEW_SCHEDULED", "INTERVIEWED", "FINALIST"]
    )
    interview_scheduled_at: datetime | None = Field(
        None,
        description="Дата и время интервью (ISO 8601 формат)",
        examples=["2025-12-20T14:00:00Z"]
    )
    interview_link: str | None = Field(
        None,
        max_length=500,
        description="Ссылка на интервью (Calendly, Google Meet, Zoom, etc.)",
        examples=["https://calendly.com/hiring-manager/interview"]
    )
    notes: str | None = Field(
        None,
        description="Заметки HM о кандидате",
        examples=["Сильные навыки в Python, хорошо прошел technical interview"]
    )


class CandidatePoolResponse(BaseModel):
    """Schema for candidate pool response."""

    id: uuid.UUID
    vacancy_id: int
    candidate_id: uuid.UUID
    status: CandidatePoolStatus
    interview_scheduled_at: datetime | None
    interview_link: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Combined responses with related data
class VacancyWithCandidatesResponse(BaseModel):
    """Schema for vacancy with candidates list."""

    vacancy: VacancyResponse
    candidates: list[CandidatePoolResponse]


class CandidatePoolWithDetailsResponse(CandidatePoolResponse):
    """Schema for candidate pool with candidate details."""

    candidate_full_name: str = Field(..., description="Имя кандидата")
    candidate_phone: str | None = Field(None, description="Телефон кандидата")
    candidate_location: str | None = Field(None, description="Местоположение кандидата")

    class Config:
        """Pydantic config."""

        from_attributes = True


# Vacancy Statistics
class VacancyStatsResponse(BaseModel):
    """Schema for vacancy statistics by candidate statuses."""

    vacancy_id: int = Field(..., description="ID вакансии")
    total_candidates: int = Field(..., description="Всего кандидатов в пуле")
    viewed: int = Field(..., description="Просмотрено (пропущено)")
    selected: int = Field(..., description="Отобрано для интервью")
    interview_scheduled: int = Field(..., description="Интервью назначено")
    interviewed: int = Field(..., description="Проинтервьюировано")
    finalist: int = Field(..., description="Финалистов")
    offer_sent: int = Field(..., description="Оффер отправлен")
    rejected: int = Field(..., description="Отклонено")


# Interview Feedback
class InterviewFeedbackCreate(BaseModel):
    """Schema for creating interview feedback."""

    feedback_text: str = Field(
        ...,
        min_length=1,
        description="Комментарий HM после интервью",
        examples=["Сильные технические навыки, хорошо решал задачи"]
    )
    decision: str = Field(
        ...,
        description=(
            "Решение по кандидату:\n"
            "- reject_globally: отказ во всей компании\n"
            "- reject_team: отказ по команде, другие HM могут смотреть\n"
            "- freeze: поморозим и посмотрим позже\n"
            "- to_finalist: в список финалистов"
        ),
        examples=["to_finalist", "freeze", "reject_team", "reject_globally"]
    )


class InterviewFeedbackResponse(BaseModel):
    """Schema for interview feedback response."""

    id: uuid.UUID = Field(..., description="UUID фидбека")
    pool_id: uuid.UUID = Field(..., description="UUID записи в candidate pool")
    feedback_text: str = Field(..., description="Комментарий HM")
    decision: str = Field(..., description="Решение по кандидату")
    created_at: datetime = Field(..., description="Когда фидбек был создан")

    class Config:
        """Pydantic config."""

        from_attributes = True
