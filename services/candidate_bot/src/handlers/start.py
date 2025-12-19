"""Start command handler."""

import logging

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.keyboards import make_keyboard, REMOVE_KEYBOARD
from src.states import InternForm

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """Handle /start command."""
    await state.clear()
    
    greeting = (
        "👋 Привет! Я бот для подачи заявки на стажировку в X5 Tech.\n\n"
        "Как ты хочешь заполнить анкету?"
    )
    
    kb = make_keyboard(
        ["📝 Заполнить вручную", "📄 Загрузить резюме (PDF)"],
        row_width=1,
    )
    
    await message.answer(greeting, reply_markup=kb)
    await state.set_state(InternForm.waiting_for_choice)


@router.message(InternForm.waiting_for_choice)
async def process_choice(message: types.Message, state: FSMContext) -> None:
    """Handle initial choice (manual or PDF)."""
    text = message.text
    
    if text == "📝 Заполнить вручную":
        await message.answer(
            "Отлично! Давай начнём.\nВведи свою **Фамилию**:",
            reply_markup=REMOVE_KEYBOARD,
        )
        await state.set_state(InternForm.surname)
        
    elif text == "📄 Загрузить резюме (PDF)":
        await message.answer(
            "Пожалуйста, отправь мне файл резюме в формате **PDF** (до 5 МБ).",
            reply_markup=REMOVE_KEYBOARD,
        )
        await state.set_state(InternForm.upload_resume)
        
    else:
        await message.answer("Пожалуйста, выбери один из вариантов кнопками.")

