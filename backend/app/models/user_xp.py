from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class UserXP(Base, TimestampMixin):
    __tablename__ = "user_xp"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )

    xp_total: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    level: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    current_streak: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    user: Mapped["User"] = relationship(back_populates="xp")

    @property
    def xp_for_next_level(self) -> int:
        return self.level * 100

    @property
    def level_progress_percent(self) -> float:
        previous_threshold = (self.level - 1) * 100
        span = self.xp_for_next_level - previous_threshold
        if span <= 0:
            return 0.0
        return min(100.0, round(((self.xp_total - previous_threshold) / span) * 100, 1))
