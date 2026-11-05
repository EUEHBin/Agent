from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.exception import NotFoundException
from app.schema.product import ProductBrief, ProductCreate, ProductResponse, ProductUpdate
from app.service.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["商品"])


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    return await ProductService(db).create_product(data)


@router.get("")
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    keyword: str | None = Query(default=None, description="搜索关键词"),
    category_id: int | None = Query(default=None, description="分类ID筛选"),
    brand: str | None = Query(default=None, description="品牌筛选"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
):
    return await ProductService(db).list_products(
        keyword=keyword,
        category_id=category_id,
        brand=brand,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await ProductService(db).get_product(product_id)
    if result is None:
        raise NotFoundException(message="商品不存在")
    return result


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await ProductService(db).update_product(product_id, data)
    if result is None:
        raise NotFoundException(message="商品不存在")
    return result


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    deleted = await ProductService(db).delete_product(product_id)
    if not deleted:
        raise NotFoundException(message="商品不存在")
