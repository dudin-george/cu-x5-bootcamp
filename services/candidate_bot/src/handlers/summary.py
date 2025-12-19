"""Summary display and form submission."""

import logging

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.states import InternForm
from src.api_client import api_client
from src.message_utils import track_bot_message, clear_chat_history

logger = logging.getLogger(__name__)
router = Router()


async def show_summary(message: types.Message, state: FSMContext) -> None:
    """Show form summary with edit buttons."""
    data = await state.get_data()
    
    summary = (
        "📋 **Проверь свои данные:**\n\n"
        f"👤 Фамилия: {data.get('surname', '—')}\n"
        f"👤 Имя: {data.get('name', '—')}\n"
        f"📱 Телефон: {data.get('phone', '—')}\n"
        f"📧 Email: {data.get('email', '—')}\n"
        f"📄 Резюме: {data.get('resume_link', '—')}\n"
        f"🎯 Приоритет 1: {data.get('priority1', '—')}\n"
        f"🎯 Приоритет 2: {data.get('priority2', '—')}\n"
        f"🎓 Курс: {data.get('course', '—')}\n"
        f"🏛 ВУЗ: {data.get('university', '—')}\n"
        f"📚 Специальность: {data.get('specialty', '—')}\n"
        f"⏰ Занятость: {data.get('employment_hours', '—')} ч/нед\n"
        f"🏙 Город: {data.get('city', '—')}\n"
        f"📣 Источник: {data.get('source', '—')}\n"
        f"📅 Год рождения: {data.get('birth_year', '—')}\n"
        f"🌍 Гражданство: {data.get('citizenship', '—')}\n"
        f"💻 Стек: {data.get('tech_stack', '—')}\n"
    )
    
    # Edit buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Фамилия", callback_data="edit_surname"),
            InlineKeyboardButton(text="Имя", callback_data="edit_name"),
        ],
        [
            InlineKeyboardButton(text="Телефон", callback_data="edit_phone"),
            InlineKeyboardButton(text="Email", callback_data="edit_email"),
        ],
        [
            InlineKeyboardButton(text="Резюме", callback_data="edit_resume_link"),
        ],
        [
            InlineKeyboardButton(text="Приоритет 1", callback_data="edit_priority1"),
            InlineKeyboardButton(text="Приоритет 2", callback_data="edit_priority2"),
        ],
        [
            InlineKeyboardButton(text="Курс", callback_data="edit_course"),
            InlineKeyboardButton(text="ВУЗ", callback_data="edit_university"),
        ],
        [
            InlineKeyboardButton(text="Специальность", callback_data="edit_specialty"),
            InlineKeyboardButton(text="Занятость", callback_data="edit_employment_hours"),
        ],
        [
            InlineKeyboardButton(text="Город", callback_data="edit_city"),
            InlineKeyboardButton(text="Год рожд.", callback_data="edit_birth_year"),
        ],
        [
            InlineKeyboardButton(text="Гражданство", callback_data="edit_citizenship"),
            InlineKeyboardButton(text="Стек", callback_data="edit_tech_stack"),
        ],
        [
            InlineKeyboardButton(text="✅ Отправить анкету", callback_data="submit_form"),
        ],
    ])
    
    sent = await message.answer(summary, reply_markup=keyboard)
    await track_bot_message(sent, state)
    await state.set_state(InternForm.confirm)


@router.callback_query(F.data == "submit_form", InternForm.confirm)
async def submit_form(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Submit form to API and clear chat history."""
    bot: Bot = callback.bot
    chat_id = callback.message.chat.id
    data = await state.get_data()
    user = callback.from_user
    
    # Prepare API payload
    payload = {
        "telegram_id": user.id,
        "username": user.username,
        "surname": data.get("surname"),
        "name": data.get("name"),
        "phone": data.get("phone"),
        "email": data.get("email"),
        "resume_link": data.get("resume_link"),
        "priority1": data.get("priority1"),
        "priority2": data.get("priority2"),
        "course": data.get("course"),
        "university": data.get("university"),
        "specialty": data.get("specialty"),
        "employment_hours": data.get("employment_hours"),
        "city": data.get("city"),
        "source": data.get("source"),
        "birth_year": data.get("birth_year"),
        "citizenship": data.get("citizenship"),
        "tech_stack": data.get("tech_stack"),
    }
    
    # Send to API
    response = await api_client.create_candidate(payload)
    
    if response:
        # Save candidate_id for quiz
        candidate_id = response.get("id")
        name = data.get("name", "друг")
        track = data.get("priority1", "твоему направлению")
        
        # Clear all chat history first
        await clear_chat_history(bot, chat_id, state)
        
        # Delete the summary message too
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        # Update state with candidate_id but keep name/track
        await state.update_data(
            candidate_id=candidate_id,
            name=name,
            priority1=track,
            tracked_message_ids=[],  # Reset tracking
        )
        
        # Success message with quiz button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Начать квиз", callback_data="start_quiz")],
        ])
        
        from src import texts
        text = texts.FORM_SUBMITTED.format(name=name, track=track)
        
        await bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        from src import texts
        await callback.message.edit_text(texts.ERROR_API)
        await state.clear()
    
    await callback.answer()
