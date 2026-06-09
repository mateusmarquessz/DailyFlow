from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import TaskStatus
from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: int, user_id: int) -> Task | None:
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(
        self,
        user_id: int,
        *,
        status: TaskStatus | None = None,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Task]:
        stmt = select(Task).where(Task.user_id == user_id)
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if due_before is not None:
            stmt = stmt.where(Task.due_date <= due_before)
        if due_after is not None:
            stmt = stmt.where(Task.due_date >= due_after)
        stmt = stmt.order_by(Task.due_date.is_(None), Task.due_date, Task.due_time.is_(None), Task.due_time)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

    def save(self, task: Task) -> Task:
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.flush()
