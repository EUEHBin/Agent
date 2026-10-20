from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.model.base import Base, IDMixin, TimestampMixin


class User(Base, IDMixin, TimestampMixin):
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
