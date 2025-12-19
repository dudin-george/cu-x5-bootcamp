"""Message utilities for clean chat experience."""

import logging
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

logger = logging.getLogger(__name__)


async def reply_clean(
    message: types.Message,
    state: FSMContext,
    text: str,
    reply_markup: ReplyKeyboardMarkup | ReplyKeyboardRemove | None = None,
) -> types.Message:
    """Send reply, deleting user message and previous bot message.
    
    1. Delete user's message (their input)
    2. Delete previous bot message (stored in state)
    3. Send new message
    4. Save new message id in state
    """
    bot: Bot = message.bot
    chat_id = message.chat.id
    
    # 1. Delete user's message
    try:
        await message.delete()
    except Exception as e:
        logger.debug(f"Cannot delete user message: {e}")
    
    # 2. Delete previous bot message
    data = await state.get_data()
    prev_msg_id = data.get("last_bot_message_id")
    if prev_msg_id:
        try:
            await bot.delete_message(chat_id, prev_msg_id)
        except Exception as e:
            logger.debug(f"Cannot delete previous bot message: {e}")
    
    # 3. Send new message
    sent = await message.answer(text, reply_markup=reply_markup)
    
    # 4. Save message id
    await state.update_data(last_bot_message_id=sent.message_id)
    
    return sent

