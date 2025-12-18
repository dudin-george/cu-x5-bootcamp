"""Authentication module Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.shared.enums import UserRole


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Пароль (минимум 8 символов)",
        examples=["SecurePassword123"]
    )
    role: UserRole = Field(
        ...,
        description="Роль пользователя: candidate или recruiter",
        examples=["candidate"]
    )


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="Пароль",
        examples=["SecurePassword123"]
    )


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )


class UserResponse(BaseModel):
    """Schema for user data response."""

    id: uuid.UUID = Field(
        ...,
        description="UUID пользователя"
    )
    email: str = Field(
        ...,
        description="Email пользователя"
    )
    role: UserRole = Field(
        ...,
        description="Роль пользователя"
    )
    telegram_id: str | None = Field(
        None,
        description="ID в Telegram"
    )
    is_active: bool = Field(
        ...,
        description="Аккаунт активен"
    )
    created_at: datetime = Field(
        ...,
        description="Дата создания аккаунта"
    )
    updated_at: datetime = Field(
        ...,
        description="Дата последнего обновления"
    )

    class Config:
        """Pydantic config."""

        from_attributes = True


class RegisterResponse(BaseModel):
    """Schema for registration response."""

    user: UserResponse = Field(
        ...,
        description="Данные созданного пользователя"
    )
    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )
