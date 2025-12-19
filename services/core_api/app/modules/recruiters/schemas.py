"""Recruiter schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class RecruiterCreate(BaseModel):
    """Schema for creating a recruiter."""

    full_name: str = Field(..., min_length=1, max_length=200, description="ФИО рекрутера")


class RecruiterResponse(BaseModel):
    """Schema for recruiter response."""

    id: int = Field(..., description="ID рекрутера")
    full_name: str = Field(..., description="ФИО рекрутера")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")

    class Config:
        from_attributes = True


class RecruiterListResponse(BaseModel):
    """Schema for list of recruiters."""

    recruiters: list[RecruiterResponse] = Field(..., description="Список рекрутеров")
