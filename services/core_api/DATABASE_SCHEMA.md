# Database Schema - X5 Recruitment System

Полное описание структуры базы данных системы рекрутинга X5 Group.

## Обзор

База данных построена на **PostgreSQL** с использованием SQLAlchemy 2.0 ORM. Использует как UUID (для пользовательских сущностей), так и integer (для системных справочников) в качестве первичных ключей.

### Основные таблицы

1. **candidates** - профили кандидатов
2. **hiring_managers** - профили hiring managers
3. **tracks** - треки/направления стажировки
4. **vacancies** - вакансии
5. **candidate_pools** - журнал движения кандидатов по воронке вакансий
6. **interview_feedbacks** - фидбек после интервью
7. **quiz_blocks** - блоки вопросов для квизов
8. **track_quiz_blocks** - связь треков и блоков квизов
9. **quiz_questions** - банк вопросов для квизов
10. **quiz_sessions** - сессии прохождения квизов
11. **quiz_answers** - ответы кандидатов на вопросы
12. **users** - системные пользователи (не используется в текущей реализации)

---

## Таблица: `candidates`

Профили кандидатов на стажировку.

### Колонки

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| `id` | UUID | PRIMARY KEY, UNIQUE, INDEX | Уникальный UUID кандидата |
| `telegram_id` | BIGINT | UNIQUE, NOT NULL, INDEX | Telegram user ID (основной идентификатор) |
| `full_name` | VARCHAR(255) | NOT NULL | Полное имя кандидата |
| `phone` | VARCHAR(20) | NULL | Номер телефона |
| `location` | VARCHAR(255) | NULL | Местоположение (город, страна) |
| `preferred_tracks` | JSONB | NOT NULL, DEFAULT '[]' | Список ID треков в порядке приоритета |
| `university` | VARCHAR(255) | NULL | Название университета |
| `course` | INTEGER | NULL | Курс обучения (1-6) |
| `achievements` | JSONB | NOT NULL, DEFAULT '[]' | Достижения (олимпиады, проекты, etc.) |
| `domains` | JSONB | NOT NULL, DEFAULT '[]' | Области интересов (ML, Web, Mobile, etc.) |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда профиль был создан |
| `updated_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда профиль последний раз обновлялся |

### Связи

- **ONE-TO-MANY** → `candidate_pools`: Один кандидат может участвовать в нескольких вакансиях

### Индексы

- `id` (PRIMARY KEY, UNIQUE)
- `telegram_id` (UNIQUE)

### Примечания

- `telegram_id` используется как основной способ идентификации кандидата
- JSONB поля (`preferred_tracks`, `achievements`, `domains`) позволяют гибко хранить массивы данных
- При удалении кандидата CASCADE удаляет все связанные записи в `candidate_pools`

---

## Таблица: `hiring_managers`

Профили hiring managers, создающих вакансии.

### Колонки

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| `id` | UUID | PRIMARY KEY, UNIQUE, INDEX | Уникальный UUID менеджера |
| `telegram_id` | BIGINT | UNIQUE, NOT NULL, INDEX | Telegram user ID |
| `calendly_id` | VARCHAR(255) | NULL | ID в системе Calendly |
| `first_name` | VARCHAR(255) | NOT NULL | Имя |
| `last_name` | VARCHAR(255) | NOT NULL | Фамилия |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда профиль был создан |
| `updated_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда профиль последний раз обновлялся |

### Связи

- **ONE-TO-MANY** → `vacancies`: Один HM может создавать несколько вакансий

### Индексы

- `id` (PRIMARY KEY, UNIQUE)
- `telegram_id` (UNIQUE)

### Примечания

- `calendly_id` используется для интеграции с внешним сервисом Calendly для планирования интервью
- При удалении HM CASCADE удаляет все созданные им вакансии

---

## Таблица: `tracks`

Треки (направления) стажировки.

