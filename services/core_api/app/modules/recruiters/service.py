"""Recruiter service layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recruiters.models import Recruiter
from app.modules.recruiters.schemas import RecruiterCreate


class RecruiterService:
    """Service for managing recruiters."""

    @staticmethod
    async def create_recruiter(
        db: AsyncSession,
        data: RecruiterCreate,
    ) -> Recruiter:
        """Create a new recruiter.

        Args:
            db: Database session.
            data: Recruiter creation data.

        Returns:
            Recruiter: Created recruiter.
        """
        recruiter = Recruiter(
            full_name=data.full_name,
        )
        db.add(recruiter)
        await db.commit()
        await db.refresh(recruiter)
        return recruiter

    @staticmethod
    async def get_recruiter_by_id(
        db: AsyncSession,
        recruiter_id: int,
    ) -> Recruiter | None:
        """Get recruiter by ID.

        Args:
            db: Database session.
            recruiter_id: Recruiter ID.

        Returns:
            Recruiter | None: Recruiter if found.
        """
        result = await db.execute(
            select(Recruiter).where(Recruiter.id == recruiter_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_recruiters(
        db: AsyncSession,
    ) -> list[Recruiter]:
        """Get all recruiters.

        Args:
            db: Database session.

        Returns:
            list[Recruiter]: List of recruiters.
        """
        result = await db.execute(
            select(Recruiter).order_by(Recruiter.full_name)
        )
        return list(result.scalars().all())
