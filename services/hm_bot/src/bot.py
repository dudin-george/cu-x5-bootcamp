"""Bot instance and dispatcher setup."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config

logger = logging.getLogger(__name__)

# Bot instance with HTML parse mode (more reliable than Markdown)
bot = Bot(
    token=config.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# Dispatcher with memory storage
dp = Dispatcher(storage=MemoryStorage())


def setup_handlers() -> None:
    """Register all handlers."""
    from src.handlers import start, menu, vacancy, tinder

    # Include routers (order matters)
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(vacancy.router)
    dp.include_router(tinder.router)

    logger.info("Handlers registered")