### Колонки

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Уникальный ID трека |
| `name` | VARCHAR(255) | UNIQUE, NOT NULL | Название трека (например, 'Python Backend', 'Frontend') |
| `description` | TEXT | NULL | Описание трека |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Трек активен и доступен для подачи заявок |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда трек был создан |
| `updated_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда трек последний раз обновлялся |

### Связи

- **ONE-TO-MANY** → `vacancies`: Один трек может иметь несколько вакансий

### Индексы

- `id` (PRIMARY KEY)
- `name` (UNIQUE)

### Примечания

- Это справочная таблица, управляется администраторами
- При удалении трека CASCADE удаляет все связанные вакансии

---

## Таблица: `vacancies`

Открытые вакансии (позиции для стажировки).

### Колонки

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Уникальный ID вакансии |
| `track_id` | INTEGER | FOREIGN KEY → `tracks.id`, NOT NULL, INDEX | Ссылка на трек |
| `hiring_manager_id` | UUID | FOREIGN KEY → `hiring_managers.id`, NOT NULL, INDEX | Ссылка на HM |
| `description` | TEXT | NOT NULL | Описание позиции |
| `status` | ENUM (VacancyStatus) | NOT NULL, INDEX, DEFAULT 'DRAFT' | Статус вакансии |
| `next_interview_at` | TIMESTAMP WITH TIMEZONE | NULL | Дата ближайшего собеседования |
| `next_interview_link` | VARCHAR(500) | NULL | Ссылка на собеседование (Calendly/Meet) |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда вакансия была создана |
| `updated_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда вакансия последний раз обновлялась |

### Enum: VacancyStatus

```python
DRAFT = "DRAFT"       # Черновик, не опубликована
ACTIVE = "ACTIVE"     # Активна, идет подбор кандидатов
ABORTED = "ABORTED"   # Отменена, закрыта
```

### Связи

- **MANY-TO-ONE** → `tracks`: Вакансия принадлежит одному треку
- **MANY-TO-ONE** → `hiring_managers`: Вакансия создана одним HM
- **ONE-TO-MANY** → `candidate_pools`: Вакансия имеет множество кандидатов в воронке

### Индексы

- `id` (PRIMARY KEY)
- `track_id` (INDEX)
- `hiring_manager_id` (INDEX)
- `status` (INDEX)

### Cascade правила

- `ON DELETE CASCADE` для `track_id` (при удалении трека удаляются вакансии)
- `ON DELETE CASCADE` для `hiring_manager_id` (при удалении HM удаляются его вакансии)
- При удалении вакансии CASCADE удаляет все записи в `candidate_pools`

---

## Таблица: `candidate_pools`

Журнал движения кандидата по воронке конкретной вакансии. Это **ассоциативная таблица** между `candidates` и `vacancies` с дополнительными полями.

