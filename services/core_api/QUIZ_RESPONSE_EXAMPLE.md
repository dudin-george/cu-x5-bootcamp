# Quiz Response Handling - Примеры

Как обрабатывать discriminated union в квиз-системе.

## Ключевая идея: Type Discriminator

Используем поле `type` для различения типа ответа:
- `type: "continue"` → квиз продолжается, есть следующий вопрос
- `type: "end"` → квиз закончен, показать результаты

## Backend (FastAPI)

### Endpoint с Union типом

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from app.modules.quiz.schemas import (
    QuizAnswerRequest,
    QuizAnswerResponse,  # Это QuizContinueResponse | QuizEndResponse
    QuizContinueResponse,
    QuizEndResponse,
)

router = APIRouter()

@router.post(
    "/answer",
    response_model=QuizAnswerResponse,
    summary="Submit answer and get next question or results",
    description="Submit answer. Returns next question if quiz continues, or results if ended."
)
async def submit_answer(
    request: QuizAnswerRequest,
    db: AsyncSession = Depends(get_db),
) -> QuizContinueResponse | QuizEndResponse:
    """Submit answer and get response."""

    # Получить сессию
    session = await get_session(db, request.session_id)
    if not session:
        raise HTTPException(404, "Quiz session not found")

    # Проверить время
    now = datetime.now(timezone.utc)
    time_expired = now >= session.expires_at

    # Сохранить ответ
    question = await get_question(db, request.question_id)
    is_correct = (request.answer == question.correct_answer)
    await save_answer(db, request.session_id, request.question_id, request.answer, is_correct)

    # Обновить статистику
    await update_session_stats(db, request.session_id, is_correct)

    # Проверить условия завершения
    if time_expired:
        # Время вышло - финализировать и вернуть результаты
        await finalize_session(db, session)
        results = await calculate_results(db, session.id)

        return QuizEndResponse(
            type="end",
            reason="timeout",
            results=results
        )

    # Получить следующий вопрос
    next_question = await get_next_question(db, session)

    if not next_question:
        # Все вопросы закончились
        await finalize_session(db, session)
        results = await calculate_results(db, session.id)

        return QuizEndResponse(
            type="end",
            reason="all_questions_answered",
            results=results
        )

    # Квиз продолжается
    time_remaining = int((session.expires_at - now).total_seconds())
    questions_answered = await count_answered_questions(db, session.id)

    return QuizContinueResponse(
        type="continue",
        time_remaining_seconds=time_remaining,
        questions_answered=questions_answered,
        next_question=format_question(next_question, questions_answered + 1)
    )
```

### OpenAPI Schema

FastAPI автоматически создаст правильную OpenAPI схему:

```yaml
/api/quiz/answer:
  post:
    responses:
      '200':
        content:
          application/json:
            schema:
              oneOf:
                - $ref: '#/components/schemas/QuizContinueResponse'
                - $ref: '#/components/schemas/QuizEndResponse'
              discriminator:
                propertyName: type
                mapping:
                  continue: '#/components/schemas/QuizContinueResponse'
                  end: '#/components/schemas/QuizEndResponse'
```

## Client Side (Telegram Bot - Python)

### Обработка ответа с проверкой типа

```python
from typing import TypedDict, Literal

class QuestionOption(TypedDict):
    key: Literal["A", "B", "C", "D"]
    text: str

class Question(TypedDict):
    id: str
    text: str
    block_name: str
    options: list[QuestionOption]
    question_number: int

class ContinueResponse(TypedDict):
    type: Literal["continue"]
    time_remaining_seconds: int
    questions_answered: int
    next_question: Question

class EndResponse(TypedDict):
    type: Literal["end"]
    reason: Literal["timeout", "all_questions_answered"]
    results: dict

QuizAnswerResponse = ContinueResponse | EndResponse


async def submit_answer(session_id: str, question_id: str, answer: str) -> None:
    """Submit answer and handle response."""

    response = await http_client.post(
        "/api/quiz/answer",
        json={
            "session_id": session_id,
            "question_id": question_id,
            "answer": answer
        }
    )
    data: QuizAnswerResponse = response.json()

    # Type narrowing через проверку discriminator
    if data["type"] == "continue":
        # TypeScript-style type narrowing работает и в Python 3.10+
        # Теперь data имеет тип ContinueResponse
        await show_next_question(data["next_question"])
        await show_timer(data["time_remaining_seconds"])
        await show_progress(data["questions_answered"])

    elif data["type"] == "end":
        # data имеет тип EndResponse
        results = data["results"]
        reason = data["reason"]

        if reason == "timeout":
            await send_message("⏰ Время вышло!")
        else:
            await send_message("✅ Все вопросы отвечены!")

        await show_results(results)
