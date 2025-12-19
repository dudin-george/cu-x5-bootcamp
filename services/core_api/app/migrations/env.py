"""Alembic migrations environment configuration."""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# Add project root to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)

# Alembic config
config = context.config

# Get DATABASE_URL and convert async to sync
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

# Convert asyncpg URL to sync psycopg2 URL for Alembic
sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", sync_url)

# Logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import metadata from models
from app.core.database import Base

# Import all models for autogenerate
from app.shared.models import User  # noqa: F401
from app.modules.candidates.models import Candidate  # noqa: F401
from app.modules.vacancies.models import Track, Vacancy, CandidatePool, InterviewFeedback  # noqa: F401
from app.modules.hiring_managers.models import HiringManager  # noqa: F401
from app.modules.quiz.models import QuizBlock, QuizQuestion, QuizSession, QuizAnswer, TrackQuizBlock  # noqa: F401
from app.modules.tasks.models import TaskType, RecruiterTask  # noqa: F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
