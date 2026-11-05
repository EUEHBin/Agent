from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class SkuCreate(BaseModel):
    sku_code: str = Field(min_length=1, max_length=50, description="SKU编码")
    price: Decimal = Field(ge=0, description="价格")
    stock: int = Field(default=0, ge=0, description="库存")
    attrs: dict[str, Any] = Field(description="规格属性")
    image_url: str = Field(min_length=1, description="图片URL")


class SkuUpdate(BaseModel):
    sku_code: str | None = Field(default=None, min_length=1, max_length=50, description="SKU编码")
    price: Decimal | None = Field(default=None, ge=0, description="价格")
    stock: int | None = Field(default=None, ge=0, description="库存")
    attrs: dict[str, Any] | None = Field(default=None, description="规格属性")
    image_url: str | None = Field(default=None, min_length=1, description="图片URL")


class SkuResponse(BaseModel):
    id: int
    product_id: int
    sku_code: str
    price: Decimal
    stock: int
    attrs: dict[str, Any]
    image_url: str

    model_config = {"from_attributes": True}
