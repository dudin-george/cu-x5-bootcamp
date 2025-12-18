"""Candidate Telegram Bot service for X5 Hiring Bootcamp."""

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Configuration from environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
PORT = int(os.getenv("PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="X5 Hiring Candidate Bot",
    description="Telegram bot for candidates",
    version="1.0.0",
)


class HealthResponse(BaseModel):
    ok: bool


class WebhookResponse(BaseModel):
    ok: bool
    message: str | None = None


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
async def healthz() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(ok=True)


@app.post("/tg/candidate/{secret}", response_model=WebhookResponse, tags=["webhook"])
async def telegram_webhook(secret: str, request: Request) -> WebhookResponse:
    """
    Telegram webhook endpoint for candidate bot.
    
    The secret in the URL must match WEBHOOK_SECRET environment variable.
    """
    # Verify webhook secret
    if secret != WEBHOOK_SECRET:
        logger.warning(f"Invalid webhook secret received")
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    
    # Parse webhook data
    try:
        body: dict[str, Any] = await request.json()
        logger.info(f"Received webhook: {body.get('update_id', 'unknown')}")
        
        # TODO: Process Telegram update here
        # For now, just acknowledge receipt
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    return WebhookResponse(ok=True, message="Webhook received")


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": "candidate-bot",
        "environment": ENVIRONMENT,
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)

