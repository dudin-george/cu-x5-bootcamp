"""Vacancies service with business logic."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.candidates.models import Candidate
from app.modules.vacancies.models import CandidatePool, InterviewFeedback, Track, Vacancy
from app.modules.vacancies.schemas import (
    CandidatePoolCreate,
    CandidatePoolUpdate,
    InterviewFeedbackCreate,
    TrackCreate,
    TrackUpdate,
    VacancyCreate,
    VacancyUpdate,
)
from app.shared.enums import CandidatePoolStatus, VacancyStatus


class TrackService:
    """Service for managing tracks."""

    @staticmethod
    async def create_track(db: AsyncSession, track_data: TrackCreate) -> Track:
        """Create a new track."""
        track = Track(
            name=track_data.name,
            description=track_data.description,
            is_active=track_data.is_active,
        )
        db.add(track)
        await db.commit()
        await db.refresh(track)
        return track

    @staticmethod
    async def get_track_by_id(db: AsyncSession, track_id: int) -> Track | None:
        """Get track by ID."""
        result = await db.execute(select(Track).where(Track.id == track_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_tracks(
        db: AsyncSession, skip: int = 0, limit: int = 100, active_only: bool = False
    ) -> list[Track]:
        """Get all tracks with optional filtering."""
        query = select(Track)
        if active_only:
            query = query.where(Track.is_active == True)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_track(
        db: AsyncSession, track: Track, update_data: TrackUpdate
    ) -> Track:
        """Update track."""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(track, field, value)
        await db.commit()
        await db.refresh(track)
        return track

    @staticmethod
    async def delete_track(db: AsyncSession, track: Track) -> None:
        """Delete track."""
        await db.delete(track)
        await db.commit()


class VacancyService:
    """Service for managing vacancies."""

    @staticmethod
    async def create_vacancy(db: AsyncSession, vacancy_data: VacancyCreate) -> Vacancy:
        """Create a new vacancy (always starts as DRAFT) and create approval task."""
        from app.modules.hiring_managers.models import HiringManager
        from app.modules.tasks.service import TaskService

        vacancy = Vacancy(
            track_id=vacancy_data.track_id,
            hiring_manager_id=vacancy_data.hiring_manager_id,
            description=vacancy_data.description,
            status=VacancyStatus.DRAFT,
        )
        db.add(vacancy)
        await db.commit()
        await db.refresh(vacancy)

        # Load track and hiring manager for task context
        track_result = await db.execute(select(Track).where(Track.id == vacancy.track_id))
        track = track_result.scalar_one()

        hm_result = await db.execute(select(HiringManager).where(HiringManager.id == vacancy.hiring_manager_id))
        hiring_manager = hm_result.scalar_one()

        # Create approval task
        await TaskService.create_vacancy_approval_task(
            db=db,
            vacancy_id=vacancy.id,
            vacancy_description=vacancy.description,
            track_name=track.name,
            hiring_manager_name=f"{hiring_manager.first_name} {hiring_manager.last_name}",
        )

        return vacancy

    @staticmethod
    async def get_vacancy_by_id(db: AsyncSession, vacancy_id: int) -> Vacancy | None:
        """Get vacancy by ID."""
        result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_vacancies(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: VacancyStatus | None = None,
        track_id: int | None = None,
        hiring_manager_id: uuid.UUID | None = None,
    ) -> list[Vacancy]:
        """Get all vacancies with optional filtering."""
        query = select(Vacancy)
        if status:
            query = query.where(Vacancy.status == status)
        if track_id:
            query = query.where(Vacancy.track_id == track_id)
        if hiring_manager_id:
            query = query.where(Vacancy.hiring_manager_id == hiring_manager_id)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_vacancy(
        db: AsyncSession, vacancy: Vacancy, update_data: VacancyUpdate
    ) -> Vacancy:
        """Update vacancy."""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(vacancy, field, value)
        await db.commit()
        await db.refresh(vacancy)
        return vacancy

    @staticmethod
    async def activate_vacancy(db: AsyncSession, vacancy: Vacancy) -> Vacancy:
        """Activate vacancy (change status from DRAFT to ACTIVE)."""
        vacancy.status = VacancyStatus.ACTIVE
        await db.commit()
        await db.refresh(vacancy)
        return vacancy

    @staticmethod
    async def abort_vacancy(db: AsyncSession, vacancy: Vacancy) -> Vacancy:
        """Abort vacancy (change status to ABORTED)."""
        vacancy.status = VacancyStatus.ABORTED
        await db.commit()
        await db.refresh(vacancy)
        return vacancy

    @staticmethod
    async def delete_vacancy(db: AsyncSession, vacancy: Vacancy) -> None:
        """Delete vacancy."""
        await db.delete(vacancy)
        await db.commit()


class CandidatePoolService:
    """Service for managing candidate pools (candidate-vacancy relationships)."""

    @staticmethod
    async def add_to_pool(
        db: AsyncSession, vacancy_id: int, pool_data: CandidatePoolCreate
    ) -> CandidatePool:
        """Add candidate to vacancy pool."""
        pool_entry = CandidatePool(
            vacancy_id=vacancy_id,
            candidate_id=pool_data.candidate_id,
            status=pool_data.status,
            notes=pool_data.notes,
        )
        db.add(pool_entry)
        await db.commit()
        await db.refresh(pool_entry)
        return pool_entry

    @staticmethod
    async def get_pool_entry_by_id(
        db: AsyncSession, pool_id: uuid.UUID
    ) -> CandidatePool | None:
        """Get candidate pool entry by ID."""
        result = await db.execute(
            select(CandidatePool).where(CandidatePool.id == pool_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_pool_entry_by_vacancy_and_candidate(
        db: AsyncSession, vacancy_id: int, candidate_id: uuid.UUID
    ) -> CandidatePool | None:
        """Get candidate pool entry by vacancy and candidate IDs."""
        result = await db.execute(
            select(CandidatePool).where(
                CandidatePool.vacancy_id == vacancy_id,
                CandidatePool.candidate_id == candidate_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_candidates_by_vacancy(
        db: AsyncSession,
        vacancy_id: int,
        status: CandidatePoolStatus | None = None,
    ) -> list[CandidatePool]:
        """Get all candidates for a vacancy, optionally filtered by status."""
        query = select(CandidatePool).where(CandidatePool.vacancy_id == vacancy_id)
        if status:
            query = query.where(CandidatePool.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_candidates_by_vacancy_with_details(
        db: AsyncSession,
        vacancy_id: int,
        status: CandidatePoolStatus | None = None,
    ) -> list[tuple[CandidatePool, Candidate]]:
        """Get candidates for vacancy with full candidate details."""
        query = (
            select(CandidatePool, Candidate)
            .join(Candidate, CandidatePool.candidate_id == Candidate.id)
            .where(CandidatePool.vacancy_id == vacancy_id)
        )
        if status:
            query = query.where(CandidatePool.status == status)
        result = await db.execute(query)
        return list(result.all())

    @staticmethod
    async def update_pool_entry(
        db: AsyncSession, pool_entry: CandidatePool, update_data: CandidatePoolUpdate
    ) -> CandidatePool:
        """Update candidate pool entry."""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(pool_entry, field, value)
        await db.commit()
        await db.refresh(pool_entry)
        return pool_entry

    @staticmethod
    async def remove_candidate_from_pool(
        db: AsyncSession, pool_entry: CandidatePool
    ) -> None:
        """Remove candidate from vacancy pool."""
        await db.delete(pool_entry)
        await db.commit()

    @staticmethod
    async def get_next_unviewed_candidate(
        db: AsyncSession, vacancy_id: int
    ) -> Candidate | None:
        """Get next candidate who hasn't been viewed for this vacancy yet.

        Uses efficient NOT IN subquery to find candidates not in the pool.
        """
        # Subquery: all candidate IDs already in this vacancy's pool
        subquery = (
            select(CandidatePool.candidate_id)
            .where(CandidatePool.vacancy_id == vacancy_id)
            .scalar_subquery()
        )

        # Main query: find first candidate NOT in the pool
        query = (
            select(Candidate)
            .where(Candidate.id.not_in(subquery))
            .limit(1)
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_candidate_with_status(
        db: AsyncSession,
        vacancy_id: int,
        candidate_id: uuid.UUID,
        status: CandidatePoolStatus,
        notes: str | None = None,
    ) -> CandidatePool:
        """Add candidate to pool with specific status.

        Helper method for action endpoints (select, skip, reject).
        """
        pool_entry = CandidatePool(
            vacancy_id=vacancy_id,
            candidate_id=candidate_id,
            status=status,
            notes=notes,
        )
        db.add(pool_entry)
        await db.commit()
        await db.refresh(pool_entry)
        return pool_entry

    @staticmethod
    async def get_vacancy_stats(
        db: AsyncSession, vacancy_id: int
    ) -> dict[str, int]:
        """Get statistics for vacancy by candidate statuses.

        Returns dict with counts for each status.
        """
        # Count candidates by status
        query = (
            select(
                CandidatePool.status,
                func.count(CandidatePool.id).label("count")
            )
            .where(CandidatePool.vacancy_id == vacancy_id)
            .group_by(CandidatePool.status)
        )

        result = await db.execute(query)
        status_counts = {row.status: row.count for row in result.all()}

        # Build response with all statuses (0 if not present)
        return {
            "vacancy_id": vacancy_id,
            "total_candidates": sum(status_counts.values()),
            "viewed": status_counts.get(CandidatePoolStatus.VIEWED, 0),
            "selected": status_counts.get(CandidatePoolStatus.SELECTED, 0),
            "interview_scheduled": status_counts.get(CandidatePoolStatus.INTERVIEW_SCHEDULED, 0),
            "interviewed": status_counts.get(CandidatePoolStatus.INTERVIEWED, 0),
            "finalist": status_counts.get(CandidatePoolStatus.FINALIST, 0),
            "offer_sent": status_counts.get(CandidatePoolStatus.OFFER_SENT, 0),
            "rejected": status_counts.get(CandidatePoolStatus.REJECTED, 0),
        }


class InterviewFeedbackService:
    """Service for managing interview feedback."""

    @staticmethod
    async def create_feedback(
        db: AsyncSession,
        pool_id: uuid.UUID,
        feedback_data: InterviewFeedbackCreate
    ) -> InterviewFeedback:
        """Create interview feedback and update candidate status based on decision."""
        # Create feedback
        feedback = InterviewFeedback(
            pool_id=pool_id,
            feedback_text=feedback_data.feedback_text,
            decision=feedback_data.decision,
        )
        db.add(feedback)

        # Get pool entry to update status
        pool_entry = await CandidatePoolService.get_pool_entry_by_id(db, pool_id)
        if pool_entry:
            # Update status based on decision
            if feedback_data.decision == "to_finalist":
                pool_entry.status = CandidatePoolStatus.FINALIST
            elif feedback_data.decision in ["reject_globally", "reject_team"]:
                pool_entry.status = CandidatePoolStatus.REJECTED
            # "freeze" keeps status as INTERVIEWED

        await db.commit()
        await db.refresh(feedback)
        return feedback

    @staticmethod
    async def get_feedback_by_pool_id(
        db: AsyncSession, pool_id: uuid.UUID
    ) -> InterviewFeedback | None:
        """Get feedback by pool entry ID."""
        result = await db.execute(
            select(InterviewFeedback).where(InterviewFeedback.pool_id == pool_id)
        )
        return result.scalar_one_or_none()
