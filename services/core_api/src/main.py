"""Core API service for X5 Hiring Bootcamp."""

import os
from fastapi import FastAPI
from pydantic import BaseModel

# Configuration from environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
PORT = int(os.getenv("PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

app = FastAPI(
    title="X5 Hiring Core API",
    description="Core API service for X5 Hiring Bootcamp",
    version="1.0.0",
    root_path="/api",
)


class HealthResponse(BaseModel):
    ok: bool


class VersionResponse(BaseModel):
    version: str
    environment: str


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
async def healthz() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(ok=True)


@app.get("/version", response_model=VersionResponse, tags=["info"])
async def version() -> VersionResponse:
    """Version endpoint."""
    return VersionResponse(version="1.0.0", environment=ENVIRONMENT)


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": "core-api",
        "environment": ENVIRONMENT,
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)

