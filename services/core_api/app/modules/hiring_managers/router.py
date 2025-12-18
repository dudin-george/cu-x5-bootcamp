"""Hiring Managers module API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.hiring_managers.schemas import (
    HiringManagerCreate,
    HiringManagerResponse,
    HiringManagerUpdate,
)
from app.modules.hiring_managers.service import HiringManagerService

router = APIRouter()


@router.post(
    "/",
    response_model=HiringManagerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create hiring manager",
    description="Create a new hiring manager profile. Telegram ID must be unique.",
)
async def create_hiring_manager(
    hiring_manager_data: HiringManagerCreate,
    db: AsyncSession = Depends(get_db),
) -> HiringManagerResponse:
    """Create a new hiring manager.

    Args:
        hiring_manager_data: Hiring manager creation data.
        db: Database session.

    Returns:
        HiringManagerResponse: Created hiring manager.

    Raises:
        HTTPException: If telegram_id already exists.
    """
    # Check if hiring manager with this telegram_id already exists
    existing = await HiringManagerService.get_hiring_manager_by_telegram_id(
        db, hiring_manager_data.telegram_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hiring manager with telegram_id {hiring_manager_data.telegram_id} already exists",
        )

    hiring_manager = await HiringManagerService.create_hiring_manager(
        db, hiring_manager_data
    )
    return HiringManagerResponse.model_validate(hiring_manager)


@router.get(
    "/{hiring_manager_id}",
    response_model=HiringManagerResponse,
    summary="Get hiring manager by ID",
    description="Get hiring manager profile by UUID.",
)
async def get_hiring_manager(
    hiring_manager_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> HiringManagerResponse:
    """Get hiring manager by ID.

    Args:
        hiring_manager_id: Hiring manager UUID.
        db: Database session.

    Returns:
        HiringManagerResponse: Hiring manager profile.

    Raises:
        HTTPException: If hiring manager not found.
    """
    hiring_manager = await HiringManagerService.get_hiring_manager_by_id(
        db, hiring_manager_id
    )
    if not hiring_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hiring manager with id {hiring_manager_id} not found",
        )
    return HiringManagerResponse.model_validate(hiring_manager)


# @router.get(
#     "/telegram/{telegram_id}",
#     response_model=HiringManagerResponse,
#     summary="Get hiring manager by Telegram ID",
#     description="Get hiring manager profile by Telegram user ID.",
# )
# async def get_hiring_manager_by_telegram(
#     telegram_id: int,
#     db: AsyncSession = Depends(get_db),
# ) -> HiringManagerResponse:
#     """Get hiring manager by Telegram ID.
#
#     Args:
#         telegram_id: Telegram user ID.
#         db: Database session.
#
#     Returns:
#         HiringManagerResponse: Hiring manager profile.
#
#     Raises:
#         HTTPException: If hiring manager not found.
#     """
#     hiring_manager = await HiringManagerService.get_hiring_manager_by_telegram_id(
#         db, telegram_id
#     )
#     if not hiring_manager:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Hiring manager with telegram_id {telegram_id} not found",
#         )
#     return HiringManagerResponse.model_validate(hiring_manager)


@router.get(
    "/",
    response_model=list[HiringManagerResponse],
    summary="Get all hiring managers",
    description="Get list of all hiring managers with pagination.",
)
async def get_all_hiring_managers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[HiringManagerResponse]:
    """Get all hiring managers.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Database session.

    Returns:
        list[HiringManagerResponse]: List of hiring managers.
    """
    hiring_managers = await HiringManagerService.get_all_hiring_managers(
        db, skip=skip, limit=limit
    )
    return [
        HiringManagerResponse.model_validate(hm) for hm in hiring_managers
    ]


# @router.patch(
#     "/{hiring_manager_id}",
#     response_model=HiringManagerResponse,
#     summary="Update hiring manager",
#     description="Update hiring manager profile fields.",
# )
# async def update_hiring_manager(
#     hiring_manager_id: uuid.UUID,
#     update_data: HiringManagerUpdate,
#     db: AsyncSession = Depends(get_db),
# ) -> HiringManagerResponse:
#     """Update hiring manager.
#
#     Args:
#         hiring_manager_id: Hiring manager UUID.
#         update_data: Fields to update.
#         db: Database session.
#
#     Returns:
#         HiringManagerResponse: Updated hiring manager.
#
#     Raises:
#         HTTPException: If hiring manager not found.
#     """
#     hiring_manager = await HiringManagerService.get_hiring_manager_by_id(
#         db, hiring_manager_id
#     )
#     if not hiring_manager:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Hiring manager with id {hiring_manager_id} not found",
#         )
#
#     updated_manager = await HiringManagerService.update_hiring_manager(
#         db, hiring_manager, update_data
#     )
#     return HiringManagerResponse.model_validate(updated_manager)


@router.delete(
    "/{hiring_manager_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete hiring manager",
    description="Delete hiring manager profile. All associated vacancies will be deleted (CASCADE).",
)
async def delete_hiring_manager(
    hiring_manager_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete hiring manager.

    Args:
        hiring_manager_id: Hiring manager UUID.
        db: Database session.

    Raises:
        HTTPException: If hiring manager not found.
    """
    hiring_manager = await HiringManagerService.get_hiring_manager_by_id(
        db, hiring_manager_id
    )
    if not hiring_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hiring manager with id {hiring_manager_id} not found",
        )

    await HiringManagerService.delete_hiring_manager(db, hiring_manager)


# =============================================================================
# NOT IMPLEMENTED YET - Endpoints for future features
# =============================================================================

@router.post(
    "/me/magic-schedule-link",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Generate magic link for calendar setup (NOT IMPLEMENTED)",
    description=(
        "Generate magic link for HM to set up their availability slots via Calendly.\n\n"
        "This endpoint will be implemented later with Calendly integration."
    ),
)
async def generate_magic_schedule_link(
    hiring_manager_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate magic link for calendar setup.

    NOT IMPLEMENTED YET - requires Calendly integration.

    Should return:
    {
        "availability_url": "https://our-domain/hm/availability/<token>"
    }
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Magic schedule link generation not implemented yet. Will be available with Calendly integration.",
    )


@router.get(
    "/{hiring_manager_id}/availability-slots",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Get HM availability slots (NOT IMPLEMENTED)",
    description="Get hiring manager's available time slots for interviews. Requires Calendly integration.",
)
async def get_availability_slots(
    hiring_manager_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get availability slots.

    NOT IMPLEMENTED YET - requires Calendly integration.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Availability slots retrieval not implemented yet. Will be available with Calendly integration.",
    )
