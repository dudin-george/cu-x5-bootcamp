"""Candidates module Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CandidateBase(BaseModel):
    """Base candidate schema - matches Telegram bot + AI parser format."""

    telegram_id: int = Field(..., description="Telegram user ID")
    username: str | None = Field(None, max_length=255, description="Telegram username")
    surname: str = Field(..., min_length=1, max_length=255, description="Фамилия")
    name: str = Field(..., min_length=1, max_length=255, description="Имя")
    phone: str | None = Field(None, max_length=20, description="Номер телефона")
    email: str | None = Field(None, max_length=255, description="Email адрес")
    resume_link: str | None = Field(None, max_length=500, description="Ссылка на резюме")
    priority1: str | None = Field(None, max_length=100, description="Первый приоритет трека")
    priority2: str | None = Field(None, max_length=100, description="Второй приоритет трека")
    course: str | None = Field(None, max_length=50, description="Курс обучения")
    university: str | None = Field(None, max_length=255, description="Университет")
    specialty: str | None = Field(None, max_length=255, description="Специальность")
    employment_hours: str | None = Field(None, max_length=50, description="Часы работы")
    city: str | None = Field(None, max_length=255, description="Город")
    source: str | None = Field(None, max_length=100, description="Источник")
    birth_year: str | None = Field(None, max_length=10, description="Год рождения")
    citizenship: str | None = Field(None, max_length=100, description="Гражданство")
    tech_stack: str | None = Field(None, max_length=500, description="Технологический стек")


class CandidateCreate(CandidateBase):
    """Schema for creating candidate profile."""

    pass


class CandidateUpdate(BaseModel):
    """Schema for updating candidate profile."""

    username: str | None = Field(None, max_length=255, description="Telegram username")
    surname: str | None = Field(None, min_length=1, max_length=255, description="Фамилия")
    name: str | None = Field(None, min_length=1, max_length=255, description="Имя")
    phone: str | None = Field(None, max_length=20, description="Номер телефона")
    email: str | None = Field(None, max_length=255, description="Email адрес")
    resume_link: str | None = Field(None, max_length=500, description="Ссылка на резюме")
    priority1: str | None = Field(None, max_length=100, description="Первый приоритет трека")
    priority2: str | None = Field(None, max_length=100, description="Второй приоритет трека")
    course: str | None = Field(None, max_length=50, description="Курс обучения")
    university: str | None = Field(None, max_length=255, description="Университет")
    specialty: str | None = Field(None, max_length=255, description="Специальность")
    employment_hours: str | None = Field(None, max_length=50, description="Часы работы")
    city: str | None = Field(None, max_length=255, description="Город")
    source: str | None = Field(None, max_length=100, description="Источник")
    birth_year: str | None = Field(None, max_length=10, description="Год рождения")
    citizenship: str | None = Field(None, max_length=100, description="Гражданство")
    tech_stack: str | None = Field(None, max_length=500, description="Технологический стек")


class CandidateResponse(CandidateBase):
    """Schema for candidate profile response."""

    id: uuid.UUID = Field(..., description="UUID кандидата")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    class Config:
        """Pydantic config."""

        from_attributes = True
