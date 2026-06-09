"""Pure "should we notify now?" predicates — no DB, no Telegram client, easy to unit test."""

from datetime import date, datetime, time

from bot.models import Habit


def is_task_due_soon(*, due_date: date | None, due_time: time | None, now: datetime, window_minutes: int) -> bool:
    if due_date != now.date() or due_time is None:
        return False
    due_at = datetime.combine(due_date, due_time)
    minutes_until_due = (due_at - now.replace(tzinfo=None)).total_seconds() / 60
    return 0 <= minutes_until_due <= window_minutes


def is_goal_deadline_approaching(*, deadline: date | None, today: date, days_threshold: int) -> bool:
    if deadline is None:
        return False
    days_left = (deadline - today).days
    return 0 <= days_left <= days_threshold


def is_habit_scheduled_on(habit: Habit, target_date: date) -> bool:
    if not habit.is_active:
        return False
    if habit.frequency != "weekly":
        return True
    if not habit.target_days:
        return False
    return target_date.weekday() in habit.target_days
