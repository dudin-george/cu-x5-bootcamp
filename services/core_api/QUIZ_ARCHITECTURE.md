# Quiz System Architecture

Архитектура системы квизов для X5 Recruitment System.

## Обзор

Система квизов для проверки знаний кандидатов по выбранным трекам. Квиз длится 15 минут, кандидат отвечает на вопросы из разных блоков, цель - ответить правильно на максимальное количество вопросов.

## Workflow

```
1. Кандидат выбирает трек → POST /api/quiz/start
   ↓
   Response: {session_id, first_question, expires_at}

2. Кандидат отвечает → POST /api/quiz/answer
   ↓
   Backend проверяет:
   - Время не истекло?
   - Ответ правильный?
   ↓
   Response: {is_correct, next_question OR quiz_ended}

3. Повторяется пункт 2 до истечения 15 минут

4. Квиз завершается:
   - По таймауту (15 минут)
   - По явному завершению кандидатом (опционально)
   ↓
   Response: {quiz_ended: true, final_score, stats}
```

## Архитектурное решение: Request-Response Pattern

### Почему именно этот паттерн?

**1. Синхронность flow:**
- Telegram bot делает HTTP запрос
- Backend обрабатывает ответ + возвращает следующий вопрос
- Bot сразу показывает новый вопрос пользователю
- Нет необходимости в push-уведомлениях

**2. Простота:**
- Stateless HTTP endpoints
- Нет WebSocket инфраструктуры
- Легко тестировать и дебажить

**3. Атомарность:**
- В одной транзакции: сохранить ответ + получить новый вопрос
- Нет race conditions

**4. Естественность для Telegram Bot:**
- Боты работают по принципу "команда → ответ"
- Не нужны кнопки - бот просто парсит response и показывает вопрос

### Endpoints

```python
# 1. Начать квиз
POST /api/quiz/start
Body: {
    "candidate_id": "uuid",
    "track_id": 1
}
Response 200: {
    "session_id": "uuid",
    "track_name": "Python Backend",
    "total_duration_seconds": 900,  # 15 минут
    "started_at": "2025-01-15T10:00:00Z",
    "expires_at": "2025-01-15T10:15:00Z",
    "question": {
        "id": "uuid",
        "text": "Что такое декоратор в Python?",
        "block_name": "Python Basics",
        "options": [
            {"key": "A", "text": "Функция, которая модифицирует другую функцию"},
            {"key": "B", "text": "Класс для наследования"},
            {"key": "C", "text": "Библиотека для UI"},
            {"key": "D", "text": "Менеджер контекста"}
        ],
        "question_number": 1
    }
}

# 2. Отправить ответ и получить следующий вопрос
POST /api/quiz/answer
Body: {
    "session_id": "uuid",
    "question_id": "uuid",
    "answer": "A"  # Ключ выбранного варианта
}
Response 200 (квиз продолжается): {
    "is_correct": true,
    "correct_answer": "A",  # Показываем правильный ответ
    "time_remaining_seconds": 823,
    "questions_answered": 5,
    "correct_answers": 4,
    "quiz_ended": false,
    "next_question": {
        "id": "uuid",
        "text": "Что вернет list.pop()?",
        "block_name": "Python Basics",
        "options": [...],
        "question_number": 6
    }
}

Response 200 (время вышло): {
    "is_correct": true,
    "correct_answer": "A",
    "time_remaining_seconds": 0,
    "quiz_ended": true,
    "reason": "timeout",
    "final_results": {
        "total_questions": 12,
        "correct_answers": 9,
        "wrong_answers": 3,
        "accuracy": 75.0,
        "completion_time_seconds": 900,
        "blocks_performance": [
            {"block": "Algorithms", "correct": 4, "total": 5},
            {"block": "Python Basics", "correct": 5, "total": 7}
        ]
    }
}

# 3. Получить результаты квиза (опционально, для истории)
GET /api/quiz/results/{session_id}
Response 200: {
    "session_id": "uuid",
    "candidate_id": "uuid",
    "track_id": 1,
    "started_at": "...",
    "ended_at": "...",
    "duration_seconds": 900,
    "total_questions": 12,
    "correct_answers": 9,
    "score": 75.0,
    ...
}

# 4. История попыток кандидата
GET /api/quiz/attempts?candidate_id={uuid}
Response 200: [
    {
        "session_id": "uuid",
        "track_name": "Python Backend",
        "started_at": "...",
        "score": 75.0,
        "status": "completed"
    },
    ...
]
```

