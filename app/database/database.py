from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config.config import settings

# Async SQLAlchemy URL for PostgreSQL


if settings.database_com != "sqlite":
    DATABASE_URL = (
        f"postgresql+asyncpg://{settings.database_username}:"
        f"{settings.database_password}@{settings.database_host}:"
        f"{settings.database_port}/{settings.database_name}"
    )
else:
    DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, autoflush=False
)


# Base class for models
class Base(DeclarativeBase):
    pass


# Dependency
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
