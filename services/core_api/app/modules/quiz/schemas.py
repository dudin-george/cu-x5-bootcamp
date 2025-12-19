"""Quiz module schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# =============================================================================
# Request schemas
# =============================================================================

class QuizStartRequest(BaseModel):
    """Request to start a quiz session."""

    candidate_id: uuid.UUID = Field(..., description="Candidate UUID")
    track_id: int = Field(..., description="Track ID to quiz on")


class QuizAnswerRequest(BaseModel):
    """Request to submit an answer."""

    session_id: uuid.UUID = Field(..., description="Quiz session UUID")
    question_id: uuid.UUID = Field(..., description="Question UUID")
    answer: Literal["A", "B", "C", "D"] = Field(..., description="Selected answer option")


# =============================================================================
# Response schemas - Questions
# =============================================================================

class QuestionOption(BaseModel):
    """Single answer option."""

    key: Literal["A", "B", "C", "D"] = Field(..., description="Option key")
    text: str = Field(..., description="Option text")


class QuestionResponse(BaseModel):
    """Question with options."""

    id: uuid.UUID = Field(..., description="Question UUID")
    text: str = Field(..., description="Question text")
    block_name: str = Field(..., description="Block name (e.g., 'Algorithms')")
    options: list[QuestionOption] = Field(..., description="Answer options (always 4)")
    question_number: int = Field(..., description="Sequential number in quiz (1, 2, 3...)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "text": "Что такое декоратор в Python?",
                "block_name": "Python Basics",
                "options": [
                    {"key": "A", "text": "Функция, которая модифицирует другую функцию"},
                    {"key": "B", "text": "Класс для наследования"},
                    {"key": "C", "text": "Библиотека для UI"},
                    {"key": "D", "text": "Менеджер контекста"}
                ],
                "question_number": 1
            }
        }


# =============================================================================
# Response schemas - Quiz Results
# =============================================================================

class BlockPerformance(BaseModel):
    """Performance in a specific block."""

    block_name: str = Field(..., description="Block name")
    correct: int = Field(..., description="Correct answers in this block")
    total: int = Field(..., description="Total questions from this block")
    accuracy: float = Field(..., description="Accuracy percentage (0-100)")


class QuizResults(BaseModel):
    """Final quiz results."""

    session_id: uuid.UUID = Field(..., description="Quiz session UUID")
    total_questions: int = Field(..., description="Total questions answered")
    correct_answers: int = Field(..., description="Number of correct answers")
    wrong_answers: int = Field(..., description="Number of wrong answers")
    accuracy: float = Field(..., description="Overall accuracy percentage (0-100)")
    completion_time_seconds: int = Field(..., description="Time taken to complete")
    blocks_performance: list[BlockPerformance] = Field(..., description="Performance by block")


# =============================================================================
# Response schemas - Quiz Start
# =============================================================================

class QuizStartResponse(BaseModel):
    """Response when quiz is started."""

    session_id: uuid.UUID = Field(..., description="Quiz session UUID for submitting answers")
    question: QuestionResponse = Field(..., description="First question")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "question": {
                    "id": "660e8400-e29b-41d4-a716-446655440001",
                    "text": "Что такое декоратор в Python?",
                    "block_name": "Python Basics",
                    "options": [
                        {"key": "A", "text": "Функция, которая модифицирует другую функцию"},
                        {"key": "B", "text": "Класс для наследования"},
                        {"key": "C", "text": "Библиотека для UI"},
                        {"key": "D", "text": "Менеджер контекста"}
                    ],
                    "question_number": 1
                }
            }
        }


# =============================================================================
# Response schemas - Quiz Answer (Discriminated Union)
# =============================================================================

class QuizContinueResponse(BaseModel):
    """Response when quiz continues with next question."""

    type: Literal["continue"] = Field("continue", description="Response type: continue")
    question: QuestionResponse = Field(..., description="Next question")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "continue",
                "question": {
                    "id": "770e8400-e29b-41d4-a716-446655440002",
                    "text": "Что вернет list.pop()?",
                    "block_name": "Python Basics",
                    "options": [
                        {"key": "A", "text": "Последний элемент"},
                        {"key": "B", "text": "Первый элемент"},
                        {"key": "C", "text": "None"},
                        {"key": "D", "text": "Ошибку"}
                    ],
                    "question_number": 6
                }
            }
        }


class QuizEndResponse(BaseModel):
    """Response when quiz has ended."""

    type: Literal["end"] = Field("end", description="Response type: end")
    message: str = Field(..., description="Completion message")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "end",
                "message": "Квиз завершен"
            }
        }


# Discriminated Union для ответа на submit answer
QuizAnswerResponse = QuizContinueResponse | QuizEndResponse


# =============================================================================
# Response schemas - Quiz History
# =============================================================================

class QuizAttemptResponse(BaseModel):
    """Single quiz attempt in history."""

    session_id: uuid.UUID = Field(..., description="Session UUID")
    track_name: str = Field(..., description="Track name")
    started_at: datetime = Field(..., description="When quiz started")
    ended_at: datetime | None = Field(None, description="When quiz ended")
    status: Literal["in_progress", "completed", "expired"] = Field(
        ..., description="Session status"
    )
    score: float | None = Field(None, description="Score percentage (0-100)")
    total_questions: int = Field(..., description="Total questions answered")
    correct_answers: int = Field(..., description="Correct answers")


class QuizAttemptsResponse(BaseModel):
    """List of quiz attempts."""

    attempts: list[QuizAttemptResponse] = Field(..., description="Quiz attempts")


# =============================================================================
# Admin schemas (for creating questions)
# =============================================================================

class QuizBlockCreate(BaseModel):
    """Create a quiz block."""

    name: str = Field(..., max_length=255, description="Block name (unique)")
    description: str | None = Field(None, description="Block description")
    is_active: bool = Field(True, description="Is block active")


class QuizBlockResponse(BaseModel):
    """Quiz block response."""

    id: int = Field(..., description="Block ID")
    name: str = Field(..., description="Block name")
    description: str | None = Field(None, description="Block description")
    is_active: bool = Field(..., description="Is block active")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")


class TrackQuizBlockCreate(BaseModel):
    """Link track with quiz block."""

    track_id: int = Field(..., description="Track ID")
    block_id: int = Field(..., description="Block ID")
    questions_count: int = Field(..., ge=1, description="Number of questions from this block")


class TrackQuizBlockResponse(BaseModel):
    """Track-Block association."""

    track_id: int = Field(..., description="Track ID")
    block_id: int = Field(..., description="Block ID")
    block_name: str = Field(..., description="Block name")
    questions_count: int = Field(..., description="Questions count")


class QuizQuestionCreate(BaseModel):
    """Create a quiz question."""

    block_id: int = Field(..., description="Block ID")
    question_text: str = Field(..., description="Question text")
    option_a: str = Field(..., description="Option A text")
    option_b: str = Field(..., description="Option B text")
    option_c: str = Field(..., description="Option C text")
    option_d: str = Field(..., description="Option D text")
    correct_answer: Literal["A", "B", "C", "D"] = Field(..., description="Correct answer")
    difficulty: Literal["easy", "medium", "hard"] = Field("medium", description="Difficulty level")
    is_active: bool = Field(True, description="Is question active")


class QuizQuestionResponse(BaseModel):
    """Quiz question response (admin view with correct answer)."""

    id: uuid.UUID = Field(..., description="Question UUID")
    block_id: int = Field(..., description="Block ID")
    block_name: str = Field(..., description="Block name")
    question_text: str = Field(..., description="Question text")
    option_a: str = Field(..., description="Option A text")
    option_b: str = Field(..., description="Option B text")
    option_c: str = Field(..., description="Option C text")
    option_d: str = Field(..., description="Option D text")
    correct_answer: Literal["A", "B", "C", "D"] = Field(..., description="Correct answer")
    is_active: bool = Field(..., description="Is question active")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")
