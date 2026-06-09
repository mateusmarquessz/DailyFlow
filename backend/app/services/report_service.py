from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.datetime_utils import as_aware_utc
from app.models.enums import GoalStatus
from app.repositories.goal_repository import GoalRepository
from app.repositories.habit_repository import HabitRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.report import ReportPeriod
from app.services.habit_streaks import compute_streaks, is_scheduled

PERIOD_DAYS: dict[ReportPeriod, int] = {
    ReportPeriod.daily: 1,
    ReportPeriod.weekly: 7,
    ReportPeriod.monthly: 30,
}


def _local_date(value: datetime) -> date:
    return as_aware_utc(value).astimezone().date()


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)
        self.habits = HabitRepository(db)
        self.goals = GoalRepository(db)

    def build_summary(self, user_id: int, period: ReportPeriod, *, reference_date: date | None = None) -> dict:
        end_date = reference_date or date.today()
        span = PERIOD_DAYS[period]
        start_date = end_date - timedelta(days=span - 1)
        period_days = [start_date + timedelta(days=offset) for offset in range(span)]

        tasks = self.tasks.list_for_user(user_id)
        all_habits = self.habits.list_for_user(user_id)
        active_habits = [habit for habit in all_habits if habit.is_active]
        goals = self.goals.list_for_user(user_id)

        daily_breakdown = []
        tasks_completed = 0
        habit_checkins = 0
        for day in period_days:
            tasks_done = sum(
                1 for task in tasks if task.completed_at is not None and _local_date(task.completed_at) == day
            )
            habits_done = sum(
                1 for habit in all_habits if any(entry.date == day and entry.completed for entry in habit.history)
            )
            tasks_completed += tasks_done
            habit_checkins += habits_done
            daily_breakdown.append({"date": day, "tasks_completed": tasks_done, "habits_completed": habits_done})

        tasks_due = sum(1 for task in tasks if task.due_date is not None and start_date <= task.due_date <= end_date)
        task_completion_rate = (tasks_completed / tasks_due * 100) if tasks_due else 0.0

        expected_checkins = sum(1 for habit in active_habits for day in period_days if is_scheduled(habit, day))
        habit_completion_rate = (habit_checkins / expected_checkins * 100) if expected_checkins else 0.0

        goals_completed = sum(
            1
            for goal in goals
            if goal.status == GoalStatus.completed and start_date <= _local_date(goal.updated_at) <= end_date
        )

        best_streak = max(
            (compute_streaks(habit, habit.history, end_date)[0] for habit in active_habits),
            default=0,
        )

        return {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "tasks_completed": tasks_completed,
            "tasks_due": tasks_due,
            "task_completion_rate": round(task_completion_rate, 1),
            "habits_active": len(active_habits),
            "habit_checkins": habit_checkins,
            "habit_completion_rate": round(habit_completion_rate, 1),
            "goals_completed": goals_completed,
            "best_streak": best_streak,
            "daily_breakdown": daily_breakdown,
        }
