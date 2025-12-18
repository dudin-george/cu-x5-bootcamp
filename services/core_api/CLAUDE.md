# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

X5 Recruitment System Backend - FastAPI-based recruitment platform for X5 Group internship programs. The system handles candidate applications, vacancy management, hiring manager workflows, and interview scheduling with Telegram bot integration.

## Development Commands

### Running the Application
```bash
# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Using Poetry
poetry run uvicorn app.main:app --reload
```

### Database Migrations
```bash
# Create a new migration (auto-generate from models)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade one migration
alembic downgrade -1

# View migration history
alembic history
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest app/tests/test_auth.py
```

### Dependency Management
```bash
# Install dependencies
poetry install

# Add new dependency
poetry add package-name

# Update dependencies
poetry update

# Export requirements.txt
poetry export -f requirements.txt --output requirements.txt
```

## Architecture

### Module Structure

The application follows a **modular architecture** where each feature domain is isolated in `app/modules/`:

```
app/
├── core/           # Cross-cutting concerns (config, database, security, exceptions)
├── shared/         # Shared models and utilities used across modules
├── modules/        # Feature modules (auth, candidates, vacancies, hiring_managers)
└── migrations/     # Alembic database migrations
```

Each module follows the same pattern:
- `models.py` - SQLAlchemy ORM models
- `schemas.py` - Pydantic request/response schemas
- `router.py` - FastAPI route handlers
- `service.py` - Business logic layer

### Authentication Architecture

Authentication is handled through JWT tokens with a two-tier user model:

1. **Base User Model** (`app/shared/models.py`):
   - Shared across all user types
   - Contains email, password_hash, role (candidate/recruiter)
   - Located in `shared/` because it's referenced by multiple modules

2. **Role-Specific Models**:
   - `Candidate` model in `app/modules/candidates/models.py`
   - `HiringManager` model in `app/modules/hiring_managers/models.py`
   - Both use `telegram_id` as the primary identifier (not User.id)

**Important**: The system uses Telegram-based authentication. Users authenticate via Telegram bots, not email/password. The User model exists for future extensibility but current authentication flow is Telegram-only.

### Database Models Relationships

Key relationships to understand:

1. **Tracks → Vacancies**: One-to-many (a track has multiple vacancies)
2. **HiringManager → Vacancies**: One-to-many (a manager creates multiple vacancies)
3. **Vacancy ↔ Candidate** (through CandidatePool): Many-to-many with metadata
   - `CandidatePool` is the association table with extra fields (status, interview details, notes)
   - Tracks candidate movement through the hiring funnel
   - Constraint: One candidate can only be in one vacancy's pool once (`uq_vacancy_candidate`)

4. **CandidatePool → InterviewFeedback**: One-to-one (feedback after interview)

### Dependency Injection Pattern

The application uses FastAPI's dependency injection extensively:

- `DBSession`: Type alias for `AsyncSession` via `get_db()` dependency
- `CurrentUserId`: Type alias for extracting user ID from JWT token
- Both defined in `app/core/dependencies.py`

**Usage in routers**:
```python
async def endpoint(db: DBSession, user_id: CurrentUserId):
    # db is an AsyncSession instance
    # user_id is extracted from Bearer token
```

### Service Layer Pattern

Business logic is isolated in service classes (e.g., `CandidateService`, `AuthService`). Services are instantiated per-request and receive the database session:

```python
# In router
service = CandidateService(db)
result = await service.create_candidate(data)
```

This keeps routers thin and focused on HTTP concerns while services handle business logic.

### Configuration Management

Settings are managed via Pydantic Settings (`app/core/config.py`):
- Loads from `.env` file
- Type-safe configuration with defaults
- Accessed globally via `settings` singleton
- Environment variables are case-insensitive

**Key settings**:
- `database_url`: PostgreSQL connection (async)
- `secret_key`: JWT signing key
- `frontend_url`: CORS configuration

## Important Patterns and Conventions

### Async/Await Throughout
All database operations are async. Always use:
- `async def` for route handlers and service methods
- `await` for database queries
- `AsyncSession` for database sessions

### UUID vs Integer IDs
- `User`, `Candidate`, `HiringManager`, `CandidatePool`, `InterviewFeedback`: Use UUID
- `Track`, `Vacancy`: Use auto-incrementing integers
- Reason: UUIDs prevent enumeration attacks for user-related entities

### JSONB Fields
Several models use PostgreSQL JSONB for flexible data:
- `Candidate.preferred_tracks`: List of track IDs in priority order
- `Candidate.achievements`: Free-form list of strings
- `Candidate.domains`: Areas of interest/expertise

When modifying these fields, be aware they're not strongly typed at the database level.

### Timestamp Handling
All models use UTC timestamps:
```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
)
```

Always use `datetime.now(timezone.utc)` for consistency.

### Enum Usage
Status enums are defined in `app/shared/enums.py`:
- `UserRole`: candidate, recruiter
- `VacancyStatus`: DRAFT, ACTIVE, ABORTED
- `CandidatePoolStatus`: VIEWED, SELECTED, INTERVIEW_SCHEDULED, INTERVIEWED, FINALIST, OFFER_SENT, REJECTED

These are stored as strings in the database and mapped to Python Enums.

## Migration Notes

### Creating Migrations
When adding new models or modifying existing ones:
1. Update the model in the appropriate `models.py`
2. Import the model in `app/migrations/env.py` if it's a new model
3. Run `alembic revision --autogenerate -m "description"`
4. **Always review** the generated migration - autogenerate can miss certain changes
5. Test the migration: `alembic upgrade head` then `alembic downgrade -1`

### Migration Script Location
Migrations are in `app/migrations/versions/`. The `alembic.ini` configuration points to `app/migrations` as the script location.

## API Documentation

FastAPI auto-generates interactive docs:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI JSON: `http://localhost:8000/api/openapi.json`

All endpoints are prefixed with `/api/`.

## External Dependencies

The system integrates with:
- **Calendly**: Hiring managers have `calendly_id` for interview scheduling integration
