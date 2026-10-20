from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 从项目配置中读取数据库连接信息
from app.core.config import db_settings

# 导入模型（通过 __init__.py 触发所有模型注册到 Base.metadata）
from app.model.base import Base

# Alembic 配置对象，用于读取 alembic.ini
config = context.config

# 配置 Python 日志（读取 alembic.ini 中的 [loggers] 配置）
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 用项目配置覆盖 alembic.ini 中的 sqlalchemy.url
# 使用同步驱动 postgresql://（不需要 +asyncpg）
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.name}",
)

# 告诉 Alembic 你的模型元数据，用于自动生成迁移
target_metadata = Base.metadata

# 其他配置项可通过 config.get_main_option() 获取


def run_migrations_offline() -> None:
    """离线模式执行迁移（只生成 SQL 脚本，不连接数据库）"""
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
    """在线模式执行迁移（直接连接数据库执行）"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