### Колонки

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| `id` | UUID | PRIMARY KEY, UNIQUE, INDEX | Уникальный UUID записи в пуле |
| `vacancy_id` | INTEGER | FOREIGN KEY → `vacancies.id`, NOT NULL, INDEX | Ссылка на вакансию |
| `candidate_id` | UUID | FOREIGN KEY → `candidates.id`, NOT NULL, INDEX | Ссылка на кандидата |
| `status` | ENUM (CandidatePoolStatus) | NOT NULL, INDEX | Текущий статус кандидата в воронке |
| `interview_scheduled_at` | TIMESTAMP WITH TIMEZONE | NULL | Дата и время назначенного интервью |
| `interview_link` | VARCHAR(500) | NULL | Ссылка на интервью (Calendly/Meet) |
| `notes` | TEXT | NULL | Заметки HM о кандидате |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда кандидат попал в этот статус |
| `updated_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда запись последний раз обновлялась |

### Enum: CandidatePoolStatus

```python
VIEWED = "VIEWED"                       # Кандидат просмотрен HM (Tinder swipe)
SELECTED = "SELECTED"                   # Кандидат выбран для интервью
INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"  # Интервью назначено
INTERVIEWED = "INTERVIEWED"             # Интервью проведено
FINALIST = "FINALIST"                   # В списке финалистов
OFFER_SENT = "OFFER_SENT"              # Оффер отправлен
REJECTED = "REJECTED"                   # Отклонен (может быть на любом этапе)
```

### Связи

- **MANY-TO-ONE** → `vacancies`: Запись принадлежит одной вакансии
- **MANY-TO-ONE** → `candidates`: Запись связана с одним кандидатом
- **ONE-TO-ONE** → `interview_feedbacks`: Одна запись может иметь один фидбек

### Constraints

- **UNIQUE CONSTRAINT**: `uq_vacancy_candidate` на `(vacancy_id, candidate_id)` - один кандидат может быть добавлен в воронку вакансии только один раз

### Индексы

- `id` (PRIMARY KEY, UNIQUE)
- `vacancy_id` (INDEX)
- `candidate_id` (INDEX)
- `status` (INDEX)
- `idx_vacancy_status` (COMPOSITE INDEX на `vacancy_id` и `status`)

### Cascade правила

- `ON DELETE CASCADE` для `vacancy_id` (при удалении вакансии удаляются записи пула)
- `ON DELETE CASCADE` для `candidate_id` (при удалении кандидата удаляются записи пула)

### Примечания

- Это **Rich Association Table** - хранит не только связь, но и состояние процесса
- Используется для реализации "Tinder mode" - HM свайпает кандидатов
- Статус `VIEWED` устанавливается при первом просмотре (swipe right/left/skip)
- `interview_scheduled_at` и `interview_link` заполняются через интеграцию с Calendly

---

## Таблица: `interview_feedbacks`

Фидбек hiring manager после проведенного интервью.

### Колонки

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| `id` | UUID | PRIMARY KEY, UNIQUE, INDEX | Уникальный UUID фидбека |
| `pool_id` | UUID | FOREIGN KEY → `candidate_pools.id`, UNIQUE, NOT NULL, INDEX | Ссылка на запись в candidate pool |
| `feedback_text` | TEXT | NOT NULL | Комментарий HM после интервью |
| `decision` | VARCHAR(50) | NOT NULL | Решение HM |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда фидбек был создан |

### Возможные значения decision

```python
"reject_globally"  # Отказ во всей компании (статус pool → REJECTED)
"reject_team"      # Отказ по команде, другие HM могут смотреть (статус → REJECTED)
"freeze"           # Поморозим и посмотрим позже (статус → INTERVIEWED)
"to_finalist"      # В список финалистов (статус → FINALIST)
```

### Связи

- **ONE-TO-ONE** → `candidate_pools`: Фидбек связан с одной записью в пуле

### Constraints

- **UNIQUE**: `pool_id` - для одной записи в пуле может быть только один фидбек

### Индексы

- `id` (PRIMARY KEY, UNIQUE)
- `pool_id` (UNIQUE, INDEX)

### Cascade правила

- `ON DELETE CASCADE` для `pool_id` (при удалении записи в пуле удаляется фидбек)

### Примечания

- Фидбек создается ПОСЛЕ проведения интервью
- `decision` влияет на обновление статуса в `candidate_pools`
- Невозможно создать два фидбека для одной записи в пуле (UNIQUE constraint)

---

## Таблица: `users`

Системные пользователи (кандидаты и рекрутеры) с email/password аутентификацией.

### Статус: НЕ ИСПОЛЬЗУЕТСЯ В ТЕКУЩЕЙ РЕАЛИЗАЦИИ

В текущей версии система использует Telegram-based идентификацию через `candidates.telegram_id` и `hiring_managers.telegram_id`. Эта таблица оставлена для возможной будущей реализации email/password аутентификации.

### Колонки

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| `id` | UUID | PRIMARY KEY, UNIQUE, INDEX | Уникальный UUID пользователя |
| `email` | VARCHAR(320) | UNIQUE, NOT NULL, INDEX | Email пользователя (логин) |
| `password_hash` | VARCHAR(128) | NOT NULL | Bcrypt-хэш пароля |
| `role` | ENUM (UserRole) | NOT NULL | Роль: candidate или recruiter |
| `telegram_id` | VARCHAR(100) | UNIQUE, NULL, INDEX | ID пользователя в Telegram |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Аккаунт активен/заблокирован |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда аккаунт был создан |
| `updated_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Когда аккаунт последний раз обновлялся |

### Enum: UserRole

```python
CANDIDATE = "candidate"
RECRUITER = "recruiter"
```

### Индексы

- `id` (PRIMARY KEY, UNIQUE)
- `email` (UNIQUE)
- `telegram_id` (UNIQUE, if not NULL)

---

## Диаграмма связей

```
┌─────────────────┐
│ hiring_managers │
│   (UUID)        │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐         ┌─────────────────┐
│     tracks      │         │   candidates    │
│   (INTEGER)     │         │     (UUID)      │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ 1:N                       │ 1:N
         │                           │
         ▼                           ▼
    ┌─────────────────┐        ┌─────────────────────┐
    │    vacancies    │◄──────►│  candidate_pools    │
    │   (INTEGER)     │  N:M   │      (UUID)         │
    └─────────────────┘        └──────────┬──────────┘
                                          │
                                          │ 1:1
                                          ▼
                               ┌─────────────────────┐
                               │interview_feedbacks  │
                               │      (UUID)         │
                               └─────────────────────┘
```

### Детали связей

1. **hiring_managers → vacancies** (ONE-TO-MANY)
   - Один HM создает много вакансий
   - Удаление HM → CASCADE удаление всех его вакансий

