"""Edit field callback handlers."""

import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.states import InternForm
from src.keyboards import make_keyboard, REMOVE_KEYBOARD
from src.data_loader import PRIORITIES, COURSES, UNIVERSITIES

logger = logging.getLogger(__name__)
router = Router()


# Field configuration: state, prompt, keyboard
FIELD_CONFIG = {
    "surname": (InternForm.surname, "Введи новую фамилию:", None),
    "name": (InternForm.name, "Введи новое имя:", None),
    "phone": (
        InternForm.phone,
        "Отправь номер телефона (кнопка):",
        lambda: make_keyboard([], request_contact=True),
    ),
    "email": (InternForm.email, "Введи новый email:", None),
    "resume_link": (InternForm.resume_link, "Введи ссылку на резюме:", None),
    "priority1": (
        InternForm.priority1,
        "Выбери первый приоритет:",
        lambda: make_keyboard(PRIORITIES),
    ),
    "priority2": (
        InternForm.priority2,
        "Выбери второй приоритет:",
        lambda: make_keyboard(PRIORITIES),
    ),
    "course": (
        InternForm.course,
        "Укажи ступень обучения:",
        lambda: make_keyboard(COURSES, add_other=True),
    ),
    "university": (
        InternForm.university,
        "Выбери ВУЗ:",
        lambda: make_keyboard(UNIVERSITIES, add_other=True),
    ),
    "specialty": (InternForm.specialty, "Укажи специальность:", None),
    "employment_hours": (
        InternForm.employment_hours,
        "Выбери занятость:",
        lambda: make_keyboard(["20", "30", "40"], row_width=3),
    ),
    "city": (
        InternForm.city,
        "Укажи город:",
        lambda: make_keyboard(["Москва", "Санкт-Петербург", "Казань"], add_other=True),
    ),
    "birth_year": (InternForm.birth_year, "Укажи год рождения:", None),
    "citizenship": (
        InternForm.citizenship,
        "Укажи гражданство:",
        lambda: make_keyboard(["РФ"], add_other=True),
    ),
    "tech_stack": (InternForm.tech_stack, "Введи стек технологий:", None),
}


@router.callback_query(F.data.startswith("edit_"), InternForm.confirm)
async def edit_field(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle edit button click."""
    field = callback.data.removeprefix("edit_")
    
    if field not in FIELD_CONFIG:
        await callback.answer("Неизвестное поле")
        return
    
    target_state, prompt, keyboard_fn = FIELD_CONFIG[field]
    
    # Mark as editing mode
    await state.update_data(is_editing=True)
    await state.set_state(target_state)
    
    # Get keyboard if defined
    keyboard = keyboard_fn() if keyboard_fn else REMOVE_KEYBOARD
    
    await callback.message.answer(prompt, reply_markup=keyboard)
    await callback.answer()

