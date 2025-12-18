import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# 1. Явно указываем путь к .env, относительно текущей директории
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
env_path = os.path.join(BASE_DIR, ".env")
print(f"Loading .env from: {env_path}")  # для отладки
load_dotenv(env_path)

# 2. Добавляем backend в sys.path, чтобы импорт моделей работал
sys.path.append(BASE_DIR)

# 3. Alembic config
config = context.config

# 4. Получаем синхронный URL для Alembic и очищаем его от невидимых символов
alembic_url = os.getenv("DATABASE_URL_SYNC")
if not alembic_url:
    raise RuntimeError("DATABASE_URL_SYNC is not set in .env file")
alembic_url = alembic_url.strip()  # убираем \r, пробелы и BOM
config.set_main_option("sqlalchemy.url", alembic_url)

# 5. Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 6. Импорт метаданных моделей
from app.core.database import Base

# Импорт всех моделей для автогенерации миграций
from app.shared.models import User  # noqa: F401
from app.modules.candidates.models import Candidate  # noqa: F401
from app.modules.vacancies.models import Track, Vacancy, CandidatePool  # noqa: F401
from app.modules.hiring_managers.models import HiringManager  # noqa: F401
# TODO: recruitment and notifications modules need to be redesigned to work with new architecture
# from app.modules.recruitment.models import Application, VacancyApplication, Interview  # noqa: F401
# from app.modules.notifications.models import Notification  # noqa: F401

target_metadata = Base.metadata

# 7. Режим offline
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# 8. Режим online
def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
