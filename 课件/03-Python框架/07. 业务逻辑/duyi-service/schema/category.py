from pydantic import BaseModel, Field

from app.schema.product import ProductBrief


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="分类名称")
    description: str = Field(default="", description="分类描述")


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50, description="分类名称")
    description: str | None = Field(default=None, description="分类描述")


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}


class CategoryDetailResponse(BaseModel):
    """分类详情，包含关联的商品列表"""
    id: int
    name: str
    description: str
    products: list[ProductBrief] = []

    model_config = {"from_attributes": True}
