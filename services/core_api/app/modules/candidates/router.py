"""Candidates module API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.candidates.schemas import (
    CandidateCreate,
    CandidateResponse,
    CandidateUpdate,
)
from app.modules.candidates.service import CandidateService

router = APIRouter()


@router.post(
    "/",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create candidate",
    description="Create a new candidate profile. Telegram ID must be unique.",
)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: AsyncSession = Depends(get_db),
) -> CandidateResponse:
    """Create a new candidate.

    Args:
        candidate_data: Candidate creation data.
        db: Database session.

    Returns:
        CandidateResponse: Created candidate.

    Raises:
        HTTPException: If telegram_id already exists.
    """
    # Check if candidate with this telegram_id already exists
    existing = await CandidateService.get_candidate_by_telegram_id(
        db, candidate_data.telegram_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate with telegram_id {candidate_data.telegram_id} already exists",
        )

    candidate = await CandidateService.create_candidate(db, candidate_data)
    return CandidateResponse.model_validate(candidate)


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
    summary="Get candidate by ID",
    description="Get candidate profile by UUID.",
)
async def get_candidate(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CandidateResponse:
    """Get candidate by ID.

    Args:
        candidate_id: Candidate UUID.
        db: Database session.

    Returns:
        CandidateResponse: Candidate profile.

    Raises:
        HTTPException: If candidate not found.
    """
    candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found",
        )
    return CandidateResponse.model_validate(candidate)


# @router.get(
#     "/telegram/{telegram_id}",
#     response_model=CandidateResponse,
#     summary="Get candidate by Telegram ID",
#     description="Get candidate profile by Telegram user ID.",
# )
# async def get_candidate_by_telegram(
#     telegram_id: int,
#     db: AsyncSession = Depends(get_db),
# ) -> CandidateResponse:
#     """Get candidate by Telegram ID.
#
#     Args:
#         telegram_id: Telegram user ID.
#         db: Database session.
#
#     Returns:
#         CandidateResponse: Candidate profile.
#
#     Raises:
#         HTTPException: If candidate not found.
#     """
#     candidate = await CandidateService.get_candidate_by_telegram_id(db, telegram_id)
#     if not candidate:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Candidate with telegram_id {telegram_id} not found",
#         )
#     return CandidateResponse.model_validate(candidate)


@router.get(
    "/",
    response_model=list[CandidateResponse],
    summary="Get all candidates",
    description="Get list of all candidates with pagination.",
)
async def get_all_candidates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[CandidateResponse]:
    """Get all candidates.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Database session.

    Returns:
        list[CandidateResponse]: List of candidates.
    """
    candidates = await CandidateService.get_all_candidates(db, skip=skip, limit=limit)
    return [CandidateResponse.model_validate(c) for c in candidates]


# @router.patch(
#     "/{candidate_id}",
#     response_model=CandidateResponse,
#     summary="Update candidate",
#     description="Update candidate profile fields.",
# )
# async def update_candidate(
#     candidate_id: uuid.UUID,
#     update_data: CandidateUpdate,
#     db: AsyncSession = Depends(get_db),
# ) -> CandidateResponse:
#     """Update candidate.
#
#     Args:
#         candidate_id: Candidate UUID.
#         update_data: Fields to update.
#         db: Database session.
#
#     Returns:
#         CandidateResponse: Updated candidate.
#
#     Raises:
#         HTTPException: If candidate not found.
#     """
#     candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
#     if not candidate:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Candidate with id {candidate_id} not found",
#         )
#
#     updated_candidate = await CandidateService.update_candidate(
#         db, candidate, update_data
#     )
#     return CandidateResponse.model_validate(updated_candidate)


@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete candidate",
    description="Delete candidate profile. All associated data will be deleted (CASCADE).",
)
async def delete_candidate(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete candidate.

    Args:
        candidate_id: Candidate UUID.
        db: Database session.

    Raises:
        HTTPException: If candidate not found.
    """
    candidate = await CandidateService.get_candidate_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found",
        )

    await CandidateService.delete_candidate(db, candidate)


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