---

## Схема БД

### Новые таблицы

#### 1. `quiz_blocks`

Блоки вопросов (например, "Algorithms", "Python", "Frontend").

```sql
CREATE TABLE quiz_blocks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

#### 2. `track_quiz_blocks`

Связь между треками и блоками (many-to-many).

```sql
CREATE TABLE track_quiz_blocks (
    track_id INTEGER NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    block_id INTEGER NOT NULL REFERENCES quiz_blocks(id) ON DELETE CASCADE,
    questions_count INTEGER NOT NULL DEFAULT 5,  -- Сколько вопросов из этого блока в квизе
    PRIMARY KEY (track_id, block_id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Пример:
-- track_id=1 (Python Backend), block_id=1 (Algorithms), questions_count=5
-- track_id=1 (Python Backend), block_id=2 (Python), questions_count=10
-- track_id=2 (Frontend), block_id=1 (Algorithms), questions_count=5
-- track_id=2 (Frontend), block_id=3 (JavaScript), questions_count=10
```

#### 3. `quiz_questions`

Банк вопросов.

```sql
CREATE TABLE quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    block_id INTEGER NOT NULL REFERENCES quiz_blocks(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    difficulty VARCHAR(20) DEFAULT 'medium',  -- easy, medium, hard
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    INDEX idx_block_active (block_id, is_active)
);
```

#### 4. `quiz_sessions`

Сессии прохождения квиза (попытки).

```sql
CREATE TABLE quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',  -- in_progress, completed, expired
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,  -- started_at + 15 минут
    ended_at TIMESTAMP WITH TIME ZONE,
    total_questions INTEGER NOT NULL DEFAULT 0,
    correct_answers INTEGER NOT NULL DEFAULT 0,
    wrong_answers INTEGER NOT NULL DEFAULT 0,
    score DECIMAL(5,2),  -- Процент правильных ответов
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    INDEX idx_candidate (candidate_id),
    INDEX idx_status (status),
    INDEX idx_track (track_id)
);
```

#### 5. `quiz_answers`

Ответы кандидата в рамках сессии.

```sql
CREATE TABLE quiz_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
    candidate_answer CHAR(1) NOT NULL CHECK (candidate_answer IN ('A', 'B', 'C', 'D')),
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    time_taken_seconds INTEGER,  -- Сколько времени потратили на ответ
    INDEX idx_session (session_id),
    UNIQUE (session_id, question_id)  -- Один вопрос - один ответ в рамках сессии
);
```

---

## Диаграмма связей

```
tracks (1) ←──────→ (M) track_quiz_blocks (M) ←──────→ (1) quiz_blocks
                                                              │
                                                              │ (1)
                                                              │
                                                              ↓
                                                        quiz_questions (M)
                                                              │
                                                              │
                                                              ↓
candidates (1) ──→ quiz_sessions (1) ──→ quiz_answers (M) ──┘
            (M)                    (M)
```

---

## Алгоритм работы

### 1. Начало квиза (`POST /api/quiz/start`)

```python
async def start_quiz(candidate_id: UUID, track_id: int):
    # 1. Проверить, что у кандидата нет активной сессии по этому треку
    existing = await get_active_session(candidate_id, track_id)
    if existing:
        raise HTTPException(400, "Active quiz session already exists")

    # 2. Получить конфигурацию блоков для трека
    track_blocks = await get_track_quiz_blocks(track_id)
    # [{"block_id": 1, "questions_count": 5}, {"block_id": 2, "questions_count": 10}]

    # 3. Создать сессию квиза
    session = await create_quiz_session(
        candidate_id=candidate_id,
        track_id=track_id,
        expires_at=now + timedelta(minutes=15)
    )

    # 4. Выбрать первый вопрос (рандомно из первого блока)
    first_block = track_blocks[0]
    question = await get_random_question_from_block(first_block.block_id)

    # 5. Вернуть ответ с первым вопросом
    return {
        "session_id": session.id,
        "expires_at": session.expires_at,
        "question": format_question(question)
    }
