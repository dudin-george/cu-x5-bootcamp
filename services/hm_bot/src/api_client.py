"""HTTP client for core_api."""

import logging
from typing import Any

import aiohttp

from src.config import config

logger = logging.getLogger(__name__)


class ApiClient:
    """Async HTTP client for core_api."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or config.api_base_url).rstrip("/")

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> tuple[dict | list | None, int]:
        """Make HTTP request to API.

        Returns:
            Tuple of (response_json, status_code)
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    try:
                        body = await response.json()
                    except Exception:
                        body = None

                    if response.status in (200, 201, 204):
                        return body, response.status
                    else:
                        logger.warning(f"API {response.status} {url}: {body}")
                        return body, response.status

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            return None, 0
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return None, 0

    async def get(
        self, endpoint: str, params: dict | None = None
    ) -> tuple[Any, int]:
        """GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: dict | None = None
    ) -> tuple[Any, int]:
        """POST request."""
        return await self._request("POST", endpoint, data=data)

    # =========================================================================
    # Hiring Manager API
    # =========================================================================

    async def create_or_get_hm(
        self,
        telegram_id: int,
        first_name: str,
        last_name: str,
    ) -> dict | None:
        """Create HM or return existing one.

        POST /api/hiring-managers/ returns 400 if exists.
        In that case, we fetch all HMs and filter by telegram_id.
        """
        data = {
            "telegram_id": telegram_id,
            "first_name": first_name,
            "last_name": last_name or "Manager",
        }

        result, status = await self.post("/api/hiring-managers/", data)

        if status == 201:
            # Created new HM
            return result
        elif status == 400:
            # Already exists - fetch all and filter
            all_hms, _ = await self.get("/api/hiring-managers/")
            if all_hms:
                for hm in all_hms:
                    if hm.get("telegram_id") == telegram_id:
                        return hm
        return None

    # =========================================================================
    # Tracks API
    # =========================================================================

    async def get_tracks(self, active_only: bool = True) -> list[dict]:
        """Get available tracks.

        GET /api/tracks/?active_only=true
        """
        params = {"active_only": str(active_only).lower()}
        result, status = await self.get("/api/tracks/", params=params)
        return result if isinstance(result, list) else []

    async def get_track_by_id(self, track_id: int) -> dict | None:
        """Get track by ID."""
        result, status = await self.get(f"/api/tracks/{track_id}")
        return result if status == 200 else None

    # =========================================================================
    # Vacancies API
    # =========================================================================

    async def create_vacancy(
        self,
        track_id: int,
        hiring_manager_id: str,
        description: str,
    ) -> dict | None:
        """Create vacancy (DRAFT status).

        POST /api/vacancies/
        """
        data = {
            "track_id": track_id,
            "hiring_manager_id": hiring_manager_id,
            "description": description,
        }
        result, status = await self.post("/api/vacancies/", data)
        return result if status == 201 else None

    async def activate_vacancy(self, vacancy_id: int) -> dict | None:
        """Activate vacancy (DRAFT -> ACTIVE).

        POST /api/vacancies/{id}/activate
        """
        result, status = await self.post(f"/api/vacancies/{vacancy_id}/activate")
        return result if status == 200 else None

    async def abort_vacancy(self, vacancy_id: int) -> dict | None:
        """Abort vacancy.

        POST /api/vacancies/{id}/abort
        """
        result, status = await self.post(f"/api/vacancies/{vacancy_id}/abort")
        return result if status == 200 else None

    async def get_my_vacancies(
        self,
        hiring_manager_id: str,
        status_filter: str | None = "ACTIVE",
    ) -> list[dict]:
        """Get vacancies for HM.

        GET /api/vacancies/?hiring_manager_id=X&status=Y
        """
        params: dict[str, str] = {"hiring_manager_id": hiring_manager_id}
        if status_filter:
            params["status"] = status_filter

        result, status = await self.get("/api/vacancies/", params=params)
        return result if isinstance(result, list) else []

    async def get_vacancy(self, vacancy_id: int) -> dict | None:
        """Get vacancy by ID.

        GET /api/vacancies/{id}
        """
        result, status = await self.get(f"/api/vacancies/{vacancy_id}")
        return result if status == 200 else None

    async def get_vacancy_stats(self, vacancy_id: int) -> dict | None:
        """Get vacancy statistics.

        GET /api/vacancies/{id}/stats
        """
        result, status = await self.get(f"/api/vacancies/{vacancy_id}/stats")
        return result if status == 200 else None

    # =========================================================================
    # Candidate Selection API (Tinder mode)
    # =========================================================================

    async def get_next_candidate(self, vacancy_id: int) -> dict | None:
        """Get next unviewed candidate for vacancy.

        GET /api/vacancies/{id}/next-candidate
        Returns 404 if no more candidates.
        """
        result, status = await self.get(f"/api/vacancies/{vacancy_id}/next-candidate")
        return result if status == 200 else None

    async def select_candidate(
        self, vacancy_id: int, candidate_id: str
    ) -> dict | None:
        """Select candidate (invite).

        POST /api/vacancies/{id}/candidates/{cid}/select
        """
        result, status = await self.post(
            f"/api/vacancies/{vacancy_id}/candidates/{candidate_id}/select"
        )
        return result if status == 201 else None

    async def skip_candidate(
        self, vacancy_id: int, candidate_id: str
    ) -> dict | None:
        """Skip candidate.

        POST /api/vacancies/{id}/candidates/{cid}/skip
        """
        result, status = await self.post(
            f"/api/vacancies/{vacancy_id}/candidates/{candidate_id}/skip"
        )
        return result if status == 201 else None

    async def reject_candidate(
        self, vacancy_id: int, candidate_id: str, notes: str | None = None
    ) -> dict | None:
        """Reject candidate.

        POST /api/vacancies/{id}/candidates/{cid}/reject
        """
        endpoint = f"/api/vacancies/{vacancy_id}/candidates/{candidate_id}/reject"
        if notes:
            endpoint += f"?notes={notes}"
        result, status = await self.post(endpoint)
        return result if status == 201 else None


# Global client instance
api = ApiClient()