2. **tracks → vacancies** (ONE-TO-MANY)
   - Один трек содержит много вакансий
   - Удаление трека → CASCADE удаление всех вакансий этого трека

3. **vacancies ↔ candidates** через **candidate_pools** (MANY-TO-MANY)
   - Rich Association Table с собственным состоянием
   - Одна вакансия → много кандидатов в воронке
   - Один кандидат → может участвовать в нескольких вакансиях
   - UNIQUE constraint: один кандидат только один раз в воронке конкретной вакансии

4. **candidate_pools → interview_feedbacks** (ONE-TO-ONE)
   - Одна запись в пуле → один фидбек после интервью
   - UNIQUE constraint на `pool_id`

---

## Ключевые особенности архитектуры

### 1. Гибридная стратегия первичных ключей

- **UUID** - для пользовательских сущностей (`candidates`, `hiring_managers`, `candidate_pools`, `interview_feedbacks`)
  - Обеспечивает анонимность
  - Невозможно угадать ID
  - Подходит для распределенных систем

- **INTEGER** - для системных справочников (`tracks`, `vacancies`)
  - Простота использования в API
  - Лучшая производительность для JOIN операций
  - Предсказуемость для internal операций

### 2. Telegram-based идентификация

- `telegram_id` (BIGINT) - основной способ идентификации пользователей
- Используется вместо email/password аутентификации
- Уникальный и индексированный для быстрого поиска

### 3. JSONB для гибких данных

- `candidates.preferred_tracks` - массив integer
- `candidates.achievements` - массив строк
- `candidates.domains` - массив строк
- Позволяет избежать дополнительных таблиц для простых списков

### 4. Rich Association Table Pattern

`candidate_pools` - не просто связующая таблица, а полноценная сущность:
- Собственный UUID как PRIMARY KEY
- Хранит состояние процесса (`status`)
- Дополнительные поля (`notes`, `interview_scheduled_at`, `interview_link`)
- Временные метки для аудита

### 5. Cascade стратегия

- Используется агрессивная CASCADE стратегия для всех связей
- При удалении родителя → автоматически удаляются дочерние записи
- Упрощает код, но требует осторожности при удалении

### 6. Временные метки

Все таблицы имеют:
- `created_at` - timestamp создания
- `updated_at` - timestamp последнего обновления (автоматически через onupdate)
- Все timestamps с timezone (UTC)

### 7. Индексирование

Индексы созданы для:
- Всех первичных ключей
- Всех внешних ключей
- Полей для частого поиска (`telegram_id`, `status`)
- Composite index для частых запросов (`idx_vacancy_status`)

---

## Типичные запросы

### 1. Получить всех кандидатов вакансии с определенным статусом

```sql
SELECT c.*, cp.status, cp.notes
FROM candidates c
JOIN candidate_pools cp ON c.id = cp.candidate_id
WHERE cp.vacancy_id = :vacancy_id
  AND cp.status = 'FINALIST'
ORDER BY cp.created_at DESC;
```

### 2. Получить следующего непросмотренного кандидата для вакансии

```sql
SELECT c.*
FROM candidates c
WHERE c.id NOT IN (
    SELECT candidate_id
    FROM candidate_pools
    WHERE vacancy_id = :vacancy_id
)
LIMIT 1;
```

### 3. Статистика по вакансии

```sql
SELECT
    status,
    COUNT(*) as count
FROM candidate_pools
WHERE vacancy_id = :vacancy_id
GROUP BY status;
```

### 4. Все активные вакансии с информацией о треке и HM

```sql
SELECT
    v.*,
    t.name as track_name,
    hm.first_name || ' ' || hm.last_name as hm_name
FROM vacancies v
JOIN tracks t ON v.track_id = t.id
JOIN hiring_managers hm ON v.hiring_manager_id = hm.id
WHERE v.status = 'ACTIVE';
```

---

## Миграции

Миграции управляются через **Alembic**:

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

Файлы миграций находятся в `alembic/versions/`.

---

## Важные замечания

1. **Concurrent access**: PostgreSQL используется с asyncpg драйвером через SQLAlchemy AsyncSession
2. **Timezone**: Все timestamps хранятся в UTC с timezone awareness
3. **JSONB indexing**: При необходимости можно добавить GIN индексы на JSONB колонки
4. **Soft delete**: В текущей реализации не используется soft delete, все удаления физические
5. **Audit trail**: Временные метки (`created_at`, `updated_at`) обеспечивают базовый audit trail
