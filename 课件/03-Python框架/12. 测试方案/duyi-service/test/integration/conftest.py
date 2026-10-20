import asyncio
import os
from contextlib import contextmanager
from pathlib import Path

os.environ["DB_NAME"] = "duyi_integration_test_db"

from app.core.config import db_settings

import pytest
import psycopg2
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

DB_URL = f"postgresql+asyncpg://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.name}"


@contextmanager
def _create_cur():
    conn = psycopg2.connect(
        host=db_settings.host,
        port=db_settings.port,
        user=db_settings.user,
        password=db_settings.password,
        dbname="postgres",
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
        conn.close()


def pytest_sessionstart(session):
    with _create_cur() as cur:
        cur.execute(
            f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
            f"FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{db_settings.name}' "
            f"AND pid <> pg_backend_pid()"
        )
        cur.execute(f"DROP DATABASE IF EXISTS {db_settings.name}")
        cur.execute(f"CREATE DATABASE {db_settings.name}")

    from alembic import command
    from alembic.config import Config

    web_service_dir = Path(__file__).resolve().parent.parent.parent
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(web_service_dir / "migrations"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        f"postgresql://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.name}",
    )
    command.upgrade(alembic_cfg, "head")


def pytest_sessionfinish(session, exitstatus):
    with _create_cur() as cur:
        cur.execute(
            f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
            f"FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{db_settings.name}' "
            f"AND pid <> pg_backend_pid()"
        )
        cur.execute(f"DROP DATABASE IF EXISTS {db_settings.name}")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    from app.model.base import Base

    engine = create_async_engine(DB_URL, poolclass=NullPool)

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def async_client(db_session):
    from app.core.database import get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
