from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot

from bot import jobs
from bot.config import settings


def build_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.timezone)

    scheduler.add_job(
        jobs.send_morning_summaries,
        CronTrigger(hour=settings.morning_summary_hour, minute=0, timezone=settings.timezone),
        args=[bot],
        id="morning_summary",
    )
    scheduler.add_job(
        jobs.send_evening_summaries,
        CronTrigger(hour=settings.evening_summary_hour, minute=0, timezone=settings.timezone),
        args=[bot],
        id="evening_summary",
    )
    scheduler.add_job(
        jobs.send_habit_reminders,
        CronTrigger(hour=settings.habit_reminder_hour, minute=0, timezone=settings.timezone),
        args=[bot],
        id="habit_reminder",
    )
    scheduler.add_job(
        jobs.send_task_due_soon_reminders,
        IntervalTrigger(minutes=settings.poll_interval_minutes),
        args=[bot],
        id="task_due_soon",
    )
    scheduler.add_job(
        jobs.send_task_overdue_reminders,
        IntervalTrigger(minutes=settings.poll_interval_minutes),
        args=[bot],
        id="task_overdue",
    )
    scheduler.add_job(
        jobs.send_goal_deadline_reminders,
        IntervalTrigger(hours=12),
        args=[bot],
        id="goal_deadline",
    )

    return scheduler
