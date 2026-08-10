from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import settings
from app.models.base import Base


class Database:
    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.async_session_factory: async_sessionmaker[AsyncSession] | None = None

    def init(self) -> None:
        self.engine = create_async_engine(
            settings.database.url,
            echo=settings.database.echo,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
        )
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        if self.engine:
            await self.engine.dispose()

    async def create_tables(self) -> None:
        if not self.engine:
            raise RuntimeError("Database not initialized")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        if not self.engine:
            raise RuntimeError("Database not initialized")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


db = Database()


def create_worker_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create a NullPool-based session factory for Celery worker tasks.

    Must be called inside the event loop where sessions will be used.
    NullPool ensures connections are never shared across event loops
    or forked processes, preventing "Future attached to a different loop" errors.
    """
    engine = create_async_engine(
        settings.database.url,
        echo=False,
        poolclass=NullPool,
    )
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    ), engine


async def get_db() -> AsyncSession:
    if not db.async_session_factory:
        raise RuntimeError("Database not initialized")
    async with db.async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
