"""Candidates module Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CandidateBase(BaseModel):
    """Base candidate schema."""

    telegram_id: int = Field(..., description="Telegram user ID")
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Полное имя кандидата",
        examples=["Иванов Иван Иванович"]
    )
    phone: str | None = Field(
        None,
        max_length=20,
        description="Номер телефона",
        examples=["+79991234567"]
    )
    location: str | None = Field(
        None,
        max_length=255,
        description="Местоположение (город, страна)",
        examples=["Москва, Россия"]
    )
    preferred_tracks: list[int] = Field(
        default_factory=list,
        description="Список ID треков в порядке приоритета",
        examples=[[1, 2, 3]]
    )
    university: str | None = Field(
        None,
        max_length=255,
        description="Название университета",
        examples=["МГУ им. М.В. Ломоносова"]
    )
    course: int | None = Field(
        None,
        ge=1,
        le=6,
        description="Курс обучения (1-6)",
        examples=[3]
    )
    achievements: list[str] = Field(
        default_factory=list,
        description="Достижения кандидата",
        examples=[["Победитель ACM ICPC 2024", "Автор open-source проекта с 1k+ stars"]]
    )
    domains: list[str] = Field(
        default_factory=list,
        description="Области интересов/доменов",
        examples=[["Backend Development", "Machine Learning", "Databases"]]
    )


class CandidateCreate(CandidateBase):
    """Schema for creating candidate profile."""

    pass


class CandidateUpdate(BaseModel):
    """Schema for updating candidate profile."""

    full_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Полное имя кандидата"
    )
    phone: str | None = Field(
        None,
        max_length=20,
        description="Номер телефона"
    )
    location: str | None = Field(
        None,
        max_length=255,
        description="Местоположение (город, страна)"
    )
    preferred_tracks: list[int] | None = Field(
        None,
        description="Список ID треков в порядке приоритета"
    )
    university: str | None = Field(
        None,
        max_length=255,
        description="Название университета"
    )
    course: int | None = Field(
        None,
        ge=1,
        le=6,
        description="Курс обучения (1-6)"
    )
    achievements: list[str] | None = Field(
        None,
        description="Достижения кандидата"
    )
    domains: list[str] | None = Field(
        None,
        description="Области интересов/доменов"
    )


class CandidateResponse(CandidateBase):
    """Schema for candidate profile response."""

    id: uuid.UUID = Field(..., description="UUID кандидата")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    class Config:
        """Pydantic config."""

        from_attributes = True
