"""Hiring Managers module Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class HiringManagerBase(BaseModel):
    """Base hiring manager schema."""

    telegram_id: int = Field(..., description="Telegram user ID")
    first_name: str = Field(..., min_length=1, max_length=255, description="Имя")
    last_name: str = Field(..., min_length=1, max_length=255, description="Фамилия")
    calendly_id: str | None = Field(None, max_length=255, description="ID в системе Calendly")


class HiringManagerCreate(HiringManagerBase):
    """Schema for creating a hiring manager."""

    pass


class HiringManagerUpdate(BaseModel):
    """Schema for updating a hiring manager."""

    first_name: str | None = Field(None, min_length=1, max_length=255, description="Имя")
    last_name: str | None = Field(None, min_length=1, max_length=255, description="Фамилия")
    calendly_id: str | None = Field(None, max_length=255, description="ID в системе Calendly")


class HiringManagerResponse(HiringManagerBase):
    """Schema for hiring manager response."""

    id: uuid.UUID = Field(..., description="Уникальный UUID менеджера")
    created_at: datetime = Field(..., description="Когда профиль был создан")
    updated_at: datetime = Field(..., description="Когда профиль последний раз обновлялся")

    class Config:
        """Pydantic config."""

        from_attributes = True
