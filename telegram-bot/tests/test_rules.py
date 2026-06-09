from datetime import date, datetime, time

from bot.models import Habit
from bot import rules


def _habit(*, frequency="daily", target_days=None, is_active=True) -> Habit:
    return Habit(name="Hábito", frequency=frequency, target_days=target_days, is_active=is_active)


# --- is_task_due_soon -------------------------------------------------------

def test_task_due_soon_within_window_is_true():
    now = datetime(2026, 6, 7, 10, 0)
    assert rules.is_task_due_soon(due_date=date(2026, 6, 7), due_time=time(11, 30), now=now, window_minutes=120)


def test_task_due_soon_outside_window_is_false():
    now = datetime(2026, 6, 7, 10, 0)
    assert not rules.is_task_due_soon(due_date=date(2026, 6, 7), due_time=time(13, 0), now=now, window_minutes=120)


def test_task_due_soon_already_passed_is_false():
    now = datetime(2026, 6, 7, 10, 0)
    assert not rules.is_task_due_soon(due_date=date(2026, 6, 7), due_time=time(9, 0), now=now, window_minutes=120)


def test_task_due_soon_different_date_is_false():
    now = datetime(2026, 6, 7, 10, 0)
    assert not rules.is_task_due_soon(due_date=date(2026, 6, 8), due_time=time(11, 0), now=now, window_minutes=120)


def test_task_due_soon_without_time_is_false():
    now = datetime(2026, 6, 7, 10, 0)
    assert not rules.is_task_due_soon(due_date=date(2026, 6, 7), due_time=None, now=now, window_minutes=120)


# --- is_goal_deadline_approaching -------------------------------------------

def test_goal_deadline_within_threshold_is_true():
    today = date(2026, 6, 7)
    assert rules.is_goal_deadline_approaching(deadline=date(2026, 6, 9), today=today, days_threshold=3)


def test_goal_deadline_beyond_threshold_is_false():
    today = date(2026, 6, 7)
    assert not rules.is_goal_deadline_approaching(deadline=date(2026, 6, 20), today=today, days_threshold=3)


def test_goal_deadline_in_the_past_is_false():
    today = date(2026, 6, 7)
    assert not rules.is_goal_deadline_approaching(deadline=date(2026, 6, 1), today=today, days_threshold=3)


def test_goal_without_deadline_is_false():
    today = date(2026, 6, 7)
    assert not rules.is_goal_deadline_approaching(deadline=None, today=today, days_threshold=3)


# --- is_habit_scheduled_on ---------------------------------------------------

def test_inactive_habit_is_never_scheduled():
    assert not rules.is_habit_scheduled_on(_habit(is_active=False), date(2026, 6, 7))


def test_daily_habit_is_always_scheduled():
    assert rules.is_habit_scheduled_on(_habit(frequency="daily"), date(2026, 6, 7))
    assert rules.is_habit_scheduled_on(_habit(frequency="daily"), date(2026, 6, 8))


def test_weekly_habit_scheduled_on_target_day():
    sunday = date(2026, 6, 7)
    assert sunday.weekday() == 6
    assert rules.is_habit_scheduled_on(_habit(frequency="weekly", target_days=[6]), sunday)


def test_weekly_habit_not_scheduled_on_other_day():
    sunday = date(2026, 6, 7)
    assert not rules.is_habit_scheduled_on(_habit(frequency="weekly", target_days=[0, 1, 2]), sunday)


def test_weekly_habit_without_target_days_is_never_scheduled():
    assert not rules.is_habit_scheduled_on(_habit(frequency="weekly", target_days=None), date(2026, 6, 7))
