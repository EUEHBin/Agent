# 阶段1
FROM python:3.14-slim AS builder

WORKDIR /app

RUN pip install uv -i https://mirrors.aliyun.com/pypi/simple/
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY packages/duyi-utils ./packages/duyi-utils
COPY apps/web-service ./apps/web-service

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --all-packages

# 阶段2
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/apps/web-service/alembic.ini /app/apps/web-service/alembic.ini
COPY --from=builder /app/apps/web-service/migrations /app/apps/web-service/migrations

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

# 先执行迁移，再启动服务
CMD ["sh", "-c", "alembic -c apps/web-service/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
