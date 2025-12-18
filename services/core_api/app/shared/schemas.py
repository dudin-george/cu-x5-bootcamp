"""Shared Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.shared.enums import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    """User creation schema."""

    password: str


class UserResponse(UserBase):
    """User response schema."""

    id: uuid.UUID
    is_active: bool
    telegram_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"
