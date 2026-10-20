from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from app.core.middleware import register_middleware
from app.core.config import common_settings, web_settings
from app.core.database import get_session_factory
from app.exception.handler.docs import generate_error_docs
from app.exception.handler.handlers import exception_handler
from app.core.openapi import setup_openapi
from app.service.setting_service import SettingService


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with get_session_factory().begin() as session:
        await SettingService(session).initialize()
    yield


app = FastAPI(
    lifespan=lifespan,
    title=web_settings.app_name,
    description=generate_error_docs(),
    docs_url=None if common_settings.environment == "production" else "/docs",
    redoc_url=None if common_settings.environment == "production" else "/redoc",
    openapi_url=(
        None if common_settings.environment == "production" else "/openapi.json"
    ),
)

# 注册中间件
register_middleware(app)

# 设置openapi的格式
setup_openapi(app)

# 注册全局异常处理器（覆盖 Starlette/FastAPI 内置处理器 + 兜底未知异常）
app.add_exception_handler(RequestValidationError, exception_handler)
app.add_exception_handler(HTTPException, exception_handler)
app.add_exception_handler(Exception, exception_handler)


# 注册路由
from app.api.products import router as product_router
from app.api.categories import router as category_router
from app.api.skus import router as sku_router
from app.api.settings import router as settings_router
from app.api.upload import router as upload_router

app.include_router(product_router)
app.include_router(category_router)
app.include_router(sku_router)
app.include_router(settings_router)
app.include_router(upload_router)