```

### 2. Отправка ответа (`POST /api/quiz/answer`)

```python
async def submit_answer(session_id: UUID, question_id: UUID, answer: str):
    # 1. Получить сессию
    session = await get_session(session_id)
    if not session:
        raise HTTPException(404, "Quiz session not found")

    # 2. Проверить время
    now = datetime.now(timezone.utc)
    if now >= session.expires_at:
        # Время вышло - завершить квиз
        await finalize_session(session)
        return {
            "quiz_ended": True,
            "reason": "timeout",
            "final_results": await calculate_results(session)
        }

    # 3. Проверить ответ
    question = await get_question(question_id)
    is_correct = (answer == question.correct_answer)

    # 4. Сохранить ответ
    await save_answer(
        session_id=session_id,
        question_id=question_id,
        answer=answer,
        is_correct=is_correct
    )

    # 5. Обновить статистику сессии
    await update_session_stats(session_id, is_correct)

    # 6. Выбрать следующий вопрос
    next_question = await get_next_question(session)
    if not next_question:
        # Все вопросы закончились
        await finalize_session(session)
        return {
            "is_correct": is_correct,
            "quiz_ended": True,
            "reason": "all_questions_answered",
            "final_results": await calculate_results(session)
        }

    # 7. Вернуть результат + следующий вопрос
    return {
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "time_remaining_seconds": (session.expires_at - now).total_seconds(),
        "questions_answered": session.total_questions,
        "correct_answers": session.correct_answers,
        "quiz_ended": False,
        "next_question": format_question(next_question)
    }
```

### 3. Выбор следующего вопроса

**Стратегия**: Последовательно проходим по блокам трека, для каждого блока выбираем рандомные вопросы.

```python
async def get_next_question(session: QuizSession):
    # 1. Получить конфигурацию блоков для трека
    track_blocks = await get_track_quiz_blocks(session.track_id)
    # [{"block_id": 1, "questions_count": 5}, {"block_id": 2, "questions_count": 10}]

    # 2. Получить уже заданные вопросы в этой сессии
    answered_questions = await get_answered_question_ids(session.id)

    # 3. Для каждого блока проверить, сколько вопросов уже было
    for block_config in track_blocks:
        block_id = block_config.block_id
        required_count = block_config.questions_count

        # Сколько вопросов из этого блока уже задали?
        block_answered_count = await count_block_questions_in_session(
            session.id, block_id
        )

        if block_answered_count < required_count:
            # Нужно взять еще вопрос из этого блока
            question = await get_random_question_from_block(
                block_id,
                exclude_ids=answered_questions
            )
            if question:
                return question

    # Все вопросы из всех блоков закончились
    return None
```

---

## Важные детали реализации

### 1. Проверка времени

**На каждом запросе** проверяем `expires_at`:

```python
if datetime.now(timezone.utc) >= session.expires_at:
    await finalize_session(session)
    return {"quiz_ended": True, "reason": "timeout"}
```

### 2. Atomic операции

Сохранение ответа и обновление статистики в **одной транзакции**:

```python
async with db.begin():
    # Сохранить ответ
    await save_answer(...)
    # Обновить счетчики
    await update_session_stats(...)
```

### 3. Предотвращение повторных ответов

UNIQUE constraint на `(session_id, question_id)` в таблице `quiz_answers`.

### 4. Рандомизация вопросов

```python
SELECT * FROM quiz_questions
WHERE block_id = :block_id
  AND is_active = TRUE
  AND id NOT IN (:answered_ids)
ORDER BY RANDOM()
LIMIT 1;
```

### 5. Финализация сессии

При завершении квиза (по timeout или по завершению всех вопросов):

```python
async def finalize_session(session: QuizSession):
    stats = await calculate_stats(session.id)

    await db.execute(
        UPDATE quiz_sessions
        SET status = 'completed',
            ended_at = NOW(),
            score = :score,
            total_questions = :total,
            correct_answers = :correct,
            wrong_answers = :wrong
        WHERE id = :session_id
    )
