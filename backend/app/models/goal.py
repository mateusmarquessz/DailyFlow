from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import GoalStatus, GoalType
from app.models.mixins import TimestampMixin


class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[GoalType] = mapped_column(default=GoalType.weekly, server_default=GoalType.weekly.value)
    status: Mapped[GoalStatus] = mapped_column(
        default=GoalStatus.in_progress, server_default=GoalStatus.in_progress.value, index=True
    )
    target_value: Mapped[float] = mapped_column(Float, default=1.0, server_default="1")
    current_value: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    deadline: Mapped[date | None] = mapped_column(Date, index=True)

    user: Mapped["User"] = relationship(back_populates="goals")

    @property
    def progress_percent(self) -> float:
        if self.target_value <= 0:
            return 0.0
        return min(100.0, round((self.current_value / self.target_value) * 100, 1))
