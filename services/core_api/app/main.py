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


# Register module routers
from app.modules.auth.router import router as auth_router
from app.modules.candidates.quiz_router import router as quiz_router
from app.modules.candidates.router import router as candidates_router
from app.modules.hiring_managers.router import router as hiring_managers_router
from app.modules.vacancies.candidate_selection_router import router as candidate_selection_router
from app.modules.vacancies.interview_management_router import router as interview_management_router
from app.modules.vacancies.pools_router import router as pools_router
from app.modules.vacancies.tracks_router import router as tracks_router
from app.modules.vacancies.vacancy_management_router import router as vacancy_management_router

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(candidates_router, prefix="/api/candidates", tags=["candidates"])
app.include_router(quiz_router, prefix="/api/quiz", tags=["quiz"])
app.include_router(hiring_managers_router, prefix="/api/hiring-managers", tags=["hiring-managers"])
app.include_router(tracks_router, prefix="/api/tracks", tags=["tracks"])
app.include_router(vacancy_management_router, prefix="/api/vacancies", tags=["vacancy-management"])
app.include_router(candidate_selection_router, prefix="/api/vacancies", tags=["candidate-selection"])
app.include_router(interview_management_router, prefix="/api/vacancies", tags=["interview-management"])
app.include_router(pools_router, prefix="/api/candidate-pools", tags=["candidate-pools"])
