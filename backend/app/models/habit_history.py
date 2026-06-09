from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HabitHistory(Base):
    __tablename__ = "habit_history"
    __table_args__ = (UniqueConstraint("habit_id", "date", name="uq_habit_history_habit_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    streak_snapshot: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    habit: Mapped["Habit"] = relationship(back_populates="history")
