from datetime import date

from sqlalchemy.orm import Session

from app.models.habit import Habit
from app.models.habit_history import HabitHistory
from app.repositories.habit_repository import HabitRepository
from app.services.exceptions import NotFoundError
from app.services.gamification_service import GamificationService
from app.services.habit_streaks import compute_streaks


class HabitService:
    def __init__(self, db: Session):
        self.db = db
        self.habits = HabitRepository(db)
        self.gamification = GamificationService(db)

    def list_habits(self, user_id: int, *, only_active: bool = False) -> list[dict]:
        habits = self.habits.list_for_user(user_id, only_active=only_active)
        return [self._with_stats(habit) for habit in habits]

    def get_habit(self, user_id: int, habit_id: int) -> dict:
        habit = self._require(user_id, habit_id)
        return self._with_stats(habit)

    def get_history(self, user_id: int, habit_id: int) -> list[HabitHistory]:
        habit = self._require(user_id, habit_id)
        return sorted(habit.history, key=lambda entry: entry.date)

    def create_habit(self, user_id: int, **fields) -> dict:
        habit = Habit(user_id=user_id, **fields)
        created = self.habits.create(habit)
        self.db.commit()
        return self._with_stats(created)

    def update_habit(self, user_id: int, habit_id: int, **fields) -> dict:
        habit = self._require(user_id, habit_id)
        for key, value in fields.items():
            if value is not None:
                setattr(habit, key, value)
        updated = self.habits.save(habit)
        self.db.commit()
        return self._with_stats(updated)

    def delete_habit(self, user_id: int, habit_id: int) -> None:
        habit = self._require(user_id, habit_id)
        self.habits.delete(habit)
        self.db.commit()

    def check_in(self, user_id: int, habit_id: int, *, day: date | None = None) -> dict:
        habit = self._require(user_id, habit_id)
        target_day = day or date.today()
        is_first_completion = self.habits.get_history_entry(habit.id, target_day) is None

        self.habits.upsert_history_entry(habit.id, target_day, completed=True, streak_snapshot=0)
        self.db.flush()
        self.db.refresh(habit)

        streak_at_target, _ = compute_streaks(habit, habit.history, target_day)
        entry = self.habits.get_history_entry(habit.id, target_day)
        entry.streak_snapshot = streak_at_target
        self.habits.save(entry)

        if is_first_completion:
            self.gamification.register_habit_checked_in(user_id)

        self.db.commit()

        self.db.refresh(habit)
        return self._with_stats(habit)

    def remove_check_in(self, user_id: int, habit_id: int, *, day: date | None = None) -> dict:
        habit = self._require(user_id, habit_id)
        target_day = day or date.today()

        entry = self.habits.get_history_entry(habit.id, target_day)
        if entry is not None:
            self.habits.delete_history_entry(entry)
            self.db.commit()
            self.db.refresh(habit)

        return self._with_stats(habit)

    def _require(self, user_id: int, habit_id: int) -> Habit:
        habit = self.habits.get_by_id(habit_id, user_id)
        if habit is None:
            raise NotFoundError("Hábito não encontrado.")
        return habit

    def _with_stats(self, habit: Habit) -> dict:
        today = date.today()
        current_streak, longest_streak = compute_streaks(habit, habit.history, today)
        completed_today = any(entry.date == today and entry.completed for entry in habit.history)
        return {
            "id": habit.id,
            "name": habit.name,
            "description": habit.description,
            "frequency": habit.frequency,
            "target_days": habit.target_days,
            "color": habit.color,
            "icon": habit.icon,
            "is_active": habit.is_active,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completed_today": completed_today,
            "created_at": habit.created_at,
            "updated_at": habit.updated_at,
        }
