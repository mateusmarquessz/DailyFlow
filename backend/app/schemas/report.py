from datetime import date
from enum import Enum

from pydantic import BaseModel


class ReportPeriod(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class ReportExportFormat(str, Enum):
    pdf = "pdf"
    excel = "excel"


class ReportDayEntry(BaseModel):
    date: date
    tasks_completed: int
    habits_completed: int


class ReportSummary(BaseModel):
    period: ReportPeriod
    start_date: date
    end_date: date
    tasks_completed: int
    tasks_due: int
    task_completion_rate: float
    habits_active: int
    habit_checkins: int
    habit_completion_rate: float
    goals_completed: int
    best_streak: int
    daily_breakdown: list[ReportDayEntry]
