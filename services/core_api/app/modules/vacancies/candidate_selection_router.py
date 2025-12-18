"""Candidate Selection API router - отбор кандидатов (Tinder mode)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.candidates.schemas import CandidateResponse
from app.modules.vacancies.schemas import (
    CandidatePoolResponse,
    VacancyWithCandidatesResponse,
    VacancyResponse,
)
from app.modules.vacancies.service import (
    CandidatePoolService,
    VacancyService,
)
from app.shared.enums import CandidatePoolStatus

router = APIRouter()


@router.get(
    "/{vacancy_id}/with-candidates",
    response_model=VacancyWithCandidatesResponse,
    summary="Get vacancy with candidates",
    description="Get vacancy details with all candidates from pool.",
)
async def get_vacancy_with_candidates(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
) -> VacancyWithCandidatesResponse:
    """Get vacancy with all candidates from pool.

    Args:
        vacancy_id: Vacancy ID.
        db: Database session.

    Returns:
        VacancyWithCandidatesResponse: Vacancy with candidates list.

    Raises:
        HTTPException: If vacancy not found.
    """
    vacancy = await VacancyService.get_vacancy_by_id(db, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found",
        )

    candidates = await CandidatePoolService.get_candidates_by_vacancy(db, vacancy_id)

    return VacancyWithCandidatesResponse(
        vacancy=VacancyResponse.model_validate(vacancy),
        candidates=[CandidatePoolResponse.model_validate(c) for c in candidates],
    )


@router.get(
    "/{vacancy_id}/next-candidate",
    response_model=CandidateResponse,
    summary="Get next candidate for review",
    description=(
        "Get next candidate who hasn't been viewed for this vacancy yet (Tinder mode).\n\n"
        "Returns the first candidate who is NOT in the vacancy's pool. "
        "If all candidates have been reviewed, returns 404."
    ),
)
async def get_next_candidate(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
) -> CandidateResponse:
    """Get next unviewed candidate for vacancy in Tinder mode.

    Args:
        vacancy_id: Vacancy ID.
        db: Database session.

    Returns:
        CandidateResponse: Next candidate to review.

    Raises:
        HTTPException: If vacancy not found or no more candidates.
    """
    # Verify vacancy exists
    vacancy = await VacancyService.get_vacancy_by_id(db, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found",
        )

    # Get next unviewed candidate
    candidate = await CandidatePoolService.get_next_unviewed_candidate(db, vacancy_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No more candidates to review for this vacancy",
        )

    return CandidateResponse.model_validate(candidate)


@router.post(
    "/{vacancy_id}/candidates/{candidate_id}/select",
    response_model=CandidatePoolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Select candidate for interview",
    description=(
        "Select candidate for interview (/invite button action).\n\n"
        "Adds candidate to pool with status SELECTED."
    ),
)
async def select_candidate(
    vacancy_id: int,
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CandidatePoolResponse:
    """Select candidate for interview.

    Args:
        vacancy_id: Vacancy ID.
        candidate_id: Candidate UUID.
        db: Database session.

    Returns:
        CandidatePoolResponse: Created pool entry with SELECTED status.

    Raises:
        HTTPException: If candidate already in pool.
    """
    # Check if already in pool
    existing = await CandidatePoolService.get_pool_entry_by_vacancy_and_candidate(
        db, vacancy_id, candidate_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate {candidate_id} is already in pool for vacancy {vacancy_id}",
        )

    pool_entry = await CandidatePoolService.add_candidate_with_status(
        db, vacancy_id, candidate_id, CandidatePoolStatus.SELECTED
    )
    return CandidatePoolResponse.model_validate(pool_entry)


@router.post(
    "/{vacancy_id}/candidates/{candidate_id}/skip",
    response_model=CandidatePoolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Skip candidate",
    description=(
        "Skip candidate (/skip button action).\n\n"
        "Adds candidate to pool with status VIEWED. "
        "This candidate won't be shown again for this vacancy."
    ),
)
async def skip_candidate(
    vacancy_id: int,
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CandidatePoolResponse:
    """Skip candidate (soft reject).

    Args:
        vacancy_id: Vacancy ID.
        candidate_id: Candidate UUID.
        db: Database session.

    Returns:
        CandidatePoolResponse: Created pool entry with VIEWED status.

    Raises:
        HTTPException: If candidate already in pool.
    """
    # Check if already in pool
    existing = await CandidatePoolService.get_pool_entry_by_vacancy_and_candidate(
        db, vacancy_id, candidate_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate {candidate_id} is already in pool for vacancy {vacancy_id}",
        )

    pool_entry = await CandidatePoolService.add_candidate_with_status(
        db, vacancy_id, candidate_id, CandidatePoolStatus.VIEWED
    )
    return CandidatePoolResponse.model_validate(pool_entry)


@router.post(
    "/{vacancy_id}/candidates/{candidate_id}/reject",
    response_model=CandidatePoolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reject candidate",
    description=(
        "Reject candidate (/reject or /redirect button action).\n\n"
        "Adds candidate to pool with status REJECTED. "
        "Use notes field to specify reason (e.g., 'redirect_to_other_team')."
    ),
)
async def reject_candidate(
    vacancy_id: int,
    candidate_id: uuid.UUID,
    notes: str | None = Query(None, description="Rejection reason or notes"),
    db: AsyncSession = Depends(get_db),
) -> CandidatePoolResponse:
    """Reject candidate.

    Args:
        vacancy_id: Vacancy ID.
        candidate_id: Candidate UUID.
        notes: Optional rejection reason (e.g., "redirect_to_other_team").
        db: Database session.

    Returns:
        CandidatePoolResponse: Created pool entry with REJECTED status.

    Raises:
        HTTPException: If candidate already in pool.
    """
    # Check if already in pool
    existing = await CandidatePoolService.get_pool_entry_by_vacancy_and_candidate(
        db, vacancy_id, candidate_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate {candidate_id} is already in pool for vacancy {vacancy_id}",
        )

    pool_entry = await CandidatePoolService.add_candidate_with_status(
        db, vacancy_id, candidate_id, CandidatePoolStatus.REJECTED, notes=notes
    )
    return CandidatePoolResponse.model_validate(pool_entry)
