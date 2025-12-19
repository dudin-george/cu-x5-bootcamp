"""Bot instance and dispatcher setup."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config

logger = logging.getLogger(__name__)

# Bot instance with default parse mode
bot = Bot(
    token=config.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)

# Dispatcher with memory storage (stateless for k8s, state in FSM per user)
dp = Dispatcher(storage=MemoryStorage())


def setup_handlers() -> None:
    """Register all handlers."""
    from src.handlers import start, form, resume, quiz, edit
    from src.handlers.summary import router as summary_router
    
    # Include routers (order matters for handler priority)
    dp.include_router(start.router)
    dp.include_router(resume.router)
    dp.include_router(form.router)
    dp.include_router(summary_router)
    dp.include_router(quiz.router)
    dp.include_router(edit.router)
    
    logger.info("Handlers registered")

