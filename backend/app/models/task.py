from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RecurrenceType, TaskPriority, TaskStatus
from app.models.mixins import TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[TaskPriority] = mapped_column(
        default=TaskPriority.medium, server_default=TaskPriority.medium.value
    )
    status: Mapped[TaskStatus] = mapped_column(
        default=TaskStatus.pending, server_default=TaskStatus.pending.value, index=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, index=True)
    due_time: Mapped[time | None] = mapped_column(Time)
    recurrence: Mapped[RecurrenceType] = mapped_column(
        default=RecurrenceType.none, server_default=RecurrenceType.none.value
    )
    parent_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"), index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    user: Mapped["User"] = relationship(back_populates="tasks")
