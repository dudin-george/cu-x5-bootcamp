"""Quiz service layer."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.quiz.models import (
    QuizAnswer,
    QuizBlock,
    QuizQuestion,
    QuizSession,
    TrackQuizBlock,
)
from app.modules.quiz.schemas import (
    BlockPerformance,
    QuizAnswerRequest,
    QuizBlockCreate,
    QuizQuestionCreate,
    QuizResults,
    QuizStartRequest,
    TrackQuizBlockCreate,
)


class QuizBlockService:
    """Service for managing quiz blocks."""

    @staticmethod
    async def create_block(
        db: AsyncSession,
        block_data: QuizBlockCreate,
    ) -> QuizBlock:
        """Create a new quiz block.

        Args:
            db: Database session.
            block_data: Block creation data.

        Returns:
            QuizBlock: Created block.
        """
        block = QuizBlock(
            name=block_data.name,
            description=block_data.description,
            is_active=block_data.is_active,
        )
        db.add(block)
        await db.commit()
        await db.refresh(block)
        return block

    @staticmethod
    async def get_block_by_id(
        db: AsyncSession,
        block_id: int,
    ) -> QuizBlock | None:
        """Get block by ID.

        Args:
            db: Database session.
            block_id: Block ID.

        Returns:
            QuizBlock | None: Block if found.
        """
        result = await db.execute(
            select(QuizBlock).where(QuizBlock.id == block_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_blocks(
        db: AsyncSession,
        is_active: bool | None = None,
    ) -> list[QuizBlock]:
        """Get all quiz blocks.

        Args:
            db: Database session.
            is_active: Filter by active status.

        Returns:
            list[QuizBlock]: List of blocks.
        """
        query = select(QuizBlock)
        if is_active is not None:
            query = query.where(QuizBlock.is_active == is_active)

        result = await db.execute(query.order_by(QuizBlock.name))
        return list(result.scalars().all())


class TrackQuizBlockService:
    """Service for managing track-block associations."""

    @staticmethod
    async def link_track_to_block(
        db: AsyncSession,
        data: TrackQuizBlockCreate,
    ) -> TrackQuizBlock:
        """Link track with quiz block.

        Args:
            db: Database session.
            data: Association data.

        Returns:
            TrackQuizBlock: Created association.
        """
        association = TrackQuizBlock(
            track_id=data.track_id,
            block_id=data.block_id,
            questions_count=data.questions_count,
        )
        db.add(association)
        await db.commit()
        await db.refresh(association)
        return association

    @staticmethod
    async def get_track_blocks(
        db: AsyncSession,
        track_id: int,
    ) -> list[TrackQuizBlock]:
        """Get all blocks for a track.

        Args:
            db: Database session.
            track_id: Track ID.

        Returns:
            list[TrackQuizBlock]: List of track-block associations.
        """
        result = await db.execute(
            select(TrackQuizBlock)
            .options(joinedload(TrackQuizBlock.block))
            .where(TrackQuizBlock.track_id == track_id)
        )
        return list(result.scalars().all())


class QuizQuestionService:
    """Service for managing quiz questions."""

    @staticmethod
    async def create_question(
        db: AsyncSession,
        question_data: QuizQuestionCreate,
    ) -> QuizQuestion:
        """Create a new quiz question.

        Args:
            db: Database session.
            question_data: Question creation data.

        Returns:
            QuizQuestion: Created question.
        """
        question = QuizQuestion(
            block_id=question_data.block_id,
            question_text=question_data.question_text,
            option_a=question_data.option_a,
            option_b=question_data.option_b,
            option_c=question_data.option_c,
            option_d=question_data.option_d,
            correct_answer=question_data.correct_answer,
            difficulty=question_data.difficulty,
            is_active=question_data.is_active,
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def get_question_by_id(
        db: AsyncSession,
        question_id: uuid.UUID,
    ) -> QuizQuestion | None:
        """Get question by ID.

        Args:
            db: Database session.
            question_id: Question UUID.

        Returns:
            QuizQuestion | None: Question if found.
        """
        result = await db.execute(
            select(QuizQuestion).where(QuizQuestion.id == question_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_random_question_from_block(
        db: AsyncSession,
        block_id: int,
        exclude_ids: list[uuid.UUID] | None = None,
    ) -> QuizQuestion | None:
        """Get random question from block.

        Args:
            db: Database session.
            block_id: Block ID.
            exclude_ids: Question IDs to exclude.

        Returns:
            QuizQuestion | None: Random question if found.
        """
        query = select(QuizQuestion).where(
            QuizQuestion.block_id == block_id,
            QuizQuestion.is_active == True,
        )

        if exclude_ids:
            query = query.where(QuizQuestion.id.notin_(exclude_ids))

        query = query.order_by(func.random()).limit(1)

        result = await db.execute(query)
        return result.scalar_one_or_none()


class QuizSessionService:
    """Service for managing quiz sessions."""

    @staticmethod
    async def create_session(
        db: AsyncSession,
        request: QuizStartRequest,
    ) -> QuizSession:
        """Create a new quiz session.

        Args:
            db: Database session.
            request: Quiz start request.

        Returns:
            QuizSession: Created session.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=15)  # TODO: Change back to minutes=15 after testing

        session = QuizSession(
            candidate_id=request.candidate_id,
            track_id=request.track_id,
            status="in_progress",
            started_at=now,
            expires_at=expires_at,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session_by_id(
        db: AsyncSession,
        session_id: uuid.UUID,
    ) -> QuizSession | None:
        """Get session by ID.

        Args:
            db: Database session.
            session_id: Session UUID.

        Returns:
            QuizSession | None: Session if found.
        """
        result = await db.execute(
            select(QuizSession).where(QuizSession.id == session_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_session(
        db: AsyncSession,
        candidate_id: uuid.UUID,
        track_id: int,
    ) -> QuizSession | None:
        """Get active session for candidate and track.

        Args:
            db: Database session.
            candidate_id: Candidate UUID.
            track_id: Track ID.

        Returns:
            QuizSession | None: Active session if found.
        """
        result = await db.execute(
            select(QuizSession).where(
                QuizSession.candidate_id == candidate_id,
                QuizSession.track_id == track_id,
                QuizSession.status == "in_progress",
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def finalize_session(
        db: AsyncSession,
        session: QuizSession,
    ) -> QuizSession:
        """Finalize quiz session.

        Args:
            db: Database session.
            session: Session to finalize.

        Returns:
            QuizSession: Finalized session.
        """
        now = datetime.now(timezone.utc)

        # Calculate score
        total = session.total_questions
        correct = session.correct_answers
        score = (correct / total * 100.0) if total > 0 else 0.0

        session.status = "completed"
        session.ended_at = now
        session.score = score

        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def update_session_stats(
        db: AsyncSession,
        session_id: uuid.UUID,
        is_correct: bool,
    ) -> None:
        """Update session statistics.

        Args:
            db: Database session.
            session_id: Session UUID.
            is_correct: Whether the answer was correct.
        """
        session = await QuizSessionService.get_session_by_id(db, session_id)
        if session:
            session.total_questions += 1
            if is_correct:
                session.correct_answers += 1
            else:
                session.wrong_answers += 1
            await db.commit()

    @staticmethod
    async def get_candidate_attempts(
        db: AsyncSession,
        candidate_id: uuid.UUID,
        track_id: int | None = None,
    ) -> list[QuizSession]:
        """Get candidate's quiz attempts.

        Args:
            db: Database session.
            candidate_id: Candidate UUID.
            track_id: Optional track ID filter.

        Returns:
            list[QuizSession]: List of quiz sessions.
        """
        query = select(QuizSession).where(
            QuizSession.candidate_id == candidate_id
        )

        if track_id is not None:
            query = query.where(QuizSession.track_id == track_id)

        query = query.order_by(QuizSession.started_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())


class QuizAnswerService:
    """Service for managing quiz answers."""

    @staticmethod
    async def save_answer(
        db: AsyncSession,
        request: QuizAnswerRequest,
        is_correct: bool,
    ) -> QuizAnswer:
        """Save quiz answer.

        Args:
            db: Database session.
            request: Answer request.
            is_correct: Whether the answer is correct.

        Returns:
            QuizAnswer: Saved answer.
        """
        answer = QuizAnswer(
            session_id=request.session_id,
            question_id=request.question_id,
            candidate_answer=request.answer,
            is_correct=is_correct,
        )
        db.add(answer)
        await db.commit()
        await db.refresh(answer)
        return answer

    @staticmethod
    async def get_answered_question_ids(
        db: AsyncSession,
        session_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        """Get list of question IDs already answered in session.

        Args:
            db: Database session.
            session_id: Session UUID.

        Returns:
            list[uuid.UUID]: List of question IDs.
        """
        result = await db.execute(
            select(QuizAnswer.question_id).where(
                QuizAnswer.session_id == session_id
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_block_questions_in_session(
        db: AsyncSession,
        session_id: uuid.UUID,
        block_id: int,
    ) -> int:
        """Count questions from specific block answered in session.

        Args:
            db: Database session.
            session_id: Session UUID.
            block_id: Block ID.

        Returns:
            int: Count of questions from this block.
        """
        result = await db.execute(
            select(func.count(QuizAnswer.id))
            .join(QuizQuestion)
            .where(
                QuizAnswer.session_id == session_id,
                QuizQuestion.block_id == block_id,
            )
        )
        return result.scalar_one()

    @staticmethod
    async def calculate_results(
        db: AsyncSession,
        session_id: uuid.UUID,
    ) -> QuizResults:
        """Calculate quiz results with block performance.

        Args:
            db: Database session.
            session_id: Session UUID.

        Returns:
            QuizResults: Detailed quiz results.
        """
        session = await QuizSessionService.get_session_by_id(db, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Get block performance
        result = await db.execute(
            select(
                QuizBlock.name,
                func.count(QuizAnswer.id).label("total"),
                func.sum(func.cast(QuizAnswer.is_correct, Integer)).label("correct"),
            )
            .join(QuizQuestion, QuizAnswer.question_id == QuizQuestion.id)
            .join(QuizBlock, QuizQuestion.block_id == QuizBlock.id)
            .where(QuizAnswer.session_id == session_id)
            .group_by(QuizBlock.name)
        )

        blocks_performance = []
        for row in result.all():
            block_name = row[0]
            total = row[1]
            correct = row[2] or 0
            accuracy = (correct / total * 100.0) if total > 0 else 0.0

            blocks_performance.append(
                BlockPerformance(
                    block_name=block_name,
                    correct=correct,
                    total=total,
                    accuracy=round(accuracy, 2),
                )
            )

        # Calculate completion time
        completion_time = 0
        if session.ended_at and session.started_at:
            completion_time = int((session.ended_at - session.started_at).total_seconds())

        return QuizResults(
            session_id=session.id,
            total_questions=session.total_questions,
            correct_answers=session.correct_answers,
            wrong_answers=session.wrong_answers,
            accuracy=float(session.score) if session.score else 0.0,
            completion_time_seconds=completion_time,
            blocks_performance=blocks_performance,
        )


class QuizFlowService:
    """Service for managing quiz flow logic."""

    @staticmethod
    async def get_next_question(
        db: AsyncSession,
        session: QuizSession,
    ) -> QuizQuestion | None:
        """Get next question for quiz session.

        Args:
            db: Database session.
            session: Quiz session.

        Returns:
            QuizQuestion | None: Next question or None if all done.
        """
        # Get track blocks configuration
        track_blocks = await TrackQuizBlockService.get_track_blocks(
            db, session.track_id
        )

        # Get already answered questions
        answered_ids = await QuizAnswerService.get_answered_question_ids(
            db, session.id
        )

        # For each block, check if we need more questions
        for track_block in track_blocks:
            block_id = track_block.block_id
            required_count = track_block.questions_count

            # Count questions from this block already answered
            block_answered = await QuizAnswerService.count_block_questions_in_session(
                db, session.id, block_id
            )

            if block_answered < required_count:
                # Need more questions from this block
                question = await QuizQuestionService.get_random_question_from_block(
                    db, block_id, exclude_ids=answered_ids
                )
                if question:
                    return question

        # All questions from all blocks exhausted
        return None
