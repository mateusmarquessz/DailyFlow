import calendar
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.enums import RecurrenceType, TaskStatus
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.services.exceptions import NotFoundError
from app.services.gamification_rules import TASK_COMPLETION_XP
from app.services.gamification_service import GamificationService


def _next_due_date(current: date, recurrence: RecurrenceType) -> date | None:
    if recurrence == RecurrenceType.daily:
        return current + timedelta(days=1)
    if recurrence == RecurrenceType.weekly:
        return current + timedelta(days=7)
    if recurrence == RecurrenceType.monthly:
        month = current.month + 1
        year = current.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(current.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)
    return None


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)
        self.gamification = GamificationService(db)

    def list_tasks(
        self,
        user_id: int,
        *,
        status: TaskStatus | None = None,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Task]:
        return self.tasks.list_for_user(user_id, status=status, due_before=due_before, due_after=due_after)

    def get_task(self, user_id: int, task_id: int) -> Task:
        task = self.tasks.get_by_id(task_id, user_id)
        if task is None:
            raise NotFoundError("Tarefa não encontrada.")
        return task

    def create_task(self, user_id: int, **fields) -> Task:
        task = Task(user_id=user_id, **fields)
        created = self.tasks.create(task)
        self.db.commit()
        return created

    def update_task(self, user_id: int, task_id: int, **fields) -> Task:
        task = self.get_task(user_id, task_id)
        for key, value in fields.items():
            if value is not None:
                setattr(task, key, value)
        updated = self.tasks.save(task)
        self.db.commit()
        return updated

    def delete_task(self, user_id: int, task_id: int) -> None:
        task = self.get_task(user_id, task_id)
        self.tasks.delete(task)
        self.db.commit()

    def complete_task(self, user_id: int, task_id: int) -> Task:
        task = self.get_task(user_id, task_id)
        if task.status != TaskStatus.completed:
            task.status = TaskStatus.completed
            task.completed_at = datetime.now(timezone.utc)
            first_completion = task.xp_awarded == 0
            if first_completion:
                task.xp_awarded = TASK_COMPLETION_XP[task.priority]
            self.tasks.save(task)
            self._spawn_next_occurrence(task)
            if first_completion:
                self.gamification.register_task_completed(user_id, priority=task.priority)
            self.db.commit()
        return task

    def reopen_task(self, user_id: int, task_id: int) -> Task:
        task = self.get_task(user_id, task_id)
        if task.status != TaskStatus.pending:
            task.status = TaskStatus.pending
            task.completed_at = None
            self.tasks.save(task)
            self.db.commit()
        return task

    def _spawn_next_occurrence(self, task: Task) -> Task | None:
        if task.recurrence == RecurrenceType.none or task.due_date is None:
            return None

        next_due = _next_due_date(task.due_date, task.recurrence)
        if next_due is None:
            return None

        next_task = Task(
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=next_due,
            due_time=task.due_time,
            recurrence=task.recurrence,
            parent_task_id=task.parent_task_id or task.id,
        )
        return self.tasks.create(next_task)
