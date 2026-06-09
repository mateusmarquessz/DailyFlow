from datetime import date

from pydantic import BaseModel


class DayCompletion(BaseModel):
    date: date
    tasks_completed: int
    habits_completed: int


class DashboardStats(BaseModel):
    tasks_due_today: int
    tasks_completed_today: int
    habits_total: int
    habits_completed_today: int
    best_current_streak: int
    goals_in_progress: int
    weekly_completions: list[DayCompletion]
