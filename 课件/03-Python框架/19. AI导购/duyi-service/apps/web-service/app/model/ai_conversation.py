from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.model.base import Base, TimestampMixin


class AiConversation(Base, TimestampMixin):

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), primary_key=True)
    messages: Mapped[list[dict]] = mapped_column(JSONB, default=list)
