"""Start command handler."""

import logging

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.keyboards import make_keyboard, REMOVE_KEYBOARD
from src.states import InternForm
from src.message_utils import reply_clean
from src.api_client import api_client
from src import texts

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """Handle /start command."""
    await state.clear()
    
    # Delete /start command
    try:
        await message.delete()
    except Exception:
        pass
    
    telegram_id = message.from_user.id
    
    # Check if candidate already exists
    candidate = await api_client.get_candidate_by_telegram_id(telegram_id)
    
    if candidate:
        # Existing candidate - show status
        await show_status(message, state, candidate)
        return
    
    # New candidate - show welcome
    kb = make_keyboard(
        ["📝 Заполнить вручную", "📄 Загрузить резюме (PDF)"],
        row_width=1,
    )
    
    sent = await message.answer(texts.WELCOME_NEW, reply_markup=kb)
    await state.update_data(last_bot_message_id=sent.message_id)
    await state.set_state(InternForm.waiting_for_choice)


async def show_status(message: types.Message, state: FSMContext, candidate: dict) -> None:
    """Show status for existing candidate."""
    name = candidate.get("name", "друг")
    track = candidate.get("priority1", "Не выбрано")
    candidate_id = candidate.get("id")
    
    # Check quiz status
    quiz_status = texts.QUIZ_NOT_PASSED
    next_steps = texts.NEXT_STEPS_QUIZ
    show_quiz_button = True
    
    if candidate_id:
        attempts = await api_client.get_quiz_attempts(str(candidate_id))
        if attempts and attempts.get("attempts"):
            last_attempt = attempts["attempts"][0]
            status = last_attempt.get("status")
            
            if status == "completed":
                total = last_attempt.get("total_questions", 0)
                correct = last_attempt.get("correct_answers", 0)
                accuracy = int((correct / total * 100)) if total > 0 else 0
                quiz_status = texts.QUIZ_PASSED.format(score=accuracy)
                next_steps = texts.NEXT_STEPS_WAIT
                show_quiz_button = False
            elif status == "in_progress":
                quiz_status = texts.QUIZ_IN_PROGRESS
                next_steps = texts.NEXT_STEPS_QUIZ
    
    text = texts.WELCOME_BACK.format(
        name=name,
        quiz_status=quiz_status,
        track=track,
        next_steps=next_steps,
    )
    
    # Keyboard
    if show_quiz_button:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Пройти квиз", callback_data="start_quiz")],
        ])
    else:
        keyboard = None
    
    await state.update_data(
        candidate_id=candidate_id,
        priority1=track,
    )
    
    sent = await message.answer(text, reply_markup=keyboard)
    await state.update_data(last_bot_message_id=sent.message_id)


@router.message(InternForm.waiting_for_choice)
async def process_choice(message: types.Message, state: FSMContext) -> None:
    """Handle initial choice (manual or PDF)."""
    text = message.text
    
    if text == "📝 Заполнить вручную":
        await reply_clean(
            message, state,
            texts.FORM_START,
            reply_markup=REMOVE_KEYBOARD,
        )
        await state.set_state(InternForm.surname)
        
    elif text == "📄 Загрузить резюме (PDF)":
        await reply_clean(
            message, state,
            texts.FORM_RESUME_UPLOAD,
            reply_markup=REMOVE_KEYBOARD,
        )
        await state.set_state(InternForm.upload_resume)
        
    else:
        await reply_clean(message, state, "Пожалуйста, выбери один из вариантов кнопками 👇")

