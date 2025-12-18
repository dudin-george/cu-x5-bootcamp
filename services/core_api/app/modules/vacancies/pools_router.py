"""Candidate Pools API router."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.vacancies.schemas import (
    CandidatePoolCreate,
    CandidatePoolResponse,
    CandidatePoolUpdate,
    CandidatePoolWithDetailsResponse,
)
from app.modules.vacancies.service import CandidatePoolService
from app.shared.enums import CandidatePoolStatus

router = APIRouter()


@router.post(
    "/",
    response_model=CandidatePoolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add candidate to pool",
    description=(
        "Add candidate to vacancy pool with initial status.\n\n"
        "**Возможные статусы кандидата:**\n"
        "- `VIEWED` - кандидат просмотрен\n"
        "- `SELECTED` - кандидат выбран для интервью\n"
        "- `INTERVIEW_SCHEDULED` - интервью назначено\n"
        "- `INTERVIEWED` - интервью проведено\n"
        "- `FINALIST` - финалист\n"
        "- `OFFER_SENT` - оффер отправлен\n"
        "- `REJECTED` - отклонен (может быть на любом этапе)\n\n"
        "По умолчанию статус устанавливается в `VIEWED`."
    ),
)
async def add_candidate_to_pool(
    vacancy_id: int = Query(..., description="Vacancy ID"),
    pool_data: CandidatePoolCreate = ...,
    db: AsyncSession = Depends(get_db),
) -> CandidatePoolResponse:
    """Add candidate to vacancy pool.

    Args:
        vacancy_id: Vacancy ID.
        pool_data: Candidate pool creation data.
        db: Database session.

    Returns:
        CandidatePoolResponse: Created pool entry.

    Raises:
        HTTPException: If candidate already in pool.
    """
    # Check if candidate is already in this vacancy pool
    existing = await CandidatePoolService.get_pool_entry_by_vacancy_and_candidate(
        db, vacancy_id, pool_data.candidate_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate {pool_data.candidate_id} is already in pool for vacancy {vacancy_id}",
        )

    pool_entry = await CandidatePoolService.add_to_pool(db, vacancy_id, pool_data)
    return CandidatePoolResponse.model_validate(pool_entry)


@router.get(
    "/",
    response_model=list[CandidatePoolWithDetailsResponse],
    summary="Get candidates in pool",
    description="Get candidates in vacancy pool with optional filters.",
)
async def get_candidates_in_pool(
    vacancy_id: int = Query(..., description="Vacancy ID to filter by"),
    status_filter: CandidatePoolStatus | None = Query(None, alias="status", description="Filter by status"),
    db: AsyncSession = Depends(get_db),
) -> list[CandidatePoolWithDetailsResponse]:
    """Get candidates in vacancy pool with details.

    Args:
        vacancy_id: Vacancy ID.
        status_filter: Optional status filter.
        db: Database session.

    Returns:
        list[CandidatePoolWithDetailsResponse]: List of candidates with details.
    """
    results = await CandidatePoolService.get_candidates_by_vacancy_with_details(
        db, vacancy_id, status=status_filter
    )

    return [
        CandidatePoolWithDetailsResponse(
            id=pool.id,
            vacancy_id=pool.vacancy_id,
            candidate_id=pool.candidate_id,
            status=pool.status,
            interview_scheduled_at=pool.interview_scheduled_at,
            interview_link=pool.interview_link,
            notes=pool.notes,
            created_at=pool.created_at,
            updated_at=pool.updated_at,
            candidate_full_name=candidate.full_name,
            candidate_phone=candidate.phone,
            candidate_location=candidate.location,
        )
        for pool, candidate in results
    ]


# @router.get(
#     "/{pool_id}",
#     response_model=CandidatePoolResponse,
#     summary="Get pool entry by ID",
#     description="Get specific candidate pool entry by its ID.",
# )
# async def get_pool_entry_by_id(
#     pool_id: uuid.UUID,
#     db: AsyncSession = Depends(get_db),
# ) -> CandidatePoolResponse:
#     """Get pool entry by ID.
#
#     Args:
#         pool_id: Pool entry UUID.
#         db: Database session.
#
#     Returns:
#         CandidatePoolResponse: Pool entry.
#
#     Raises:
#         HTTPException: If pool entry not found.
#     """
#     pool_entry = await CandidatePoolService.get_by_id(db, pool_id)
#     if not pool_entry:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Pool entry with id {pool_id} not found",
#         )
#     return CandidatePoolResponse.model_validate(pool_entry)


# @router.patch(
#     "/{pool_id}",
#     response_model=CandidatePoolResponse,
#     summary="Update pool entry",
#     description=(
#         "Update candidate pool entry (status, interview details, notes).\n\n"
#         "**Возможные статусы кандидата:**\n"
#         "- `VIEWED` - кандидат просмотрен\n"
#         "- `SELECTED` - кандидат выбран для интервью\n"
#         "- `INTERVIEW_SCHEDULED` - интервью назначено\n"
#         "- `INTERVIEWED` - интервью проведено\n"
#         "- `FINALIST` - финалист\n"
#         "- `OFFER_SENT` - оффер отправлен\n"
#         "- `REJECTED` - отклонен\n\n"
#         "Все поля опциональны. Обновляются только переданные поля."
#     ),
# )
# async def update_pool_entry(
#     pool_id: uuid.UUID,
#     update_data: CandidatePoolUpdate,
#     db: AsyncSession = Depends(get_db),
# ) -> CandidatePoolResponse:
#     """Update candidate pool entry.
#
#     Args:
#         pool_id: Pool entry UUID.
#         update_data: Fields to update.
#         db: Database session.
#
#     Returns:
#         CandidatePoolResponse: Updated pool entry.
#
#     Raises:
#         HTTPException: If pool entry not found.
#     """
#     pool_entry = await CandidatePoolService.get_by_id(db, pool_id)
#     if not pool_entry:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Pool entry with id {pool_id} not found",
#         )
#
#     updated_entry = await CandidatePoolService.update(db, pool_entry, update_data)
#     return CandidatePoolResponse.model_validate(updated_entry)


# @router.delete(
#     "/{pool_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     summary="Remove candidate from pool",
#     description="Remove candidate from vacancy pool.",
# )
# async def remove_from_pool(
#     pool_id: uuid.UUID,
#     db: AsyncSession = Depends(get_db),
# ) -> None:
#     """Remove candidate from vacancy pool.
#
#     Args:
#         pool_id: Pool entry UUID.
#         db: Database session.
#
#     Raises:
#         HTTPException: If pool entry not found.
#     """
#     pool_entry = await CandidatePoolService.get_by_id(db, pool_id)
#     if not pool_entry:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Pool entry with id {pool_id} not found",
#         )
#
#     await CandidatePoolService.remove(db, pool_entry)
