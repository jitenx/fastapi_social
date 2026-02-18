from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your models and settings
from app.models.models import Base
from app.config.config import settings

config = context.config

# 1. Logic to handle the DB URL dynamically
# If database_host is missing or set to a local string, assume SQLite
if settings.database_com != "sqlite":
    # Use PostgreSQL format
    db_url = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"
else:
    # Use SQLite format (adjust the filename as needed)
    db_url = "sqlite:///./sql_app.db"

config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Required for SQLite to allow table modifications
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Get the URL we set above
    configuration = config.get_section(config.config_ini_section, {})

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # 2. Check the dialect name to apply SQLite-specific logic if needed
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Essential for SQLite compatibility
            render_as_batch=True,
            # Optional: Ensures constraint names are handled properly
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
