"""
Alembic Migration Environment

LEARNING NOTE:
Alembic handles database migrations - the process of updating your database
schema when your models change. Think of migrations as "version control for
your database structure."

Key commands:
- alembic revision --autogenerate -m "description" : Create a new migration
- alembic upgrade head : Apply all pending migrations
- alembic downgrade -1 : Rollback one migration

TUTORIAL: https://alembic.sqlalchemy.org/en/latest/tutorial.html
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your models and database config
# LEARNING NOTE: This import ensures all models are registered with Base
from app.database import Base
from app.models import *  # noqa: F401, F403 - Import all models
from app.config import get_settings

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# LEARNING NOTE:
# target_metadata tells Alembic about your models so it can auto-generate migrations
# by comparing your Python models to what's actually in the database
target_metadata = Base.metadata

# Get database URL from our settings (reads from .env)
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    LEARNING NOTE:
    Offline mode generates SQL without connecting to the database.
    Useful for reviewing migrations before applying them.
    """
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
    """
    Run migrations in 'online' mode.

    LEARNING NOTE:
    Online mode connects to the database and applies changes directly.
    This is what you'll use most of the time.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
