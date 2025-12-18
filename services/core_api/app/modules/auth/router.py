"""Authentication router with API endpoints."""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUserId, DBSession
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя (кандидата или рекрутера) и возвращает access token",
)
async def register(
    data: RegisterRequest,
    db: DBSession,
) -> RegisterResponse:
    """Register a new user.

    Args:
        data: Registration data (email, password, role).
        db: Database session.

    Returns:
        RegisterResponse: User data with access token.

    Raises:
        HTTPException 400: If user with this email already exists.
    """
    service = AuthService(db)
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Вход в систему",
    description="Аутентификация пользователя по email и паролю, возвращает access token",
)
async def login(
    data: LoginRequest,
    db: DBSession,
) -> TokenResponse:
    """Login user.

    Args:
        data: Login credentials (email, password).
        db: Database session.

    Returns:
        TokenResponse: Access token.

    Raises:
        HTTPException 401: If credentials are invalid.
        HTTPException 403: If user account is blocked.
    """
    service = AuthService(db)
    return await service.login(data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить текущего пользователя",
    description="Возвращает данные текущего аутентифицированного пользователя",
)
async def get_current_user(
    db: DBSession,
    user_id: CurrentUserId,
) -> UserResponse:
    """Get current authenticated user.

    Args:
        db: Database session.
        user_id: Current user ID from JWT token.

    Returns:
        UserResponse: Current user data.

    Raises:
        HTTPException 404: If user not found.
        HTTPException 401: If token is invalid.
    """
    service = AuthService(db)
    return await service.get_current_user(user_id)