```

### Альтернативный вариант с isinstance (для старых Python версий)

```python
from pydantic import BaseModel

class QuizContinueResponse(BaseModel):
    type: Literal["continue"]
    time_remaining_seconds: int
    questions_answered: int
    next_question: dict

class QuizEndResponse(BaseModel):
    type: Literal["end"]
    reason: str
    results: dict

async def submit_answer(session_id: str, question_id: str, answer: str) -> None:
    response = await http_client.post(...)

    # Парсим с Pydantic
    data_dict = response.json()

    if data_dict["type"] == "continue":
        data = QuizContinueResponse(**data_dict)
        await show_next_question(data.next_question)

    elif data_dict["type"] == "end":
        data = QuizEndResponse(**data_dict)
        await show_results(data.results)
```

## Client Side (TypeScript)

TypeScript имеет нативную поддержку discriminated unions:

```typescript
interface QuestionOption {
    key: 'A' | 'B' | 'C' | 'D';
    text: string;
}

interface Question {
    id: string;
    text: string;
    block_name: string;
    options: QuestionOption[];
    question_number: number;
}

interface QuizContinueResponse {
    type: 'continue';
    time_remaining_seconds: number;
    questions_answered: number;
    next_question: Question;
}

interface QuizEndResponse {
    type: 'end';
    reason: 'timeout' | 'all_questions_answered';
    results: {
        session_id: string;
        total_questions: number;
        correct_answers: number;
        accuracy: number;
        // ... other fields
    };
}

type QuizAnswerResponse = QuizContinueResponse | QuizEndResponse;

async function submitAnswer(
    sessionId: string,
    questionId: string,
    answer: string
): Promise<void> {
    const response = await fetch('/api/quiz/answer', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, question_id: questionId, answer })
    });

    const data: QuizAnswerResponse = await response.json();

    // Type narrowing работает автоматически
    if (data.type === 'continue') {
        // TypeScript знает, что data - это QuizContinueResponse
        showNextQuestion(data.next_question);
        showTimer(data.time_remaining_seconds);
        showProgress(data.questions_answered);
    } else {
        // TypeScript знает, что data - это QuizEndResponse
        if (data.reason === 'timeout') {
            showMessage('⏰ Время вышло!');
        } else {
            showMessage('✅ Все вопросы отвечены!');
        }
        showResults(data.results);
    }
}
```

## Client Side (Telegram Bot - aiogram)

Реальный пример для aiogram (популярная библиотека для Telegram ботов):

```python
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import httpx

router = Router()

class QuizStates(StatesGroup):
    waiting_for_answer = State()

@router.message(Command("start_quiz"))
async def start_quiz(message: Message, state: FSMContext):
    """Start quiz command."""

    # Запрос на backend
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://backend:8000/api/quiz/start",
            json={
                "candidate_id": str(message.from_user.id),
                "track_id": 1  # TODO: let user select
            }
        )
        data = response.json()

    # Сохранить session_id в FSM
    await state.update_data(
        session_id=data["session_id"],
        expires_at=data["expires_at"]
    )
    await state.set_state(QuizStates.waiting_for_answer)

    # Показать первый вопрос
    await show_question(message, data["question"])


