"""Main FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import BaseAppException

app = FastAPI(
    title="X5 Recruitment System API",
    description="API для системы рекрутинга X5 Group",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Handle application exceptions.

    Args:
        request: HTTP request.
        exc: Application exception.

    Returns:
        JSONResponse: Error response.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        dict: Welcome message.
    """
    return {"message": "X5 Recruitment System API"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Health status.
    """
    return {"status": "healthy"}


@app.post("/dev/clear-database")
async def clear_database() -> dict[str, str]:
    """Clear all tables in database (except enums).

    WARNING: This endpoint deletes ALL data from ALL tables!
    Use only for development/testing purposes.

    Returns:
        dict: Status message.
    """
    from sqlalchemy import text
    from app.core.database import get_db

    async for db in get_db():
        try:
            # Disable foreign key checks temporarily
            await db.execute(text("SET session_replication_role = 'replica';"))

            # List of tables to truncate (in order to handle dependencies)
            tables = [
                "interview_feedback",
                "candidate_pool",
                "recruiter_tasks",
                "vacancies",
                "recruiters",
                "task_types",
                "candidates",
                "hiring_managers",
                "tracks",
            ]

            for table in tables:
                await db.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))

            # Re-enable foreign key checks
            await db.execute(text("SET session_replication_role = 'origin';"))

            await db.commit()

            return {"status": "success", "message": "All tables cleared"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clear database: {str(e)}"
            )
        finally:
            break  # Only use first db session from generator


# Register module routers
from app.modules.auth.router import router as auth_router
from app.modules.candidates.quiz_router import router as quiz_router
from app.modules.candidates.router import router as candidates_router
from app.modules.hiring_managers.router import router as hiring_managers_router
from app.modules.quiz.admin_router import router as quiz_admin_router
from app.modules.recruiters.router import router as recruiters_router
from app.modules.tasks.admin_router import router as tasks_admin_router
from app.modules.tasks.router import router as tasks_router
from app.modules.vacancies.candidate_selection_router import router as candidate_selection_router
from app.modules.vacancies.interview_management_router import router as interview_management_router
from app.modules.vacancies.pools_router import router as pools_router
from app.modules.vacancies.tracks_router import router as tracks_router
from app.modules.vacancies.vacancy_management_router import router as vacancy_management_router

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(candidates_router, prefix="/api/candidates", tags=["candidates"])
app.include_router(quiz_router, prefix="/api/quiz", tags=["quiz"])
app.include_router(quiz_admin_router, prefix="/api/quiz/admin", tags=["quiz-admin"])
app.include_router(hiring_managers_router, prefix="/api/hiring-managers", tags=["hiring-managers"])
app.include_router(recruiters_router, prefix="/api/recruiters", tags=["recruiters"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(tasks_admin_router, prefix="/api/tasks/admin", tags=["tasks-admin"])
app.include_router(tracks_router, prefix="/api/tracks", tags=["tracks"])
app.include_router(vacancy_management_router, prefix="/api/vacancies", tags=["vacancy-management"])
app.include_router(candidate_selection_router, prefix="/api/vacancies", tags=["candidate-selection"])
app.include_router(interview_management_router, prefix="/api/vacancies", tags=["interview-management"])
app.include_router(pools_router, prefix="/api/candidate-pools", tags=["candidate-pools"])
