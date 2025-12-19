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
    ) -> dict | None:
        """Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/api/candidates")
            data: JSON body for POST/PUT
            params: Query parameters
            
        Returns:
            Response JSON or None on error.
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
                    if response.status in (200, 201):
                        return await response.json()
                    elif response.status == 404:
                        logger.debug(f"Not found: {url}")
                        return None
                    else:
                        text = await response.text()
                        logger.error(f"API Error {response.status} {url}: {text}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return None
    
    async def get(self, endpoint: str, params: dict | None = None) -> dict | None:
        """GET request."""
        return await self._request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: dict) -> dict | None:
        """POST request."""
        return await self._request("POST", endpoint, data=data)
    
    # =========================================================================
    # Candidate API
    # =========================================================================
    
    async def create_candidate(self, candidate_data: dict) -> dict | None:
        """Create candidate profile.
        
        POST /api/candidates/
        
        Args:
            candidate_data: Candidate data from form.
            
        Returns:
            Created candidate with `id` (UUID) or None.
        """
        return await self.post("/api/candidates/", candidate_data)
    
    async def get_candidate_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get candidate by telegram ID.
        
        GET /api/candidates/telegram/{telegram_id}
        
        Args:
            telegram_id: Telegram user ID.
            
        Returns:
            Candidate data with `id` (UUID) or None if not found.
        """
        return await self.get(f"/api/candidates/telegram/{telegram_id}")
    
    # =========================================================================
    # Quiz API
    # Swagger: https://dev.x5teamintern.ru/api/docs
    # =========================================================================
    
    async def start_quiz(self, candidate_id: str, track_id: int) -> dict | None:
        """Start quiz session.
        
        POST /api/quiz/start
        
        Args:
            candidate_id: Candidate UUID (string).
            track_id: Track ID for quiz.
            
        Returns:
            {
                "session_id": "uuid",
                "question": {
                    "id": "uuid",
                    "text": "...",
                    "block_name": "...",
                    "options": [{"key": "A", "text": "..."}, ...],
                    "question_number": 1
                }
            }
        """
        return await self.post("/api/quiz/start", {
            "candidate_id": candidate_id,
            "track_id": track_id,
        })
    
    async def submit_answer(
        self,
        session_id: str,
        question_id: str,
        answer: str,
    ) -> dict | None:
        """Submit quiz answer.
        
        POST /api/quiz/answer
        
        Args:
            session_id: Quiz session UUID.
            question_id: Question UUID.
            answer: Answer key ("A", "B", "C", or "D").
            
        Returns:
            If quiz continues:
            {
                "type": "continue",
                "question": {...}
            }
            
            If quiz ended:
            {
                "type": "end",
                "message": "Квиз завершен"
            }
        """
        return await self.post("/api/quiz/answer", {
            "session_id": session_id,
            "question_id": question_id,
            "answer": answer,
        })
    
    async def get_quiz_attempts(
        self,
        candidate_id: str,
        track_id: int | None = None,
    ) -> dict | None:
        """Get quiz attempts for candidate.
        
        GET /api/quiz/attempts?candidate_id=xxx&track_id=yyy
        
        Args:
            candidate_id: Candidate UUID.
            track_id: Optional track filter.
            
        Returns:
            {"attempts": [...]}
        """
        params = {"candidate_id": candidate_id}
        if track_id:
            params["track_id"] = track_id
        return await self.get("/api/quiz/attempts", params=params)
    
    # =========================================================================
    # Tracks API
    # =========================================================================
    
    async def get_tracks(self, active_only: bool = True) -> list[dict] | None:
        """Get available tracks.
        
        GET /api/tracks/?active_only=true
        
        Args:
            active_only: Return only active tracks.
            
        Returns:
            List of tracks: [{id: int, name: str, description: str, is_active: bool}, ...]
        """
        params = {"active_only": str(active_only).lower()}
        result = await self.get("/api/tracks/", params=params)
        return result if isinstance(result, list) else None
    
    async def get_track_by_id(self, track_id: int) -> dict | None:
        """Get track by ID.
        
        GET /api/tracks/{track_id}
        
        Args:
            track_id: Track ID.
            
        Returns:
            Track data or None.
        """
        return await self.get(f"/api/tracks/{track_id}")


# Global client instance
api_client = ApiClient()
