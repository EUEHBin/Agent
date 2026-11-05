from collections.abc import AsyncGenerator
import time

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import db_settings, log_settings

_engine: AsyncEngine | None = None
_query_start_times: dict[int, float] = {}


def _register_db_events(engine: AsyncEngine) -> None:
    from app.core.logger.db_log import DBLog

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def _before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        _query_start_times[id(context)] = time.perf_counter()

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def _after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        start = _query_start_times.pop(id(context), None)
        if start is None:
            return
        duration = (time.perf_counter() - start) * 1000
        if duration >= log_settings.slow_query_threshold:
            DBLog(
                message="慢查询",
                sql=statement,
                params=str(parameters),
                duration_ms=round(duration, 2),
            ).warning()
        else:
            DBLog(
                message="SQL执行",
                sql=statement,
                params=str(parameters),
                duration_ms=round(duration, 2),
            ).debug()


def get_engine() -> AsyncEngine:
    global _engine

    if _engine is None:
        url = f"postgresql+asyncpg://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.name}"
        _engine = create_async_engine(
            url, pool_size=10, max_overflow=20, pool_pre_ping=True, echo=False
        )
        _register_db_events(_engine)

    return _engine


_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory

    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,  # 明确指定使用异步 Session
            expire_on_commit=False,
            autoflush=True,
        )

    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession]:
    session = get_session_factory()()
    session.begin()
    try:
        yield session
    except:
        await session.rollback()
        raise
    else:
        await session.commit()
    finally:
        await session.close()

    # async with get_session_factory().begin() as session:
    #     yield session
