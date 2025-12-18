"""Authentication service with business logic."""

import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.shared.enums import UserRole
from app.shared.models import User


class AuthService:
    """Authentication service for user registration and login."""

    def __init__(self, db: AsyncSession):
        """Initialize auth service.

        Args:
            db: Database session.
        """
        self.db = db

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        """Register a new user.

        Args:
            data: Registration data.

        Returns:
            RegisterResponse: Registered user data with access token.

        Raises:
            HTTPException: If user with this email already exists.
        """
        # Check if user already exists
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

        # Create new user
        hashed_password = get_password_hash(data.password)
        new_user = User(
            id=uuid.uuid4(),
            email=data.email,
            password_hash=hashed_password,
            role=data.role,
            is_active=True,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # Generate access token
        access_token = create_access_token(
            data={"sub": str(new_user.id), "role": new_user.role.value}
        )

        return RegisterResponse(
            user=UserResponse.model_validate(new_user),
            access_token=access_token,
            token_type="bearer"
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user and return access token.

        Args:
            data: Login credentials.

        Returns:
            TokenResponse: Access token.

        Raises:
            HTTPException: If credentials are invalid or user is inactive.
        """
        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        # Verify user exists and password is correct
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт заблокирован"
            )

        # Generate access token
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )

    async def get_current_user(self, user_id: str) -> UserResponse:
        """Get current user by ID.

        Args:
            user_id: User UUID.

        Returns:
            UserResponse: Current user data.

        Raises:
            HTTPException: If user not found.
        """
        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return UserResponse.model_validate(user)
