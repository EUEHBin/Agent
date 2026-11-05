from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.model.setting_group import SettingGroup


class Setting(Base, IDMixin, TimestampMixin):

    key: Mapped[str] = mapped_column(String(200))
    value: Mapped[str] = mapped_column(Text, default="")
    display_name: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")

    group_id: Mapped[int] = mapped_column(
        ForeignKey("settinggroup.id", ondelete="CASCADE")
    )

    group: Mapped["SettingGroup"] = relationship(back_populates="settings")

    __table_args__ = (
        UniqueConstraint("group_id", "key", name="uq_setting_group_key"),
    )
