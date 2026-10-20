from fastapi import FastAPI

from app.core.config import common_settings, web_settings
from app.exception.base import BusinessException

app = FastAPI(
    title=web_settings.app_name,
    docs_url=None if common_settings.environment == "production" else "/docs",
    redoc_url=None if common_settings.environment == "production" else "/redoc",
    openapi_url=(
        None if common_settings.environment == "production" else "/openapi.json"
    ),
)

# 注册路由
from app.api.products import router as product_router
from app.api.categories import router as category_router
from app.api.skus import router as sku_router

app.include_router(product_router)
app.include_router(category_router)
app.include_router(sku_router)
