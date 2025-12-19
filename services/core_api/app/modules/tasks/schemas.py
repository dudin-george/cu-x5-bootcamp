"""Task schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.enums import TaskStatus


# =============================================================================
# TaskType schemas
# =============================================================================

class TaskTypeCreate(BaseModel):
    """Schema for creating task type."""

    code: str = Field(..., min_length=1, max_length=100, description="Код типа задачи")
    name: str = Field(..., min_length=1, max_length=200, description="Название типа задачи")
    description: str | None = Field(None, description="Описание типа задачи")
    is_active: bool = Field(True, description="Активен ли тип задачи")


class TaskTypeResponse(BaseModel):
    """Schema for task type response."""

    id: int = Field(..., description="ID типа задачи")
    code: str = Field(..., description="Код типа задачи")
    name: str = Field(..., description="Название типа задачи")
    description: str | None = Field(None, description="Описание типа задачи")
    is_active: bool = Field(..., description="Активен ли тип задачи")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")

    class Config:
        from_attributes = True


# =============================================================================
# RecruiterTask schemas
# =============================================================================

class RecruiterTaskCreate(BaseModel):
    """Schema for creating recruiter task."""

    task_type_id: int = Field(..., description="ID типа задачи")
    title: str = Field(..., min_length=1, max_length=500, description="Заголовок задачи")
    description: str | None = Field(None, description="Описание задачи")
    context: dict = Field(default_factory=dict, description="Контекст задачи (JSON)")


class RecruiterTaskResponse(BaseModel):
    """Schema for recruiter task response (simplified for kanban cards)."""

    id: uuid.UUID = Field(..., description="UUID задачи")
    task_type_name: str = Field(..., description="Название типа задачи")
    status: TaskStatus = Field(..., description="Статус задачи")
    title: str = Field(..., description="Заголовок задачи")
    description: str | None = Field(None, description="Описание задачи")
    context: dict = Field(..., description="Контекст задачи")

    class Config:
        from_attributes = True


class TasksListResponse(BaseModel):
    """Schema for list of tasks."""

    tasks: list[RecruiterTaskResponse] = Field(..., description="Список задач")


# =============================================================================
# Task action schemas
# =============================================================================

class AssignTaskRequest(BaseModel):
    """Schema for assigning task to recruiter (backlog -> in_progress)."""

    recruiter_id: uuid.UUID = Field(..., description="Ory Identity ID рекрутера")


class CompleteTaskRequest(BaseModel):
    """Schema for completing task (optional fields for future use)."""

    pass  # Можно добавить поля в будущем, пока пустой


class RejectTaskRequest(BaseModel):
    """Schema for rejecting task (optional fields for future use)."""

    pass  # Можно добавить поля в будущем, пока пустой


class UpdateTaskStatusRequest(BaseModel):
    """Schema for updating task status (PATCH endpoint)."""

    status: TaskStatus = Field(..., description="Новый статус задачи")
