from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from bot.models import Goal, Habit, HabitHistory, Notification, Task, TelegramAccount, User


def get_linked_accounts(db: Session) -> list[TelegramAccount]:
    stmt = select(TelegramAccount).where(TelegramAccount.is_active.is_(True), TelegramAccount.chat_id.isnot(None))
    return list(db.execute(stmt).scalars().all())


def get_account_by_chat_id(db: Session, chat_id: int) -> TelegramAccount | None:
    stmt = select(TelegramAccount).where(TelegramAccount.chat_id == chat_id)
    return db.execute(stmt).scalar_one_or_none()


def upsert_pending_link(db: Session, *, chat_id: int, code: str, expires_at: datetime) -> TelegramAccount:
    account = get_account_by_chat_id(db, chat_id)
    if account is None:
        account = TelegramAccount(chat_id=chat_id)
        db.add(account)

    account.link_code = code
    account.link_code_expires_at = expires_at
    db.flush()
    db.refresh(account)
    return account


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def list_pending_tasks_due_on(db: Session, user_id: int, target_date: date) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id, Task.status == "pending", Task.due_date == target_date)
    return list(db.execute(stmt).scalars().all())


def list_pending_tasks_overdue(db: Session, user_id: int, today: date) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id, Task.status == "pending", Task.due_date < today)
    return list(db.execute(stmt).scalars().all())


def list_tasks_completed_on(db: Session, user_id: int, target_date: date) -> list[Task]:
    stmt = select(Task).where(
        Task.user_id == user_id,
        Task.completed_at.isnot(None),
        Task.completed_at >= datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc),
        Task.completed_at < datetime.combine(target_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc),
    )
    return list(db.execute(stmt).scalars().all())


def list_active_habits(db: Session, user_id: int) -> list[Habit]:
    stmt = select(Habit).where(Habit.user_id == user_id, Habit.is_active.is_(True))
    return list(db.execute(stmt).scalars().all())


def get_habit_entry_on(db: Session, habit_id: int, target_date: date) -> HabitHistory | None:
    stmt = select(HabitHistory).where(HabitHistory.habit_id == habit_id, HabitHistory.date == target_date)
    return db.execute(stmt).scalar_one_or_none()


def list_goals_in_progress(db: Session, user_id: int) -> list[Goal]:
    stmt = select(Goal).where(Goal.user_id == user_id, Goal.status == "in_progress")
    return list(db.execute(stmt).scalars().all())


def has_notification_since(
    db: Session,
    *,
    user_id: int,
    type_: str,
    since: datetime,
    reference_id: int | None = None,
) -> bool:
    stmt = select(Notification.id).where(
        Notification.user_id == user_id,
        Notification.type == type_,
        Notification.created_at >= since,
    )
    if reference_id is not None:
        stmt = stmt.where(Notification.reference_id == reference_id)
    return db.execute(stmt).first() is not None


def record_notification(
    db: Session,
    *,
    user_id: int,
    type_: str,
    title: str,
    message: str,
    reference_type: str | None = None,
    reference_id: int | None = None,
) -> Notification:
    now = datetime.now(timezone.utc)
    notification = Notification(
        user_id=user_id,
        type=type_,
        title=title,
        message=message,
        status="sent",
        reference_type=reference_type,
        reference_id=reference_id,
        scheduled_for=now,
        sent_at=now,
        created_at=now,
    )
    db.add(notification)
    db.flush()
    return notification
