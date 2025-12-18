"""Hiring Managers module business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hiring_managers.models import HiringManager
from app.modules.hiring_managers.schemas import HiringManagerCreate, HiringManagerUpdate


class HiringManagerService:
    """Service for managing hiring managers."""

    @staticmethod
    async def create_hiring_manager(
        db: AsyncSession,
        hiring_manager_data: HiringManagerCreate,
    ) -> HiringManager:
        """Create a new hiring manager.

        Args:
            db: Database session.
            hiring_manager_data: Hiring manager creation data.

        Returns:
            HiringManager: Created hiring manager.
        """
        hiring_manager = HiringManager(
            telegram_id=hiring_manager_data.telegram_id,
            first_name=hiring_manager_data.first_name,
            last_name=hiring_manager_data.last_name,
            calendly_id=hiring_manager_data.calendly_id,
        )
        db.add(hiring_manager)
        await db.commit()
        await db.refresh(hiring_manager)
        return hiring_manager

    @staticmethod
    async def get_hiring_manager_by_id(
        db: AsyncSession,
        hiring_manager_id: uuid.UUID,
    ) -> HiringManager | None:
        """Get hiring manager by ID.

        Args:
            db: Database session.
            hiring_manager_id: Hiring manager UUID.

        Returns:
            HiringManager | None: Hiring manager or None if not found.
        """
        result = await db.execute(
            select(HiringManager).where(HiringManager.id == hiring_manager_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_hiring_manager_by_telegram_id(
        db: AsyncSession,
        telegram_id: int,
    ) -> HiringManager | None:
        """Get hiring manager by Telegram ID.

        Args:
            db: Database session.
            telegram_id: Telegram user ID.

        Returns:
            HiringManager | None: Hiring manager or None if not found.
        """
        result = await db.execute(
            select(HiringManager).where(HiringManager.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_hiring_managers(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[HiringManager]:
        """Get all hiring managers with pagination.

        Args:
            db: Database session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            list[HiringManager]: List of hiring managers.
        """
        result = await db.execute(
            select(HiringManager).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_hiring_manager(
        db: AsyncSession,
        hiring_manager: HiringManager,
        update_data: HiringManagerUpdate,
    ) -> HiringManager:
        """Update hiring manager.

        Args:
            db: Database session.
            hiring_manager: Hiring manager to update.
            update_data: Update data.

        Returns:
            HiringManager: Updated hiring manager.
        """
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(hiring_manager, field, value)

        await db.commit()
        await db.refresh(hiring_manager)
        return hiring_manager

    @staticmethod
    async def delete_hiring_manager(
        db: AsyncSession,
        hiring_manager: HiringManager,
    ) -> None:
        """Delete hiring manager.

        Args:
            db: Database session.
            hiring_manager: Hiring manager to delete.
        """
        await db.delete(hiring_manager)
        await db.commit()
