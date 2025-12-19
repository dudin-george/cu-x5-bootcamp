"""Ory Kratos session validation."""

import uuid
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class OryClient:
    """Client for Ory Kratos session validation."""

    ORY_WHOAMI_URL = "https://auth.x5teamintern.ru/sessions/whoami"

    @staticmethod
    async def validate_session(session_token: str) -> dict[str, Any]:
        """Validate Ory session token and return session data.

        Args:
            session_token: The ory_session_* cookie value.

        Returns:
            dict: Full session response from Ory.

        Raises:
            HTTPException: If session is invalid or request fails.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    OryClient.ORY_WHOAMI_URL,
                    headers={"Cookie": f"ory_session_infallibleshawgpsjwuc0lg={session_token}"},
                    timeout=5.0,
                )

                if response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired Ory session",
                    )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Ory session validation failed: {e}",
                ) from e
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to connect to Ory: {e}",
                ) from e

    @staticmethod
    async def get_identity_id(session_token: str) -> uuid.UUID:
        """Extract identity.id from Ory session.

        Args:
            session_token: The ory_session_* cookie value.

        Returns:
            uuid.UUID: The identity.id from Ory.

        Raises:
            HTTPException: If session is invalid or identity.id not found.
        """
        session_data = await OryClient.validate_session(session_token)

        try:
            identity_id_str = session_data["identity"]["id"]
            return uuid.UUID(identity_id_str)
        except (KeyError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract identity.id from Ory session: {e}",
            ) from e

    @staticmethod
    async def get_user_traits(session_token: str) -> dict[str, Any]:
        """Extract identity.traits from Ory session.

        Args:
            session_token: The ory_session_* cookie value.

        Returns:
            dict: The identity.traits from Ory (email, name, surname, person_type).

        Raises:
            HTTPException: If session is invalid or traits not found.
        """
        session_data = await OryClient.validate_session(session_token)

        try:
            return session_data["identity"]["traits"]
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract traits from Ory session: {e}",
            ) from e
