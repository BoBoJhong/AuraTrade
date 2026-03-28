"""
Database Configuration
追溯: REQ-005, REQ-087
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from apps.core.config import settings


@compiles(PG_UUID, "sqlite")
def compile_uuid_sqlite(_type, _compiler, **_kw):
    """Map PostgreSQL UUID columns to CHAR(36) when running on SQLite."""
    return "CHAR(36)"

# Create async engine with SQLite compatibility
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

# Add SQLite-specific settings if using SQLite
if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# Async session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for ORM models
Base = declarative_base()


async def get_db():
    """
    Dependency to get database session
    追溯: REQ-005
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    # Import models to ensure they are registered with Base
    import apps.models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database engine"""
    await engine.dispose()
