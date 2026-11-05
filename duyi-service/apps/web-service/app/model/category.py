# model/category.py
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.model.association import product_category
from app.model.base import Base, IDMixin

if TYPE_CHECKING:
    from app.model.product import Product


class Category(Base, IDMixin):

    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text, default="")

    products: Mapped[list["Product"]] = relationship(
        secondary=product_category, back_populates="categories"
    )
