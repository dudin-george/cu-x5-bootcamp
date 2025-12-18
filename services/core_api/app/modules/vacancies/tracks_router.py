"""Tracks API router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.vacancies.schemas import TrackCreate, TrackResponse, TrackUpdate
from app.modules.vacancies.service import TrackService

router = APIRouter()


@router.post(
    "/",
    response_model=TrackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create track",
    description="Create a new track/direction for vacancies.",
)
async def create_track(
    track_data: TrackCreate,
    db: AsyncSession = Depends(get_db),
) -> TrackResponse:
    """Create a new track.

    Args:
        track_data: Track creation data.
        db: Database session.

    Returns:
        TrackResponse: Created track.
    """
    track = await TrackService.create_track(db, track_data)
    return TrackResponse.model_validate(track)


@router.get(
    "/",
    response_model=list[TrackResponse],
    summary="Get all tracks",
    description="Get list of all tracks with optional active filter.",
)
async def get_all_tracks(
    active_only: bool = Query(False, description="Return only active tracks"),
    db: AsyncSession = Depends(get_db),
) -> list[TrackResponse]:
    """Get all tracks.

    Args:
        active_only: If True, return only active tracks.
        db: Database session.

    Returns:
        list[TrackResponse]: List of tracks.
    """
    tracks = await TrackService.get_all_tracks(db, active_only=active_only)
    return [TrackResponse.model_validate(t) for t in tracks]


@router.get(
    "/{track_id}",
    response_model=TrackResponse,
    summary="Get track by ID",
    description="Get track details by ID.",
)
async def get_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> TrackResponse:
    """Get track by ID.

    Args:
        track_id: Track ID.
        db: Database session.

    Returns:
        TrackResponse: Track details.

    Raises:
        HTTPException: If track not found.
    """
    track = await TrackService.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track with id {track_id} not found",
        )
    return TrackResponse.model_validate(track)


@router.patch(
    "/{track_id}",
    response_model=TrackResponse,
    summary="Update track",
    description="Update track fields.",
)
async def update_track(
    track_id: int,
    update_data: TrackUpdate,
    db: AsyncSession = Depends(get_db),
) -> TrackResponse:
    """Update track.

    Args:
        track_id: Track ID.
        update_data: Fields to update.
        db: Database session.

    Returns:
        TrackResponse: Updated track.

    Raises:
        HTTPException: If track not found.
    """
    track = await TrackService.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track with id {track_id} not found",
        )

    updated_track = await TrackService.update_track(db, track, update_data)
    return TrackResponse.model_validate(updated_track)


@router.delete(
    "/{track_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete track",
    description="Delete track. All associated vacancies will be deleted (CASCADE).",
)
async def delete_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete track.

    Args:
        track_id: Track ID.
        db: Database session.

    Raises:
        HTTPException: If track not found.
    """
    track = await TrackService.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track with id {track_id} not found",
        )

    await TrackService.delete_track(db, track)
