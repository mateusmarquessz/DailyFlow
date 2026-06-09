from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.datetime_utils import as_aware_utc
from app.models.enums import GoalStatus
from app.repositories.goal_repository import GoalRepository
from app.repositories.habit_repository import HabitRepository
from app.repositories.task_repository import TaskRepository
from app.services.habit_streaks import compute_streaks

WEEKLY_WINDOW_DAYS = 7


def _local_date(value: datetime) -> date:
    """Convert a `completed_at` timestamp to the server's local date.

    Without this conversion, `completed_at.date()` can be a UTC (or other
    session-offset) date and drift a day away from `date.today()` (server
    local) — e.g. during the hours each night where the local and UTC dates
    differ for negative-offset zones.
    """
    return as_aware_utc(value).astimezone().date()


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)
        self.habits = HabitRepository(db)
        self.goals = GoalRepository(db)

    def get_stats(self, user_id: int) -> dict:
        today = date.today()

        tasks = self.tasks.list_for_user(user_id)
        habits = self.habits.list_for_user(user_id, only_active=True)
        goals_in_progress = len(self.goals.list_for_user(user_id, status=GoalStatus.in_progress))

        tasks_due_today = sum(1 for task in tasks if task.due_date == today)
        tasks_completed_today = sum(
            1 for task in tasks if task.completed_at is not None and _local_date(task.completed_at) == today
        )
        habits_completed_today = sum(
            1 for habit in habits if any(entry.date == today and entry.completed for entry in habit.history)
        )
        best_current_streak = max(
            (compute_streaks(habit, habit.history, today)[0] for habit in habits),
            default=0,
        )

        weekly_completions = []
        for offset in range(WEEKLY_WINDOW_DAYS - 1, -1, -1):
            day = today - timedelta(days=offset)
            tasks_done = sum(
                1 for task in tasks if task.completed_at is not None and _local_date(task.completed_at) == day
            )
            habits_done = sum(
                1 for habit in habits if any(entry.date == day and entry.completed for entry in habit.history)
            )
            weekly_completions.append({"date": day, "tasks_completed": tasks_done, "habits_completed": habits_done})

        return {
            "tasks_due_today": tasks_due_today,
            "tasks_completed_today": tasks_completed_today,
            "habits_total": len(habits),
            "habits_completed_today": habits_completed_today,
            "best_current_streak": best_current_streak,
            "goals_in_progress": goals_in_progress,
            "weekly_completions": weekly_completions,
        }