async def show_question(message: Message, question: dict):
    """Display question with inline keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    text = f"❓ <b>Вопрос {question['question_number']}</b>\n\n"
    text += f"{question['text']}\n\n"
    text += f"📚 Блок: {question['block_name']}\n\n"

    # Создать кнопки для вариантов ответа
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{opt['key']}. {opt['text']}",
            callback_data=f"answer:{question['id']}:{opt['key']}"
        )]
        for opt in question["options"]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    """Handle answer button press."""

    # Парсим callback data: "answer:question_id:A"
    _, question_id, answer = callback.data.split(":")

    # Получить session_id из FSM
    data = await state.get_data()
    session_id = data["session_id"]

    # Отправить ответ на backend
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://backend:8000/api/quiz/answer",
            json={
                "session_id": session_id,
                "question_id": question_id,
                "answer": answer
            }
        )
        result = response.json()

    # Удалить кнопки у предыдущего вопроса
    await callback.message.edit_reply_markup(reply_markup=None)

    # Обработать ответ через discriminator
    if result["type"] == "continue":
        # Квиз продолжается - показать следующий вопрос
        minutes = result["time_remaining_seconds"] // 60
        seconds = result["time_remaining_seconds"] % 60

        await callback.message.answer(
            f"⏱ Осталось времени: {minutes}:{seconds:02d}\n"
            f"📊 Отвечено вопросов: {result['questions_answered']}"
        )

        await show_question(callback.message, result["next_question"])

    elif result["type"] == "end":
        # Квиз завершен - показать результаты
        await state.clear()

        results = result["results"]

        text = "🏁 <b>Квиз завершен!</b>\n\n"

        if result["reason"] == "timeout":
            text += "⏰ Время вышло\n\n"
        else:
            text += "✅ Все вопросы отвечены\n\n"

        text += f"📊 <b>Результаты:</b>\n"
        text += f"• Всего вопросов: {results['total_questions']}\n"
        text += f"• Правильных ответов: {results['correct_answers']}\n"
        text += f"• Точность: {results['accuracy']:.1f}%\n\n"

        text += "📚 <b>По блокам:</b>\n"
        for block in results["blocks_performance"]:
            text += f"• {block['block_name']}: {block['correct']}/{block['total']} ({block['accuracy']:.1f}%)\n"

        await callback.message.answer(text, parse_mode="HTML")

    await callback.answer()
```

## Преимущества этого подхода

### 1. Type Safety

✅ TypeScript/Python type checkers понимают структуру
✅ Автодополнение в IDE работает корректно
✅ Невозможно обратиться к полям неправильного типа

### 2. Явность

✅ Сразу видно, что может быть два типа ответа
✅ Нельзя забыть обработать один из случаев (линтер предупредит)

### 3. Документация

✅ OpenAPI автоматически генерирует правильную схему с oneOf
✅ Swagger UI показывает оба варианта
✅ Клиентские SDK генерируются корректно

### 4. Простота

✅ Не нужны дополнительные эндпоинты
✅ Один HTTP запрос вместо двух
✅ Атомарная операция

## Пример HTTP ответов

### Квиз продолжается

```http
POST /api/quiz/answer
Content-Type: application/json

{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "question_id": "660e8400-e29b-41d4-a716-446655440001",
    "answer": "A"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "type": "continue",
    "time_remaining_seconds": 823,
    "questions_answered": 5,
    "next_question": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "text": "Что вернет list.pop()?",
        "block_name": "Python Basics",
        "options": [
            {"key": "A", "text": "Последний элемент"},
            {"key": "B", "text": "Первый элемент"},
            {"key": "C", "text": "None"},
            {"key": "D", "text": "Ошибку"}
        ],
        "question_number": 6
    }
}
```

### Квиз завершен

```http
POST /api/quiz/answer
Content-Type: application/json

{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "question_id": "880e8400-e29b-41d4-a716-446655440012",
    "answer": "C"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "type": "end",
    "reason": "timeout",
    "results": {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "total_questions": 12,
        "correct_answers": 9,
        "wrong_answers": 3,
        "accuracy": 75.0,
        "completion_time_seconds": 900,
        "blocks_performance": [
            {
                "block_name": "Algorithms",
                "correct": 4,
                "total": 5,
                "accuracy": 80.0
            },
            {
                "block_name": "Python Basics",
                "correct": 5,
                "total": 7,
                "accuracy": 71.4
            }
        ]
    }
}
```

## Резюме

**Discriminated Union с полем `type` - это стандартный и элегантный паттерн для таких случаев.**

Преимущества:
- ✅ Type-safe на всех уровнях
- ✅ Понятная обработка на клиенте (просто `if data["type"] == "continue"`)
- ✅ Автоматическая документация в OpenAPI
- ✅ Один endpoint вместо двух
- ✅ Атомарная операция (нет race conditions)

Это лучше чем:
- ❌ Два отдельных endpoint'а (сложнее логика, больше запросов)
- ❌ Опциональные поля (неявно, легко ошибиться)
- ❌ HTTP status codes для различения (не semantic)
