from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class CategoryBrief(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class SkuBrief(BaseModel):
    id: int
    sku_code: str
    price: Decimal
    stock: int
    attrs: dict[str, Any]
    image_url: str

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200, description="商品名称")
    description: str = Field(default="", description="商品描述")
    brand: str | None = Field(default=None, max_length=100, description="品牌")
    category_ids: list[int] = Field(default_factory=list, description="关联分类ID列表")


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200, description="商品名称")
    description: str | None = Field(default=None, description="商品描述")
    brand: str | None = Field(default=None, max_length=100, description="品牌")
    category_ids: list[int] | None = Field(default=None, description="关联分类ID列表")


class ProductBrief(BaseModel):
    """商品简要信息，用于列表视图和嵌套引用"""
    id: int
    name: str
    description: str
    brand: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    brand: str | None
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryBrief] = []
    skus: list[SkuBrief] = []

    model_config = {"from_attributes": True}
