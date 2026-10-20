from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import get_engine

router = APIRouter(tags=["健康检查"])


@router.get("/health")
async def health() -> dict[str, str]:
    """存活探针（Liveness Probe）用。

    只检查 FastAPI 进程是否能响应请求，不依赖外部服务。
    K8s 每 30 秒调用一次，连续失败 3 次判定 Pod 死亡并重启。
    """
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    """就绪探针（Readiness Probe）用。

    检查数据库是否能正常连接。K8s 每 10 秒调用一次，
    连续失败 3 次将该 Pod 从 Service 转发列表摘除，不接收新流量。
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "not ready", "database": "disconnected"}
