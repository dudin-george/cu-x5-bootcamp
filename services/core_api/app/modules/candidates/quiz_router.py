"""Quiz API router - candidate quiz endpoints."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.quiz.models import QuizBlock
from app.modules.quiz.schemas import (
    QuestionOption,
    QuestionResponse,
    QuizAnswerRequest,
    QuizAnswerResponse,
    QuizAttemptResponse,
    QuizAttemptsResponse,
    QuizContinueResponse,
    QuizEndResponse,
    QuizStartRequest,
    QuizStartResponse,
)
from app.modules.quiz.service import (
    QuizAnswerService,
    QuizFlowService,
    QuizQuestionService,
    QuizSessionService,
    TrackQuizBlockService,
)
from app.modules.vacancies.service import VacancyService

router = APIRouter()


def format_question(
    question,
    block_name: str,
    question_number: int,
) -> QuestionResponse:
    """Format question for response.

    Args:
        question: QuizQuestion model.
        block_name: Block name.
        question_number: Sequential number.

    Returns:
        QuestionResponse: Formatted question.
    """
    return QuestionResponse(
        id=question.id,
        text=question.question_text,
        block_name=block_name,
        options=[
            QuestionOption(key="A", text=question.option_a),
            QuestionOption(key="B", text=question.option_b),
            QuestionOption(key="C", text=question.option_c),
            QuestionOption(key="D", text=question.option_d),
        ],
        question_number=question_number,
    )


@router.post(
    "/start",
    response_model=QuizStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Start quiz session",
    description=(
        "Start a new quiz session for a candidate on a specific track.\\n\\n"
        "Creates a 15-minute quiz session and returns the first question."
    ),
)
async def start_quiz(
    request: QuizStartRequest,
    db: AsyncSession = Depends(get_db),
) -> QuizStartResponse:
    """Start quiz session.

    Args:
        request: Quiz start request.
        db: Database session.

    Returns:
        QuizStartResponse: Session info with first question.

    Raises:
        HTTPException: If active session exists or track has no questions.
    """
    # Check if active session already exists
    existing = await QuizSessionService.get_active_session(
        db, request.candidate_id, request.track_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active quiz session already exists for this track",
        )

    # Get track blocks configuration
    track_blocks = await TrackQuizBlockService.get_track_blocks(db, request.track_id)
    if not track_blocks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Track {request.track_id} has no quiz blocks configured",
        )

    # Get track name
    track = await VacancyService.get_track_by_id(db, request.track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {request.track_id} not found",
        )

    # Create session
    session = await QuizSessionService.create_session(db, request)

    # Get first question from first block
    first_block = track_blocks[0]
    first_question = await QuizQuestionService.get_random_question_from_block(
        db, first_block.block_id
    )

    if not first_question:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No questions available in block {first_block.block_id}",
        )

    return QuizStartResponse(
        session_id=session.id,
        question=format_question(first_question, first_block.block.name, 1),
    )


@router.post(
    "/answer",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit answer and get next question",
    description=(
        "Submit answer to a question.\\n\\n"
        "Returns next question if quiz continues, or final results if quiz ended."
    ),
)
async def submit_answer(
    request: QuizAnswerRequest,
    db: AsyncSession = Depends(get_db),
) -> QuizContinueResponse | QuizEndResponse:
    """Submit answer and get next question or results.

    Args:
        request: Answer request.
        db: Database session.

    Returns:
        QuizContinueResponse | QuizEndResponse: Next question or results.

    Raises:
        HTTPException: If session or question not found.
    """
    # Get session
    session = await QuizSessionService.get_session_by_id(db, request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz session {request.session_id} not found",
        )

    # Check if session is still active
    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quiz session is {session.status}, cannot submit answers",
        )

    # Check time
    now = datetime.now(timezone.utc)
    time_expired = now >= session.expires_at

    # Get question
    question = await QuizQuestionService.get_question_by_id(db, request.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {request.question_id} not found",
        )

    # Check answer
    is_correct = request.answer == question.correct_answer

    # Save answer
    await QuizAnswerService.save_answer(db, request, is_correct)

    # Update session stats
    await QuizSessionService.update_session_stats(db, request.session_id, is_correct)

    # Refresh session to get updated stats
    await db.refresh(session)

    # If time expired, finalize and return results
    if time_expired:
        await QuizSessionService.finalize_session(db, session)
        results = await QuizAnswerService.calculate_results(db, session.id)

        return QuizEndResponse(
            type="end",
            results=results,
        )

    # Get next question
    next_question = await QuizFlowService.get_next_question(db, session)

    # If no more questions, finalize
    if not next_question:
        await QuizSessionService.finalize_session(db, session)
        results = await QuizAnswerService.calculate_results(db, session.id)

        return QuizEndResponse(
            type="end",
            results=results,
        )

    # Quiz continues - get block
    block = await db.get(QuizBlock, next_question.block_id)
    questions_answered = session.total_questions

    return QuizContinueResponse(
        type="continue",
        question=format_question(
            next_question,
            block.name if block else "Unknown",
            questions_answered + 1,
        ),
    )


@router.get(
    "/attempts",
    response_model=QuizAttemptsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get candidate's quiz attempts",
    description="Get all quiz attempts for a candidate, optionally filtered by track.",
)
async def get_quiz_attempts(
    candidate_id: uuid.UUID,
    track_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> QuizAttemptsResponse:
    """Get candidate's quiz attempts.

    Args:
        candidate_id: Candidate UUID.
        track_id: Optional track ID filter.
        db: Database session.

    Returns:
        QuizAttemptsResponse: List of quiz attempts.
    """
    sessions = await QuizSessionService.get_candidate_attempts(
        db, candidate_id, track_id
    )

    # Get track names
    attempts = []
    for session in sessions:
        track = await VacancyService.get_track_by_id(db, session.track_id)
        attempts.append(
            QuizAttemptResponse(
                session_id=session.id,
                track_name=track.name if track else "Unknown",
                started_at=session.started_at,
                ended_at=session.ended_at,
                status=session.status,
                score=float(session.score) if session.score else None,
                total_questions=session.total_questions,
                correct_answers=session.correct_answers,
            )
        )

    return QuizAttemptsResponse(attempts=attempts)
