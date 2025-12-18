"""Quiz API router - candidate quiz management."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


# =============================================================================
# NOT IMPLEMENTED YET - Quiz endpoints
# =============================================================================

@router.get(
    "/{candidate_id}/quiz/{track_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Get quiz for track (NOT IMPLEMENTED)",
    description="Get quiz questions for specific track. Will be implemented later.",
)
async def get_quiz_for_track(
    candidate_id: uuid.UUID,
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get quiz for track.

    NOT IMPLEMENTED YET - requires Quiz model implementation.

    Should return quiz questions with options.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Quiz functionality not implemented yet. Will be available in future release.",
    )


@router.post(
    "/{candidate_id}/quiz/{track_id}/submit",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Submit quiz answers (NOT IMPLEMENTED)",
    description="Submit answers to quiz and get score. Will be implemented later.",
)
async def submit_quiz_answers(
    candidate_id: uuid.UUID,
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit quiz answers.

    NOT IMPLEMENTED YET - requires Quiz model implementation.

    Should return:
    {
        "quiz_attempt_id": "...",
        "score": 85,
        "passed": true
    }
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Quiz submission not implemented yet. Will be available in future release.",
    )


@router.get(
    "/{candidate_id}/quiz-attempts",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Get candidate's quiz attempts (NOT IMPLEMENTED)",
    description="Get all quiz attempts for candidate. Will be implemented later.",
)
async def get_quiz_attempts(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get quiz attempts.

    NOT IMPLEMENTED YET - requires Quiz model implementation.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Quiz attempts retrieval not implemented yet. Will be available in future release.",
    )
