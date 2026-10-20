from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schema.sku import SkuCreate, SkuResponse, SkuUpdate
from app.service.sku_service import SkuService

router = APIRouter(tags=["SKU"])


# ---- 挂载在商品下的 SKU 操作 ----


@router.post(
    "/api/products/{product_id}/skus", response_model=SkuResponse, status_code=201
)
async def create_sku(
    product_id: int,
    data: SkuCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await SkuService(db).create_sku(product_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return result


@router.get("/api/products/{product_id}/skus", response_model=list[SkuResponse])
async def list_skus(
    product_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    return await SkuService(db).list_skus(product_id)


# ---- 独立 SKU 操作 ----


@router.get("/api/skus/{sku_id}", response_model=SkuResponse)
async def get_sku(sku_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await SkuService(db).get_sku(sku_id)
    if result is None:
        raise HTTPException(status_code=404, detail="SKU不存在")
    return result


@router.put("/api/skus/{sku_id}", response_model=SkuResponse)
async def update_sku(
    sku_id: int,
    data: SkuUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await SkuService(db).update_sku(sku_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="SKU不存在")
    return result


@router.delete("/api/skus/{sku_id}", status_code=204)
async def delete_sku(sku_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    deleted = await SkuService(db).delete_sku(sku_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="SKU不存在")


@router.patch("/api/skus/{sku_id}/stock", response_model=SkuResponse)
async def update_stock(
    sku_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    stock: int = Query(..., ge=0, description="新库存数量"),
):
    result = await SkuService(db).update_stock(sku_id, stock)
    if result is None:
        raise HTTPException(status_code=404, detail="SKU不存在")
    return result
