import asyncio
import os
import time
import subprocess
from pathlib import Path
from contextlib import contextmanager

# ─── 必须在任何 app 导入之前设置环境变量 ───
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent.parent / ".env.test")
os.environ["DB_NAME"] = "duyi_e2e_test_db"
from app.core.config import DBSettings

db_settings = DBSettings()

import pytest
import psycopg2

TEST_SERVER_PORT = "18000"

_server_process: subprocess.Popen | None = None
_log_file = None


@contextmanager
def _create_cur():
    conn = psycopg2.connect(  # pyright: ignore[reportCallIssue, reportArgumentType]
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


def _start_server():
    global _server_process, _log_file
    tmp_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    _log_file = open(tmp_dir / "test_server.log", "w")
    _server_process = subprocess.Popen(
        [
            "uv",
            "run",
            "--package",
            "web-service",
            "fastapi",
            "dev",
            "apps/web-service/app/main.py",
            "--port",
            TEST_SERVER_PORT,
        ],
        stdout=_log_file,
        stderr=subprocess.STDOUT,
    )
    import httpx

    for _ in range(50):
        try:
            resp = httpx.get(f"http://localhost:{TEST_SERVER_PORT}/docs")
            if resp.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(0.1)
    else:
        raise RuntimeError("测试服务器启动超时")


def _stop_server():
    global _server_process, _log_file
    if _server_process is not None:
        _server_process.terminate()
        _server_process.wait(timeout=10)
        _server_process = None
    if _log_file is not None:
        _log_file.close()
        _log_file = None


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

    from alembic.config import Config
    from alembic import command

    WEB_SERVICE_DIR = Path(__file__).resolve().parent.parent.parent
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(WEB_SERVICE_DIR / "migrations"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        f"postgresql://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.name}",
    )
    command.upgrade(alembic_cfg, "head")

    _start_server()


def pytest_sessionfinish(session, exitstatus):
    _stop_server()

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
def base_url():
    return f"http://localhost:{TEST_SERVER_PORT}"


@pytest.fixture
async def async_client():
    from httpx import AsyncClient

    async with AsyncClient(base_url=f"http://localhost:{TEST_SERVER_PORT}") as client:
        yield client


_SKIP_CLEANUP_TABLES = {"settinggroup", "setting"}


@pytest.fixture(autouse=True)
async def cleanup_db(async_client):
    yield
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import NullPool
    from app.model.base import Base

    url = (
        f"postgresql+asyncpg://{db_settings.user}:{db_settings.password}"
        f"@{db_settings.host}:{db_settings.port}/{db_settings.name}"
    )
    engine = create_async_engine(url, poolclass=NullPool, echo=False)

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name in _SKIP_CLEANUP_TABLES:
                continue
            await conn.execute(
                text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE')
            )
    await engine.dispose()
