from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from ..config.config import settings

# Async SQLAlchemy URL for PostgreSQL
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.database_username}:"
    f"{settings.database_password}@{settings.database_host}:"
    f"{settings.database_port}/{settings.database_name}"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


# Base class for models
class Base(DeclarativeBase):
    pass


# Dependency
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
