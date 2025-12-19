"""HM Bot - FastAPI webhook server for Kubernetes."""

import logging
from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from src.config import config
from src.bot import bot, dp, setup_handlers

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Starting HM Bot [{config.environment}]")
    setup_handlers()

    # Set webhook if configured
    if config.webhook_base_url and config.bot_token and config.webhook_secret:
        webhook_url = config.webhook_url
        logger.info(f"Setting webhook: {webhook_url}")
        try:
            await bot.set_webhook(
                url=webhook_url,
                secret_token=config.webhook_secret,
                allowed_updates=["message", "callback_query"],
            )
            logger.info("Webhook set successfully")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    else:
        logger.warning("Webhook not configured (missing WEBHOOK_BASE_URL or credentials)")

    yield

    # Shutdown
    logger.info("Shutting down HM Bot")
    await bot.session.close()


app = FastAPI(
    title="X5 HM Bot",
    description="Telegram bot for Hiring Managers",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/healthz")
async def healthz() -> dict:
    """Health check endpoint for Kubernetes."""
    return {"ok": True}


@app.get("/readyz")
async def readyz() -> dict:
    """Readiness check endpoint for Kubernetes."""
    return {"ok": True}


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": "hm-bot",
        "environment": config.environment,
        "status": "running",
    }


@app.post(f"{config.webhook_path}/{{secret}}")
async def telegram_webhook(secret: str, request: Request) -> JSONResponse:
    """Telegram webhook endpoint.

    URL format: /tg/hm/{secret}
    The secret must match WEBHOOK_SECRET environment variable.
    """
    # Verify secret
    if secret != config.webhook_secret:
        logger.warning("Invalid webhook secret received")
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    # Parse update
    try:
        body = await request.json()
        update = Update.model_validate(body, context={"bot": bot})

        logger.debug(f"Received update: {update.update_id}")

        # Process update
        await dp.feed_update(bot, update)

    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        # Return 200 anyway to prevent Telegram from retrying
        return JSONResponse({"ok": False, "error": str(e)})

    return JSONResponse({"ok": True})


# For local development with polling
if __name__ == "__main__":
    import asyncio

    async def main():
        """Run bot in polling mode for local development."""
        logger.info("Running in polling mode (dev)")
        setup_handlers()
        await dp.start_polling(bot)

    asyncio.run(main())
