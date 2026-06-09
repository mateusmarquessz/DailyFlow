from datetime import date, timedelta

from app.models.enums import HabitFrequency
from app.models.habit import Habit
from app.models.habit_history import HabitHistory


def is_scheduled(habit: Habit, day: date) -> bool:
    if habit.frequency == HabitFrequency.daily:
        return True
    target_days = habit.target_days or []
    if not target_days:
        return True
    return day.weekday() in target_days


def compute_streaks(habit: Habit, history: list[HabitHistory], today: date) -> tuple[int, int]:
    completed_dates = {entry.date for entry in history if entry.completed}
    if not completed_dates:
        return 0, 0

    start = min(completed_dates)

    longest = 0
    running = 0
    cursor = start
    while cursor <= today:
        if is_scheduled(habit, cursor):
            if cursor in completed_dates:
                running += 1
                longest = max(longest, running)
            else:
                running = 0
        cursor += timedelta(days=1)

    cursor = today
    if is_scheduled(habit, cursor) and cursor not in completed_dates:
        cursor -= timedelta(days=1)

    current = 0
    floor = start - timedelta(days=1)
    while cursor >= floor:
        if is_scheduled(habit, cursor):
            if cursor in completed_dates:
                current += 1
            else:
                break
        cursor -= timedelta(days=1)

    return current, longest
