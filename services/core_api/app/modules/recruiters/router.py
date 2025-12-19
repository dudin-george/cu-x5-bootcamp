"""Recruiter API router."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.recruiters.schemas import (
    RecruiterCreate,
    RecruiterListResponse,
    RecruiterResponse,
)
from app.modules.recruiters.service import RecruiterService

router = APIRouter()


@router.post(
    "/",
    response_model=RecruiterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create recruiter",
    description="Создать нового рекрутера (временная ручка для тестирования)",
)
async def create_recruiter(
    data: RecruiterCreate,
    db: AsyncSession = Depends(get_db),
) -> RecruiterResponse:
    """Create recruiter.

    Args:
        data: Recruiter creation data.
        db: Database session.

    Returns:
        RecruiterResponse: Created recruiter.
    """
    recruiter = await RecruiterService.create_recruiter(db, data)
    return RecruiterResponse.model_validate(recruiter)


@router.get(
    "/",
    response_model=RecruiterListResponse,
    status_code=status.HTTP_200_OK,
    summary="List recruiters",
    description="Получить список всех рекрутеров",
)
async def list_recruiters(
    db: AsyncSession = Depends(get_db),
) -> RecruiterListResponse:
    """List all recruiters.

    Args:
        db: Database session.

    Returns:
        RecruiterListResponse: List of recruiters.
    """
    recruiters = await RecruiterService.get_all_recruiters(db)
    return RecruiterListResponse(
        recruiters=[RecruiterResponse.model_validate(r) for r in recruiters]
    )