```

---

## Дополнительные фичи (опционально)

### 1. Ограничение попыток

Можно ограничить количество попыток по треку:

```python
attempts_count = await count_quiz_attempts(candidate_id, track_id)
if attempts_count >= MAX_ATTEMPTS:
    raise HTTPException(400, "Maximum attempts reached")
```

### 2. Cooldown между попытками

```python
last_attempt = await get_last_attempt(candidate_id, track_id)
if last_attempt and (now - last_attempt.ended_at) < timedelta(hours=24):
    raise HTTPException(400, "Please wait 24 hours before retrying")
```

### 3. Difficulty progression

Можно усложнять вопросы по мере правильных ответов:

```python
if session.correct_answers / session.total_questions > 0.8:
    difficulty = 'hard'
else:
    difficulty = 'medium'

question = await get_question_with_difficulty(block_id, difficulty, ...)
```

### 4. Статистика по блокам

Сохранять performance по каждому блоку для аналитики:

```sql
SELECT
    qb.name as block_name,
    COUNT(*) as total,
    SUM(CASE WHEN qa.is_correct THEN 1 ELSE 0 END) as correct
FROM quiz_answers qa
JOIN quiz_questions qq ON qa.question_id = qq.id
JOIN quiz_blocks qb ON qq.block_id = qb.id
WHERE qa.session_id = :session_id
GROUP BY qb.name;
```

---

## Миграции

### Создание таблиц

```bash
alembic revision --autogenerate -m "add quiz tables"
alembic upgrade head
```

### Заполнение блоков (seed data)

```python
# scripts/seed_quiz_data.py
blocks = [
    {"name": "Algorithms", "description": "Data structures and algorithms"},
    {"name": "Python Basics", "description": "Python fundamentals"},
    {"name": "Python Advanced", "description": "Advanced Python topics"},
    {"name": "JavaScript", "description": "JavaScript fundamentals"},
    {"name": "React", "description": "React framework"},
]

# Связать блоки с треками
track_blocks = [
    {"track_id": 1, "block_id": 1, "questions_count": 5},   # Python Backend - Algorithms
    {"track_id": 1, "block_id": 2, "questions_count": 8},   # Python Backend - Python Basics
    {"track_id": 1, "block_id": 3, "questions_count": 7},   # Python Backend - Python Advanced
    {"track_id": 2, "block_id": 1, "questions_count": 5},   # Frontend - Algorithms
    {"track_id": 2, "block_id": 4, "questions_count": 10},  # Frontend - JavaScript
    {"track_id": 2, "block_id": 5, "questions_count": 5},   # Frontend - React
]
```

---

## Тестирование

### Unit тесты

```python
async def test_quiz_start():
    response = await client.post("/api/quiz/start", json={
        "candidate_id": candidate_id,
        "track_id": 1
    })
    assert response.status_code == 200
    assert "session_id" in response.json()
    assert "question" in response.json()

async def test_quiz_timeout():
    # Создать сессию с expires_at в прошлом
    session = await create_expired_session(...)

    response = await client.post("/api/quiz/answer", json={
        "session_id": session.id,
        "question_id": question_id,
        "answer": "A"
    })
    assert response.json()["quiz_ended"] == True
    assert response.json()["reason"] == "timeout"
```

---

## Performance соображения

### 1. Индексы

Все внешние ключи и поля для фильтрации должны быть проиндексированы:
- `quiz_answers.session_id`
- `quiz_sessions.candidate_id`
- `quiz_questions (block_id, is_active)`

### 2. Кеширование вопросов

Можно закешировать список вопросов для блока:

```python
@lru_cache(maxsize=100)
async def get_block_questions(block_id: int):
    # Загрузить все вопросы блока в память
    ...
```

### 3. Batch operations

При финализации сессии делать batch update вместо множественных запросов.

---

## Резюме

**Рекомендую реализовать именно Request-Response паттерн:**

1. ✅ Простой и понятный flow
2. ✅ Отлично работает с Telegram Bot
3. ✅ Не требует сложной инфраструктуры
4. ✅ Атомарные операции без race conditions
5. ✅ Легко тестировать

**Ключевые точки:**
- Вопрос в response body - это нормально и правильно
- Проверка времени на каждом запросе
- Рандомизация вопросов по блокам
- Финализация сессии при timeout
- UNIQUE constraint на (session_id, question_id)
