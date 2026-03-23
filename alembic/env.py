"""
Alembic Environment Configuration

This module configures Alembic to work with our database models
and Supabase/PostgreSQL connection.

Usage:
    # Run migrations
    alembic upgrade head
    
    # Create a new migration
    alembic revision --autogenerate -m "Add new table"
    
    # Rollback
    alembic downgrade -1
"""

from logging.config import fileConfig
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.models import Base
from config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    """Get database URL from environment or settings."""
    return os.getenv(
        "DATABASE_URL",
        settings.SUPABASE_DB_URL if hasattr(settings, 'SUPABASE_DB_URL') else None
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    if url is None:
        print("WARNING: DATABASE_URL not set. Running in offline mode with mock URL.")
        url = "postgresql://user:pass@localhost/dbname"
    
    config.set_main_option("sqlalchemy.url", url)
    
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
    url = get_url()
    if url is None:
        print("ERROR: DATABASE_URL not set. Please set DATABASE_URL environment variable.")
        print("For Supabase, you can find this in Settings > Database > Connection string")
        print("Format: postgresql://postgres.[project_ref]:[password]@host:port/postgres")
        sys.exit(1)
    
    config.set_main_option("sqlalchemy.url", url)
    
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
