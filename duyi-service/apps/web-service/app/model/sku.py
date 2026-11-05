# model/sku.py
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base, IDMixin

if TYPE_CHECKING:
    from app.model.product import Product


class Sku(Base, IDMixin):

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE")
    )
    sku_code: Mapped[str] = mapped_column(String(50), unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    attrs: Mapped[dict] = mapped_column(JSONB)
    image_url: Mapped[str] = mapped_column(String)

    product: Mapped["Product"] = relationship(back_populates="skus")
