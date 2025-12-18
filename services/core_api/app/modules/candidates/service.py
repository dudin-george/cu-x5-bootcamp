"""Candidates service with business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.candidates.models import Candidate
from app.modules.candidates.schemas import (
    CandidateCreate,
    CandidateUpdate,
)


class CandidateService:
    """Service for managing candidate profiles."""

    @staticmethod
    async def create_candidate(
        db: AsyncSession,
        candidate_data: CandidateCreate,
    ) -> Candidate:
        """Create a new candidate.

        Args:
            db: Database session.
            candidate_data: Candidate creation data.

        Returns:
            Candidate: Created candidate.
        """
        candidate = Candidate(
            telegram_id=candidate_data.telegram_id,
            full_name=candidate_data.full_name,
            phone=candidate_data.phone,
            location=candidate_data.location,
            preferred_tracks=candidate_data.preferred_tracks,
        )
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)
        return candidate

    @staticmethod
    async def get_candidate_by_id(
        db: AsyncSession,
        candidate_id: uuid.UUID,
    ) -> Candidate | None:
        """Get candidate by ID.

        Args:
            db: Database session.
            candidate_id: Candidate UUID.

        Returns:
            Candidate | None: Candidate or None if not found.
        """
        result = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_candidate_by_telegram_id(
        db: AsyncSession,
        telegram_id: int,
    ) -> Candidate | None:
        """Get candidate by Telegram ID.

        Args:
            db: Database session.
            telegram_id: Telegram user ID.

        Returns:
            Candidate | None: Candidate or None if not found.
        """
        result = await db.execute(
            select(Candidate).where(Candidate.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_candidates(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Candidate]:
        """Get all candidates with pagination.

        Args:
            db: Database session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            list[Candidate]: List of candidates.
        """
        result = await db.execute(
            select(Candidate).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_candidate(
        db: AsyncSession,
        candidate: Candidate,
        update_data: CandidateUpdate,
    ) -> Candidate:
        """Update candidate.

        Args:
            db: Database session.
            candidate: Candidate to update.
            update_data: Update data.

        Returns:
            Candidate: Updated candidate.
        """
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(candidate, field, value)

        await db.commit()
        await db.refresh(candidate)
        return candidate

    @staticmethod
    async def delete_candidate(
        db: AsyncSession,
        candidate: Candidate,
    ) -> None:
        """Delete candidate.

        Args:
            db: Database session.
            candidate: Candidate to delete.
        """
        await db.delete(candidate)
        await db.commit()
