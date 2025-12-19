"""Quiz handlers - all data via API, no local storage."""

import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.states import InternForm
from src.api_client import api_client
from src.keyboards import QUIZ_ANSWER_KEYBOARD

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "start_quiz")
async def start_quiz_auto(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Start quiz automatically using priority1 from form."""
    data = await state.get_data()
    candidate_id = data.get("candidate_id")
    priority1 = data.get("priority1")
    
    # Если candidate_id не сохранён, получаем по telegram_id
    if not candidate_id:
        telegram_id = callback.from_user.id
        candidate = await api_client.get_candidate_by_telegram_id(telegram_id)
        
        if not candidate:
            await callback.message.edit_text(
                "❌ Не найден профиль кандидата.\n"
                "Сначала заполни анкету через /start"
            )
            await callback.answer()
            return
        
        candidate_id = candidate.get("id")
        priority1 = candidate.get("priority1")
        await state.update_data(candidate_id=candidate_id, priority1=priority1)
    
    # Получаем треки с API
    tracks = await api_client.get_tracks(active_only=True)
    
    if not tracks:
        await callback.message.edit_text(
            "❌ Не удалось загрузить список направлений.\n"
            "Попробуй позже."
        )
        await callback.answer()
        return
    
    # Ищем track_id по priority1
    track_id = None
    track_name = priority1
    for track in tracks:
        if track.get("name") == priority1:
            track_id = track.get("id")
            break
    
    # Если не нашли priority1 - показываем выбор
    if not track_id:
        buttons = []
        for track in tracks:
            tid = track.get("id")
            tname = track.get("name", "Unknown")
            buttons.append([
                InlineKeyboardButton(
                    text=tname,
                    callback_data=f"track_{tid}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback.message.edit_text(
            "📚 Выбери направление для квиза:\n\n"
            "⏱ Квиз длится 15 минут\n"
            "❗ Попытка только одна",
            reply_markup=keyboard,
        )
        await state.set_state(InternForm.selecting_track)
        await callback.answer()
        return
    
    # Автоматически запускаем квиз по priority1
    from src import texts
    await callback.message.edit_text(
        texts.QUIZ_START.format(track=track_name)
    )
    
    # Запускаем квиз
    response = await api_client.start_quiz(str(candidate_id), track_id)
    
    if not response:
        await callback.message.edit_text("❌ Не удалось начать квиз. Попробуй позже.")
        await callback.answer()
        return
    
    if "detail" in response:
        await callback.message.edit_text(f"❌ {response.get('detail', 'Квиз недоступен')}")
        await callback.answer()
        return
    
    session_id = response.get("session_id")
    question = response.get("question")
    
    if not session_id or not question:
        await callback.message.edit_text("❌ Ошибка: неверный ответ от сервера.")
        await callback.answer()
        return
    
    await state.update_data(
        quiz_session_id=str(session_id),
        current_question_id=str(question.get("id")),
        quiz_track_id=track_id,
    )
    
    text = format_question(question)
    await callback.message.edit_text(text, reply_markup=QUIZ_ANSWER_KEYBOARD)
    await state.set_state(InternForm.in_quiz)
    await callback.answer()


@router.callback_query(F.data.startswith("track_"), InternForm.selecting_track)
async def start_quiz_with_track(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Start quiz with selected track ID."""
    # Извлекаем track_id из callback_data
    track_id_str = callback.data.removeprefix("track_")
    try:
        track_id = int(track_id_str)
    except ValueError:
        await callback.answer("❌ Неверный ID трека")
        return
    
    data = await state.get_data()
    candidate_id = data.get("candidate_id")
    
    if not candidate_id:
        await callback.answer("❌ Ошибка: нет candidate_id")
        return
    
    # Запускаем квиз через API
    response = await api_client.start_quiz(str(candidate_id), track_id)
    
    if not response:
        await callback.message.edit_text(
            "❌ Не удалось начать квиз.\n"
            "Возможно, сервер недоступен."
        )
        await callback.answer()
        return
    
    # Проверяем на ошибку в response
    if "detail" in response:
        await callback.message.edit_text(
            f"❌ {response.get('detail', 'Квиз недоступен')}"
        )
        await callback.answer()
        return
    
    # Получаем session_id и первый вопрос
    session_id = response.get("session_id")
    question = response.get("question")
    
    if not session_id or not question:
        await callback.message.edit_text(
            "❌ Ошибка: неверный ответ от сервера."
        )
        await callback.answer()
        return
    
    # Сохраняем в FSM только ID (всё из API)
    await state.update_data(
        quiz_session_id=str(session_id),
        current_question_id=str(question.get("id")),
        quiz_track_id=track_id,
    )
    
    # Показываем первый вопрос
    text = format_question(question)
    
    await callback.message.edit_text(text, reply_markup=QUIZ_ANSWER_KEYBOARD)
    await state.set_state(InternForm.in_quiz)
    await callback.answer()


def format_question(question: dict) -> str:
    """Format question for display.
    
    API returns:
    {
        "id": "uuid",
        "text": "Question text",
        "block_name": "Block Name",
        "options": [
            {"key": "A", "text": "Option A"},
            {"key": "B", "text": "Option B"},
            {"key": "C", "text": "Option C"},
            {"key": "D", "text": "Option D"}
        ],
        "question_number": 1
    }
    """
    text = question.get("text", "Вопрос")
    block = question.get("block_name", "")
    number = question.get("question_number", "?")
    
    options = question.get("options", [])
    options_text = "\n".join(
        f"**{opt.get('key', '?')}.** {opt.get('text', '')}"
        for opt in options
    )
    
    header = f"📝 **Вопрос {number}**"
    if block:
        header += f" ({block})"
    
    return f"{header}\n\n{text}\n\n{options_text}"


@router.callback_query(F.data.startswith("quiz_ans_"), InternForm.in_quiz)
async def process_answer(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Process quiz answer."""
    # Извлекаем ответ (A, B, C, D)
    answer = callback.data.split("_")[-1]  # "quiz_ans_A" -> "A"
    
    data = await state.get_data()
    session_id = data.get("quiz_session_id")
    question_id = data.get("current_question_id")
    
    if not session_id or not question_id:
        await callback.answer("❌ Ошибка сессии. Начни квиз заново.")
        return
    
    # Отправляем ответ в API
    response = await api_client.submit_answer(
        session_id,
        question_id,
        answer,
    )
    
    if not response:
        await callback.answer("❌ Ошибка связи с сервером")
        return
    
    # API возвращает {"type": "continue", "question": {...}} или {"type": "end", "message": "..."}
    response_type = response.get("type")
    
    if response_type == "end":
        # Квиз завершён
        await handle_quiz_end(callback, state, response)
        return
    
    if response_type == "continue":
        # Показываем следующий вопрос
        next_question = response.get("question")
        
        if not next_question:
            await callback.answer("❌ Ошибка: нет следующего вопроса")
            return
        
        # Обновляем только question_id в FSM
        await state.update_data(
            current_question_id=str(next_question.get("id")),
        )
        
        # Форматируем и показываем
        text = format_question(next_question)
        
        await callback.message.edit_text(
            text,
            reply_markup=QUIZ_ANSWER_KEYBOARD,
        )
    else:
        # Неизвестный тип ответа
        logger.error(f"Unknown quiz response type: {response_type}")
        await callback.answer("❌ Неизвестный ответ от сервера")
    
    await callback.answer()


async def handle_quiz_end(
    callback: types.CallbackQuery,
    state: FSMContext,
    response: dict,
) -> None:
    """Handle quiz completion."""
    from src import texts
    
    # Получаем данные
    data = await state.get_data()
    candidate_id = data.get("candidate_id")
    track_id = data.get("quiz_track_id")
    name = data.get("name", "друг")
    
    # Значения по умолчанию
    total = 0
    correct = 0
    accuracy = 0
    
    if candidate_id:
        attempts = await api_client.get_quiz_attempts(str(candidate_id), track_id)
        if attempts and attempts.get("attempts"):
            last_attempt = attempts["attempts"][0]
            total = last_attempt.get("total_questions", 0)
            correct = last_attempt.get("correct_answers", 0)
            accuracy = int((correct / total * 100)) if total > 0 else 0
    
    text = texts.QUIZ_COMPLETED.format(
        name=name,
        correct=correct,
        total=total,
        accuracy=accuracy,
    )
    
    await callback.message.edit_text(text)
    await state.clear()
    await callback.answer()
