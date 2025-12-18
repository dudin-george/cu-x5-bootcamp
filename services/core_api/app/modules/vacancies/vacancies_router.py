"""Vacancies API router."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.candidates.schemas import CandidateResponse
from app.modules.vacancies.schemas import (
    CandidatePoolResponse,
    InterviewFeedbackCreate,
    InterviewFeedbackResponse,
    VacancyCreate,
    VacancyResponse,
    VacancyStatsResponse,
    VacancyUpdate,
    VacancyWithCandidatesResponse,
)
from app.modules.vacancies.service import (
    CandidatePoolService,
    InterviewFeedbackService,
    VacancyService,
)
from app.shared.enums import CandidatePoolStatus, VacancyStatus

router = APIRouter()


@router.post(
    "/",
    response_model=VacancyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create vacancy",
    description="Create a new vacancy. Vacancy is created with DRAFT status.",
)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    db: AsyncSession = Depends(get_db),
) -> VacancyResponse:
    """Create a new vacancy.

    Args:
        vacancy_data: Vacancy creation data.
        db: Database session.

    Returns:
        VacancyResponse: Created vacancy with DRAFT status.
    """
    vacancy = await VacancyService.create_vacancy(db, vacancy_data)
    return VacancyResponse.model_validate(vacancy)


@router.get(
    "/",
    response_model=list[VacancyResponse],
    summary="Get all vacancies",
    description="Get list of all vacancies with optional filters.",
)
async def get_all_vacancies(
    status_filter: VacancyStatus | None = Query(None, alias="status", description="Filter by status"),
    track_id: int | None = Query(None, description="Filter by track ID"),
    hiring_manager_id: uuid.UUID | None = Query(None, description="Filter by hiring manager UUID"),
    db: AsyncSession = Depends(get_db),
) -> list[VacancyResponse]:
    """Get all vacancies with optional filters.

    Args:
        status_filter: Filter by vacancy status.
        track_id: Filter by track ID.
        hiring_manager_id: Filter by hiring manager UUID.
        db: Database session.

    Returns:
        list[VacancyResponse]: List of vacancies.
    """
    vacancies = await VacancyService.get_all_vacancies(
        db,
        status=status_filter,
        track_id=track_id,
        hiring_manager_id=hiring_manager_id,
    )
    return [VacancyResponse.model_validate(v) for v in vacancies]


@router.get(
    "/{vacancy_id}",
    response_model=VacancyResponse,
    summary="Get vacancy by ID",
    description="Get vacancy details by ID.",
)
async def get_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
) -> VacancyResponse:
    """Get vacancy by ID.

    Args:
        vacancy_id: Vacancy ID.
        db: Database session.

    Returns:
        VacancyResponse: Vacancy details.

    Raises:
        HTTPException: If vacancy not found.
    """
    vacancy = await VacancyService.get_vacancy_by_id(db, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found",
        )
    return VacancyResponse.model_validate(vacancy)


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


@router.patch(
    "/{vacancy_id}",
    response_model=VacancyResponse,
    summary="Update vacancy",
    description="Update vacancy fields.",
)
async def update_vacancy(
    vacancy_id: int,
    update_data: VacancyUpdate,
    db: AsyncSession = Depends(get_db),
) -> VacancyResponse:
    """Update vacancy.

    Args:
        vacancy_id: Vacancy ID.
        update_data: Fields to update.
        db: Database session.

    Returns:
        VacancyResponse: Updated vacancy.

    Raises:
        HTTPException: If vacancy not found.
    """
    vacancy = await VacancyService.get_vacancy_by_id(db, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found",
        )

    updated_vacancy = await VacancyService.update_vacancy(db, vacancy, update_data)
    return VacancyResponse.model_validate(updated_vacancy)


@router.post(
    "/{vacancy_id}/activate",
    response_model=VacancyResponse,
    summary="Activate vacancy",
    description="Change vacancy status to ACTIVE.",
)
async def activate_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
) -> VacancyResponse:
    """Activate vacancy.

    Args:
        vacancy_id: Vacancy ID.
        db: Database session.

    Returns:
        VacancyResponse: Activated vacancy.

    Raises:
        HTTPException: If vacancy not found.
    """
    vacancy = await VacancyService.get_vacancy_by_id(db, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found",
        )

    activated_vacancy = await VacancyService.activate_vacancy(db, vacancy)
    return VacancyResponse.model_validate(activated_vacancy)


@router.post(
    "/{vacancy_id}/abort",
    response_model=VacancyResponse,
    summary="Abort vacancy",
    description="Change vacancy status to ABORTED.",
)
async def abort_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
) -> VacancyResponse:
    """Abort vacancy.

    Args:
        vacancy_id: Vacancy ID.
        db: Database session.

    Returns:
        VacancyResponse: Aborted vacancy.

    Raises:
        HTTPException: If vacancy not found.
    """
    vacancy = await VacancyService.get_vacancy_by_id(db, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found",
        )

    aborted_vacancy = await VacancyService.abort_vacancy(db, vacancy)
    return VacancyResponse.model_validate(aborted_vacancy)


@router.delete(
    "/{vacancy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete vacancy",
    description="Delete vacancy. All associated candidate pool entries will be deleted (CASCADE).",
)
async def delete_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete vacancy.

    Args:
        vacancy_id: Vacancy ID.
        db: Database session.

    Raises:
        HTTPException: If vacancy not found.
    """
    vacancy = await VacancyService.get_vacancy_by_id(db, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found",
        )

    await VacancyService.delete_vacancy(db, vacancy)


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


