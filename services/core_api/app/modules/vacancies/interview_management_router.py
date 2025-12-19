"""Interview Management API router - управление интервью."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.vacancies.schemas import (
    InterviewFeedbackCreate,
    InterviewFeedbackResponse,
)
from app.modules.vacancies.service import (
    CandidatePoolService,
    InterviewFeedbackService,
)

router = APIRouter()


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
