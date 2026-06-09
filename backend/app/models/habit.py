from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import HabitFrequency
from app.models.mixins import TimestampMixin


class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    frequency: Mapped[HabitFrequency] = mapped_column(
        default=HabitFrequency.daily, server_default=HabitFrequency.daily.value
    )
    target_days: Mapped[list[int] | None] = mapped_column(JSON)
    color: Mapped[str] = mapped_column(String(20), default="#6366F1", server_default="#6366F1")
    icon: Mapped[str] = mapped_column(String(50), default="check-circle", server_default="check-circle")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    user: Mapped["User"] = relationship(back_populates="habits")
    history: Mapped[list["HabitHistory"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan"
    )
