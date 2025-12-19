"""Form field handlers."""

import logging

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.keyboards import make_keyboard, REMOVE_KEYBOARD
from src.states import InternForm
from src.data_loader import COURSES, UNIVERSITIES, SOURCES
from src.api_client import api_client
from src.handlers.summary import show_summary

logger = logging.getLogger(__name__)
router = Router()


async def get_track_names() -> list[str]:
    """Get track names from API."""
    tracks = await api_client.get_tracks(active_only=True)
    if tracks:
        return [t.get("name", "") for t in tracks if t.get("name")]
    return []


# === Basic Info ===

@router.message(InternForm.surname)
async def process_surname(message: types.Message, state: FSMContext) -> None:
    """Handle surname input."""
    await state.update_data(surname=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await message.answer("Введи своё **Имя**:")
    await state.set_state(InternForm.name)


@router.message(InternForm.name)
async def process_name(message: types.Message, state: FSMContext) -> None:
    """Handle name input."""
    await state.update_data(name=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    kb = make_keyboard([], request_contact=True)
    await message.answer(
        "Нажми кнопку, чтобы отправить **номер телефона**:",
        reply_markup=kb,
    )
    await state.set_state(InternForm.phone)


@router.message(InternForm.phone)
async def process_phone(message: types.Message, state: FSMContext) -> None:
    """Handle phone input (contact sharing only)."""
    if not message.contact:
        await message.answer(
            "Пожалуйста, используй кнопку **📱 Отправить номер телефона**."
        )
        return
    
    # Verify it's user's own contact
    if message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, отправь СВОЙ номер телефона.")
        return
    
    phone = message.contact.phone_number
    if len(phone) < 7:
        await message.answer("Некорректный номер. Попробуй ещё раз.")
        return
    
    await state.update_data(phone=phone)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await message.answer("Введи свою **почту**:", reply_markup=REMOVE_KEYBOARD)
    await state.set_state(InternForm.email)


@router.message(InternForm.email)
async def process_email(message: types.Message, state: FSMContext) -> None:
    """Handle email input."""
    if "@" not in message.text:
        await message.answer("Пожалуйста, введи корректный email.")
        return
    
    await state.update_data(email=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await message.answer("Вставь **ссылку на резюме** (или напиши 'нет'):")
    await state.set_state(InternForm.resume_link)


@router.message(InternForm.resume_link)
async def process_resume_link(message: types.Message, state: FSMContext) -> None:
    """Handle resume link input."""
    await state.update_data(resume_link=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_priority1(message, state)


async def ask_priority1(message: types.Message, state: FSMContext) -> None:
    """Ask for priority 1 with tracks from API."""
    tracks = await get_track_names()
    if not tracks:
        await message.answer(
            "⚠️ Не удалось загрузить направления. Напиши вручную:",
            reply_markup=REMOVE_KEYBOARD,
        )
    else:
        # Сохраняем в state для валидации
        await state.update_data(available_tracks=tracks)
        kb = make_keyboard(tracks)
        await message.answer("Выбери **первый приоритет** (направление):", reply_markup=kb)
    await state.set_state(InternForm.priority1)


# === Priority ===

@router.message(InternForm.priority1)
async def process_priority1(message: types.Message, state: FSMContext) -> None:
    """Handle priority 1 selection."""
    data = await state.get_data()
    tracks = data.get("available_tracks", [])
    
    # Принимаем любой текст если треки не загрузились
    if tracks and message.text not in tracks:
        kb = make_keyboard(tracks)
        await message.answer("Выбери направление кнопкой.", reply_markup=kb)
        return
    
    await state.update_data(priority1=message.text)
    
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_priority2(message, state)


async def ask_priority2(message: types.Message, state: FSMContext) -> None:
    """Ask for priority 2."""
    data = await state.get_data()
    tracks = data.get("available_tracks")
    
    # Если треки ещё не загружены - загружаем
    if not tracks:
        tracks = await get_track_names()
        if tracks:
            await state.update_data(available_tracks=tracks)
    
    if tracks:
        kb = make_keyboard(tracks)
        await message.answer("Выбери **второй приоритет**:", reply_markup=kb)
    else:
        await message.answer("Укажи **второй приоритет**:", reply_markup=REMOVE_KEYBOARD)
    
    await state.set_state(InternForm.priority2)


@router.message(InternForm.priority2)
async def process_priority2(message: types.Message, state: FSMContext) -> None:
    """Handle priority 2 selection."""
    data = await state.get_data()
    tracks = data.get("available_tracks", [])
    
    # Принимаем любой текст если треки не загрузились
    if tracks and message.text not in tracks:
        kb = make_keyboard(tracks)
        await message.answer("Выбери направление кнопкой.", reply_markup=kb)
        return
    
    await state.update_data(priority2=message.text)
    
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    kb = make_keyboard(COURSES, add_other=True)
    await message.answer("Укажи **ступень обучения**:", reply_markup=kb)
    await state.set_state(InternForm.course)


# === Education ===

@router.message(InternForm.course)
async def process_course(message: types.Message, state: FSMContext) -> None:
    """Handle course selection."""
    if message.text == "Другое":
        await message.answer("Напиши ступень обучения:", reply_markup=REMOVE_KEYBOARD)
        await state.set_state(InternForm.course_custom)
        return
    
    await state.update_data(course=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_university(message, state)


@router.message(InternForm.course_custom)
async def process_course_custom(message: types.Message, state: FSMContext) -> None:
    """Handle custom course input."""
    await state.update_data(course=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_university(message, state)


async def ask_university(message: types.Message, state: FSMContext) -> None:
    """Ask for university."""
    kb = make_keyboard(UNIVERSITIES, add_other=True)
    await message.answer("Выбери **ВУЗ**:", reply_markup=kb)
    await state.set_state(InternForm.university)


@router.message(InternForm.university)
async def process_university(message: types.Message, state: FSMContext) -> None:
    """Handle university selection."""
    if message.text == "Другое":
        await message.answer("Напиши название ВУЗа:", reply_markup=REMOVE_KEYBOARD)
        await state.set_state(InternForm.university_custom)
        return
    
    await state.update_data(university=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_specialty(message, state)


@router.message(InternForm.university_custom)
async def process_university_custom(message: types.Message, state: FSMContext) -> None:
    """Handle custom university input."""
    await state.update_data(university=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_specialty(message, state)


async def ask_specialty(message: types.Message, state: FSMContext) -> None:
    """Ask for specialty."""
    await message.answer(
        "Укажи **специальность (факультет)**:",
        reply_markup=REMOVE_KEYBOARD,
    )
    await state.set_state(InternForm.specialty)


@router.message(InternForm.specialty)
async def process_specialty(message: types.Message, state: FSMContext) -> None:
    """Handle specialty input."""
    await state.update_data(specialty=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    kb = make_keyboard(["20", "30", "40"], row_width=3)
    await message.answer(
        "Какую **занятость** (часов в неделю) рассматриваешь?",
        reply_markup=kb,
    )
    await state.set_state(InternForm.employment_hours)


# === Work Preferences ===

@router.message(InternForm.employment_hours)
async def process_employment(message: types.Message, state: FSMContext) -> None:
    """Handle employment hours selection."""
    valid = ["20", "30", "40"]
    if message.text not in valid:
        kb = make_keyboard(valid, row_width=3)
        await message.answer("Выбери вариант кнопкой.", reply_markup=kb)
        return
    
    await state.update_data(employment_hours=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    kb = make_keyboard(["Москва", "Санкт-Петербург", "Казань"], add_other=True)
    await message.answer("Укажи **город**:", reply_markup=kb)
    await state.set_state(InternForm.city)


@router.message(InternForm.city)
async def process_city(message: types.Message, state: FSMContext) -> None:
    """Handle city selection."""
    if message.text == "Другое":
        await message.answer("Напиши город:", reply_markup=REMOVE_KEYBOARD)
        await state.set_state(InternForm.city_custom)
        return
    
    await state.update_data(city=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_source(message, state)


@router.message(InternForm.city_custom)
async def process_city_custom(message: types.Message, state: FSMContext) -> None:
    """Handle custom city input."""
    await state.update_data(city=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_source(message, state)


async def ask_source(message: types.Message, state: FSMContext) -> None:
    """Ask for source."""
    kb = make_keyboard(SOURCES, row_width=1)
    await message.answer("Откуда узнал о стажировке?", reply_markup=kb)
    await state.set_state(InternForm.source)


@router.message(InternForm.source)
async def process_source(message: types.Message, state: FSMContext) -> None:
    """Handle source selection."""
    if message.text == "Другое":
        await message.answer("Укажи источник:", reply_markup=REMOVE_KEYBOARD)
        await state.set_state(InternForm.source_custom)
        return
    
    await state.update_data(source=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_birth_year(message, state)


@router.message(InternForm.source_custom)
async def process_source_custom(message: types.Message, state: FSMContext) -> None:
    """Handle custom source input."""
    await state.update_data(source=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_birth_year(message, state)


# === Personal Info ===

async def ask_birth_year(message: types.Message, state: FSMContext) -> None:
    """Ask for birth year."""
    await message.answer("Укажи **год рождения**:", reply_markup=REMOVE_KEYBOARD)
    await state.set_state(InternForm.birth_year)


@router.message(InternForm.birth_year)
async def process_birth_year(message: types.Message, state: FSMContext) -> None:
    """Handle birth year input."""
    if not message.text.isdigit() or len(message.text) != 4:
        await message.answer("Введи год (4 цифры).")
        return
    
    await state.update_data(birth_year=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    kb = make_keyboard(["РФ"], add_other=True)
    await message.answer("Укажи **гражданство**:", reply_markup=kb)
    await state.set_state(InternForm.citizenship)


@router.message(InternForm.citizenship)
async def process_citizenship(message: types.Message, state: FSMContext) -> None:
    """Handle citizenship selection."""
    if message.text == "Другое":
        await message.answer("Напиши гражданство:", reply_markup=REMOVE_KEYBOARD)
        await state.set_state(InternForm.citizenship_custom)
        return
    
    await state.update_data(citizenship=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_tech_stack(message, state)


@router.message(InternForm.citizenship_custom)
async def process_citizenship_custom(message: types.Message, state: FSMContext) -> None:
    """Handle custom citizenship input."""
    await state.update_data(citizenship=message.text)
    
    data = await state.get_data()
    if data.get("is_editing"):
        await show_summary(message, state)
        return
    
    await ask_tech_stack(message, state)


async def ask_tech_stack(message: types.Message, state: FSMContext) -> None:
    """Ask for tech stack."""
    await message.answer(
        "Перечисли **языки и технологии**, которые используешь:",
        reply_markup=REMOVE_KEYBOARD,
    )
    await state.set_state(InternForm.tech_stack)


@router.message(InternForm.tech_stack)
async def process_tech_stack(message: types.Message, state: FSMContext) -> None:
    """Handle tech stack input and show summary."""
    await state.update_data(tech_stack=message.text, is_editing=False)
    await show_summary(message, state)

