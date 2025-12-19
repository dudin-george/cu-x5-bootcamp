"""Message utilities for clean chat experience."""

import logging
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)


async def track_message(state: FSMContext, message_id: int) -> None:
    """Track message ID for later deletion."""
    data = await state.get_data()
    message_ids = data.get("tracked_message_ids", [])
    message_ids.append(message_id)
    await state.update_data(tracked_message_ids=message_ids)


async def track_bot_message(message: types.Message, state: FSMContext) -> None:
    """Track bot's sent message."""
    await track_message(state, message.message_id)


async def track_user_message(message: types.Message, state: FSMContext) -> None:
    """Track user's message."""
    await track_message(state, message.message_id)


async def clear_chat_history(bot: Bot, chat_id: int, state: FSMContext) -> None:
    """Delete all tracked messages from chat."""
    data = await state.get_data()
    message_ids = data.get("tracked_message_ids", [])
    
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            logger.debug(f"Cannot delete message {msg_id}: {e}")
    
    # Clear tracked IDs
    await state.update_data(tracked_message_ids=[])

