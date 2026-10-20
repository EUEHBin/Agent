# schema/item.py
from pydantic import BaseModel, Field


class Item(BaseModel):
    item_id: int | None = Field(
        default=None,
        title="商品ID",
        description="商品的唯一标识符，在创建商品时可忽略，系统会自动生成。",
        ge=1,
        examples=[1, 2, 3],
    )

    name: str = Field(
        ...,
        title="商品名称",
        description="商品的显示名称，长度必须在2到10个字符之间。",
        min_length=2,
        max_length=10,
        examples=["无线鼠标"],
    )

    price: float = Field(
        default=0.0,
        title="商品价格",
        description="商品的销售价格，必须大于或等于0。",
        ge=0.0,
        examples=[19.99, 0.0, 100.5],
    )
