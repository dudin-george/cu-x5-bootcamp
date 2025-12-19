"""Quiz admin router - temporary endpoints for seeding data."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.quiz.models import QuizBlock
from app.modules.quiz.schemas import (
    QuizBlockCreate,
    QuizBlockResponse,
    QuizQuestionCreate,
    QuizQuestionResponse,
    TrackQuizBlockCreate,
    TrackQuizBlockResponse,
)
from app.modules.quiz.service import (
    QuizBlockService,
    QuizQuestionService,
    TrackQuizBlockService,
)

router = APIRouter()


@router.post(
    "/blocks",
    response_model=QuizBlockResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create quiz block",
    description="Create a new quiz block (e.g., Algorithms, Python, etc.)",
)
async def create_block(
    data: QuizBlockCreate,
    db: AsyncSession = Depends(get_db),
) -> QuizBlockResponse:
    """Create quiz block."""
    block = await QuizBlockService.create_block(db, data)

    return QuizBlockResponse(
        id=block.id,
        name=block.name,
        description=block.description,
        is_active=block.is_active,
        created_at=block.created_at,
        updated_at=block.updated_at,
    )


@router.get(
    "/blocks",
    response_model=list[QuizBlockResponse],
    status_code=status.HTTP_200_OK,
    summary="List quiz blocks",
    description="Get all quiz blocks",
)
async def list_blocks(
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[QuizBlockResponse]:
    """List all quiz blocks."""
    blocks = await QuizBlockService.get_all_blocks(db, is_active)

    return [
        QuizBlockResponse(
            id=block.id,
            name=block.name,
            description=block.description,
            is_active=block.is_active,
            created_at=block.created_at,
            updated_at=block.updated_at,
        )
        for block in blocks
    ]


@router.post(
    "/questions",
    response_model=QuizQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create quiz question",
    description="Add a new question to a quiz block",
)
async def create_question(
    data: QuizQuestionCreate,
    db: AsyncSession = Depends(get_db),
) -> QuizQuestionResponse:
    """Create quiz question."""
    # Check that block exists
    block = await QuizBlockService.get_block_by_id(db, data.block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz block {data.block_id} not found",
        )

    question = await QuizQuestionService.create_question(db, data)

    return QuizQuestionResponse(
        id=question.id,
        block_id=question.block_id,
        block_name=block.name,
        question_text=question.question_text,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_answer=question.correct_answer,
        difficulty=question.difficulty,
        is_active=question.is_active,
        created_at=question.created_at,
        updated_at=question.updated_at,
    )


@router.post(
    "/track-blocks",
    response_model=TrackQuizBlockResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link track with quiz block",
    description="Associate a track with a quiz block and specify question count",
)
async def link_track_block(
    data: TrackQuizBlockCreate,
    db: AsyncSession = Depends(get_db),
) -> TrackQuizBlockResponse:
    """Link track with quiz block."""
    # Check that block exists
    block = await QuizBlockService.get_block_by_id(db, data.block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz block {data.block_id} not found",
        )

    association = await TrackQuizBlockService.link_track_to_block(db, data)

    return TrackQuizBlockResponse(
        track_id=association.track_id,
        block_id=association.block_id,
        block_name=block.name,
        questions_count=association.questions_count,
    )


@router.get(
    "/tracks/{track_id}/blocks",
    response_model=list[TrackQuizBlockResponse],
    status_code=status.HTTP_200_OK,
    summary="Get track's quiz blocks",
    description="Get all quiz blocks configured for a track",
)
async def get_track_blocks(
    track_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[TrackQuizBlockResponse]:
    """Get track's quiz blocks."""
    associations = await TrackQuizBlockService.get_track_blocks(db, track_id)

    return [
        TrackQuizBlockResponse(
            track_id=assoc.track_id,
            block_id=assoc.block_id,
            block_name=assoc.block.name,
            questions_count=assoc.questions_count,
        )
        for assoc in associations
    ]
