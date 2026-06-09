from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.habit import Habit
from app.models.habit_history import HabitHistory


class HabitRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, habit_id: int, user_id: int) -> Habit | None:
        stmt = (
            select(Habit)
            .where(Habit.id == habit_id, Habit.user_id == user_id)
            .options(selectinload(Habit.history))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(self, user_id: int, *, only_active: bool = False) -> list[Habit]:
        stmt = select(Habit).where(Habit.user_id == user_id).options(selectinload(Habit.history))
        if only_active:
            stmt = stmt.where(Habit.is_active.is_(True))
        stmt = stmt.order_by(Habit.created_at)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, habit: Habit) -> Habit:
        self.db.add(habit)
        self.db.flush()
        self.db.refresh(habit)
        return habit

    def save(self, habit: Habit) -> Habit:
        self.db.add(habit)
        self.db.flush()
        self.db.refresh(habit)
        return habit

    def delete(self, habit: Habit) -> None:
        self.db.delete(habit)
        self.db.flush()

    def get_history_entry(self, habit_id: int, day: date) -> HabitHistory | None:
        stmt = select(HabitHistory).where(HabitHistory.habit_id == habit_id, HabitHistory.date == day)
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert_history_entry(self, habit_id: int, day: date, *, completed: bool, streak_snapshot: int) -> HabitHistory:
        entry = self.get_history_entry(habit_id, day)
        if entry is None:
            entry = HabitHistory(habit_id=habit_id, date=day, completed=completed, streak_snapshot=streak_snapshot)
        else:
            entry.completed = completed
            entry.streak_snapshot = streak_snapshot
        self.db.add(entry)
        self.db.flush()
        self.db.refresh(entry)
        return entry

    def delete_history_entry(self, entry: HabitHistory) -> None:
        self.db.delete(entry)
        self.db.flush()