@router.get(
    "/{vacancy_id}/stats",
    response_model=VacancyStatsResponse,
    summary="Get vacancy statistics",
    description=(
        "Get statistics for vacancy - count of candidates in each status.\n\n"
        "Returns counts for: viewed, selected, interview_scheduled, "
        "interviewed, finalist, offer_sent, rejected."
    ),
)
async def get_vacancy_stats(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
) -> VacancyStatsResponse:
    """Get vacancy statistics.

    Args:
        vacancy_id: Vacancy ID.
        db: Database session.

    Returns:
        VacancyStatsResponse: Statistics by candidate statuses.

    Raises:
        HTTPException: If vacancy not found.
    """
    # Verify vacancy exists
    vacancy = await VacancyService.get_vacancy_by_id(db, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacancy with id {vacancy_id} not found",
        )

    stats = await CandidatePoolService.get_vacancy_stats(db, vacancy_id)
    return VacancyStatsResponse(**stats)


@router.post(
    "/{vacancy_id}/candidates/{pool_id}/feedback",
    response_model=InterviewFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit interview feedback",
    description=(
        "Submit feedback after interview with decision.\n\n"
        "**Возможные решения:**\n"
        "- `reject_globally`: отказ во всей компании (статус → REJECTED)\n"
        "- `reject_team`: отказ по команде, другие HM могут смотреть (статус → REJECTED)\n"
        "- `freeze`: поморозим и посмотрим позже (статус → INTERVIEWED)\n"
        "- `to_finalist`: в список финалистов (статус → FINALIST)"
    ),
)
async def submit_interview_feedback(
    vacancy_id: int,
    pool_id: uuid.UUID,
    feedback_data: InterviewFeedbackCreate,
    db: AsyncSession = Depends(get_db),
) -> InterviewFeedbackResponse:
    """Submit feedback after interview.

    Args:
        vacancy_id: Vacancy ID (for verification).
        pool_id: Candidate pool entry ID.
        feedback_data: Feedback and decision.
        db: Database session.

    Returns:
        InterviewFeedbackResponse: Created feedback.

    Raises:
        HTTPException: If pool entry not found or already has feedback.
    """
    # Verify pool entry exists and belongs to this vacancy
    pool_entry = await CandidatePoolService.get_pool_entry_by_id(db, pool_id)
    if not pool_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pool entry with id {pool_id} not found",
        )
    if pool_entry.vacancy_id != vacancy_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pool entry {pool_id} does not belong to vacancy {vacancy_id}",
        )

    # Check if feedback already exists
    existing_feedback = await InterviewFeedbackService.get_feedback_by_pool_id(db, pool_id)
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feedback already exists for pool entry {pool_id}",
        )

    feedback = await InterviewFeedbackService.create_feedback(db, pool_id, feedback_data)
    return InterviewFeedbackResponse.model_validate(feedback)


@router.get(
    "/{vacancy_id}/candidates/{pool_id}/feedback",
    response_model=InterviewFeedbackResponse,
    summary="Get interview feedback",
    description="Get feedback for specific candidate pool entry.",
)
async def get_interview_feedback(
    vacancy_id: int,
    pool_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> InterviewFeedbackResponse:
    """Get interview feedback.

    Args:
        vacancy_id: Vacancy ID (for verification).
        pool_id: Candidate pool entry ID.
        db: Database session.

    Returns:
        InterviewFeedbackResponse: Feedback details.

    Raises:
        HTTPException: If feedback not found.
    """
    feedback = await InterviewFeedbackService.get_feedback_by_pool_id(db, pool_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback for pool entry {pool_id} not found",
        )
    return InterviewFeedbackResponse.model_validate(feedback)


# =============================================================================
# NOT IMPLEMENTED YET - Endpoints for future features
# =============================================================================

@router.post(
    "/{vacancy_id}/candidates/{pool_id}/cancel-interview",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Cancel interview (NOT IMPLEMENTED)",
    description="Cancel scheduled interview. This endpoint will be implemented later with Calendly integration.",
)
async def cancel_interview(
    vacancy_id: int,
    pool_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Cancel scheduled interview.

    NOT IMPLEMENTED YET - requires Calendly integration.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Interview cancellation not implemented yet. Will be available with Calendly integration.",
    )


@router.post(
    "/{vacancy_id}/candidates/{pool_id}/reschedule-interview",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Reschedule interview (NOT IMPLEMENTED)",
    description="Reschedule interview to a new time slot. This endpoint will be implemented later with Calendly integration.",
)
async def reschedule_interview(
    vacancy_id: int,
    pool_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Reschedule interview.

    NOT IMPLEMENTED YET - requires Calendly integration.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Interview rescheduling not implemented yet. Will be available with Calendly integration.",
    )
