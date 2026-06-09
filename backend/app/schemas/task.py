from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RecurrenceType, TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None
    due_time: time | None = None
    recurrence: RecurrenceType = RecurrenceType.none


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    due_time: time | None = None
    recurrence: RecurrenceType | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    due_date: date | None
    due_time: time | None
    recurrence: RecurrenceType
    parent_task_id: int | None
    completed_at: datetime | None
    xp_awarded: int
    created_at: datetime
    updated_at: datetime
