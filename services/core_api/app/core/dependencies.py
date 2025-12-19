"""Global FastAPI dependencies."""

import uuid
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.ory_client import OryClient
from app.core.security import decode_access_token

security = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """Get current user ID from JWT token.

    Args:
        credentials: HTTP authorization credentials.

    Returns:
        str: User ID.

    Raises:
        HTTPException: If token is invalid.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return user_id


async def get_current_recruiter_id(
    ory_session_infallibleshawgpsjwuc0lg: str | None = Cookie(None),
) -> uuid.UUID:
    """Get current recruiter ID from Ory session cookie.

    Args:
        ory_session_infallibleshawgpsjwuc0lg: Ory session cookie value.

    Returns:
        uuid.UUID: Recruiter ID (identity.id from Ory).

    Raises:
        HTTPException: If cookie is missing or session is invalid.
    """
    if not ory_session_infallibleshawgpsjwuc0lg:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Ory session cookie",
        )

    recruiter_id = await OryClient.get_identity_id(ory_session_infallibleshawgpsjwuc0lg)
    return recruiter_id


# Type aliases for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentRecruiterId = Annotated[uuid.UUID, Depends(get_current_recruiter_id)]
