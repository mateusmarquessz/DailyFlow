"""Scheduled jobs: gather data per linked account, decide what to send, send it.

Each run uses a fresh DB session and records a `Notification` row before/while
sending so that re-runs (or bot restarts) within the same day don't spam users —
the idempotency rule lives in `repository.has_notification_since`.
"""

import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from telegram import Bot
from telegram.constants import ParseMode

from bot import messages, repository, rules
from bot.config import settings
from bot.db import session_scope
from bot.models import TelegramAccount

logger = logging.getLogger("dailyflow.bot.jobs")

LOCAL_TZ = ZoneInfo(settings.timezone)


def _now_local() -> datetime:
    return datetime.now(LOCAL_TZ)


def _start_of_today_utc() -> datetime:
    today_local = _now_local().date()
    midnight_local = datetime.combine(today_local, datetime.min.time(), tzinfo=LOCAL_TZ)
    return midnight_local.astimezone(timezone.utc)


async def _send(bot: Bot, account: TelegramAccount, text: str) -> None:
    try:
        await bot.send_message(chat_id=account.chat_id, text=text, parse_mode=ParseMode.HTML)
    except Exception:
        logger.exception("Failed to send Telegram message to chat %s", account.chat_id)
        raise


async def send_morning_summaries(bot: Bot) -> None:
    today = _now_local().date()
    since = _start_of_today_utc()
    with session_scope() as db:
        for account in repository.get_linked_accounts(db):
            user = repository.get_user(db, account.user_id)
            if user is None or repository.has_notification_since(db, user_id=user.id, type_="morning_summary", since=since):
                continue

            pending_tasks = repository.list_pending_tasks_due_on(db, user.id, today)
            habits = [h for h in repository.list_active_habits(db, user.id) if rules.is_habit_scheduled_on(h, today)]
            goals = repository.list_goals_in_progress(db, user.id)

            text = messages.build_morning_summary(
                name=user.name.split(" ")[0],
                pending_tasks=len(pending_tasks),
                habits_today=len(habits),
                goals_in_progress=len(goals),
            )
            await _send(bot, account, text)
            repository.record_notification(
                db, user_id=user.id, type_="morning_summary", title="Resumo matinal", message=text
            )


async def send_evening_summaries(bot: Bot) -> None:
    today = _now_local().date()
    since = _start_of_today_utc()
    with session_scope() as db:
        for account in repository.get_linked_accounts(db):
            user = repository.get_user(db, account.user_id)
            if user is None or repository.has_notification_since(db, user_id=user.id, type_="evening_summary", since=since):
                continue

            completed_tasks = repository.list_tasks_completed_on(db, user.id, today)
            habits_completed = sum(
                1
                for habit in repository.list_active_habits(db, user.id)
                if (entry := repository.get_habit_entry_on(db, habit.id, today)) is not None and entry.completed
            )

            text = messages.build_evening_summary(
                name=user.name.split(" ")[0],
                tasks_completed=len(completed_tasks),
                habits_completed=habits_completed,
            )
            await _send(bot, account, text)
            repository.record_notification(
                db, user_id=user.id, type_="evening_summary", title="Resumo noturno", message=text
            )


async def send_task_due_soon_reminders(bot: Bot) -> None:
    now = _now_local()
    since = _start_of_today_utc()
    with session_scope() as db:
        for account in repository.get_linked_accounts(db):
            user = repository.get_user(db, account.user_id)
            if user is None:
                continue

            for task in repository.list_pending_tasks_due_on(db, user.id, now.date()):
                if not rules.is_task_due_soon(
                    due_date=task.due_date, due_time=task.due_time, now=now, window_minutes=settings.due_soon_window_minutes
                ):
                    continue
                if repository.has_notification_since(db, user_id=user.id, type_="task_due_soon", since=since, reference_id=task.id):
                    continue

                text = messages.build_task_due_soon(task.title, task.due_time)
                await _send(bot, account, text)
                repository.record_notification(
                    db,
                    user_id=user.id,
                    type_="task_due_soon",
                    title="Tarefa a vencer",
                    message=text,
                    reference_type="task",
                    reference_id=task.id,
                )


async def send_task_overdue_reminders(bot: Bot) -> None:
    today = _now_local().date()
    since = _start_of_today_utc()
    with session_scope() as db:
        for account in repository.get_linked_accounts(db):
            user = repository.get_user(db, account.user_id)
            if user is None:
                continue

            for task in repository.list_pending_tasks_overdue(db, user.id, today):
                if repository.has_notification_since(db, user_id=user.id, type_="task_overdue", since=since, reference_id=task.id):
                    continue

                text = messages.build_task_overdue(task.title, task.due_date)
                await _send(bot, account, text)
                repository.record_notification(
                    db,
                    user_id=user.id,
                    type_="task_overdue",
                    title="Tarefa atrasada",
                    message=text,
                    reference_type="task",
                    reference_id=task.id,
                )


async def send_habit_reminders(bot: Bot) -> None:
    today = _now_local().date()
    since = _start_of_today_utc()
    with session_scope() as db:
        for account in repository.get_linked_accounts(db):
            user = repository.get_user(db, account.user_id)
            if user is None:
                continue

            for habit in repository.list_active_habits(db, user.id):
                if not rules.is_habit_scheduled_on(habit, today):
                    continue
                entry = repository.get_habit_entry_on(db, habit.id, today)
                if entry is not None and entry.completed:
                    continue
                if repository.has_notification_since(db, user_id=user.id, type_="habit_reminder", since=since, reference_id=habit.id):
                    continue

                text = messages.build_habit_reminder(habit.name)
                await _send(bot, account, text)
                repository.record_notification(
                    db,
                    user_id=user.id,
                    type_="habit_reminder",
                    title="Lembrete de hábito",
                    message=text,
                    reference_type="habit",
                    reference_id=habit.id,
                )


async def send_goal_deadline_reminders(bot: Bot) -> None:
    today = _now_local().date()
    since = datetime.now(timezone.utc) - timedelta(days=3)
    with session_scope() as db:
        for account in repository.get_linked_accounts(db):
            user = repository.get_user(db, account.user_id)
            if user is None:
                continue

            for goal in repository.list_goals_in_progress(db, user.id):
                if not rules.is_goal_deadline_approaching(deadline=goal.deadline, today=today, days_threshold=3):
                    continue
                if repository.has_notification_since(db, user_id=user.id, type_="goal_deadline", since=since, reference_id=goal.id):
                    continue

                days_left = (goal.deadline - today).days
                text = messages.build_goal_deadline(goal.title, days_left)
                await _send(bot, account, text)
                repository.record_notification(
                    db,
                    user_id=user.id,
                    type_="goal_deadline",
                    title="Meta perto do prazo",
                    message=text,
                    reference_type="goal",
                    reference_id=goal.id,
                )
