"""Resume PDF upload handler."""

import logging
import os
import tempfile

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.states import InternForm
from src.parser import ResumeParser
from src.data_loader import UNIVERSITIES
from src.handlers.summary import show_summary
from src.keyboards import REMOVE_KEYBOARD

logger = logging.getLogger(__name__)
router = Router()


@router.message(InternForm.upload_resume, F.document)
async def process_resume_upload(message: types.Message, state: FSMContext) -> None:
    """Handle PDF resume upload."""
    document = message.document
    
    # Validate file type
    is_pdf = (
        document.mime_type == "application/pdf"
        or document.file_name.lower().endswith(".pdf")
    )
    if not is_pdf:
        await message.answer("Пожалуйста, загрузи файл в формате PDF.")
        return
    
    # Validate file size (5 MB)
    if document.file_size > 5 * 1024 * 1024:
        await message.answer("Файл слишком большой. Максимум — 5 МБ.")
        return
    
    await message.answer("📄 Файл получен. Обрабатываю...")
    
    # Download to temp file
    try:
        from src.bot import bot
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            await bot.download(document, destination=tmp.name)
            tmp_path = tmp.name
        
        # Parse resume
        parser = ResumeParser(tmp_path)
        
        # Validate content
        if not parser.validate_content():
            os.unlink(tmp_path)
            await message.answer(
                "❌ Файл не похож на резюме.\n"
                "Проверь файл или заполни анкету вручную."
            )
            await message.answer(
                "Введи свою **Фамилию**:",
                reply_markup=REMOVE_KEYBOARD,
            )
            await state.set_state(InternForm.surname)
            return
        
        # Extract data
        extracted = parser.parse_all(universities_list=UNIVERSITIES)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Update state with extracted data
        await state.update_data(
            surname=extracted.get("surname") or "Не найдено",
            name=extracted.get("name") or "Не найдено",
            phone=extracted.get("phone") or "Не найдено",
            email=extracted.get("email") or "Не найдено",
            resume_link=extracted.get("resume_link") or "Загружено PDF",
            priority1=extracted.get("priority") or "Не выбрано",
            priority2="Не выбрано",
            course=extracted.get("course") or "Не найдено",
            university=extracted.get("university") or "Не найдено",
            specialty=extracted.get("specialty") or "Не найдено",
            employment_hours="Не выбрано",
            city=extracted.get("city") or "Не найдено",
            source="Загрузка PDF",
            birth_year=extracted.get("birth_year") or "Не найдено",
            citizenship=extracted.get("citizenship") or "Не найдено",
            tech_stack=extracted.get("tech_stack") or "Не найдено",
        )
        
        await message.answer("✅ Данные извлечены! Проверь и заполни пропуски.")
        await show_summary(message, state)
        
    except Exception as e:
        logger.exception(f"Error parsing resume: {e}")
        await message.answer(
            "❌ Ошибка при чтении файла. Заполним вручную."
        )
        await message.answer(
            "Введи свою **Фамилию**:",
            reply_markup=REMOVE_KEYBOARD,
        )
        await state.set_state(InternForm.surname)


@router.message(InternForm.upload_resume)
async def handle_non_document(message: types.Message, state: FSMContext) -> None:
    """Handle non-document messages in upload state."""
    await message.answer(
        "Пожалуйста, отправь файл PDF.\n"
        "Или напиши /start чтобы заполнить вручную."
    )

