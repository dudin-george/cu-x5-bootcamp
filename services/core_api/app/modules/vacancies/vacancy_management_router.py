"""Vacancy Management API router - управление вакансиями."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.vacancies.schemas import (
    VacancyCreate,
    VacancyResponse,
    VacancyStatsResponse,
)
from app.modules.vacancies.service import (
    CandidatePoolService,
    VacancyService,
)
from app.shared.enums import VacancyStatus

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
    hiring_manager_id: str | None = Query(None, description="Filter by hiring manager UUID"),
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
    import uuid
    hm_id = uuid.UUID(hiring_manager_id) if hiring_manager_id else None

    vacancies = await VacancyService.get_all_vacancies(
        db,
        status=status_filter,
        track_id=track_id,
        hiring_manager_id=hm_id,
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
