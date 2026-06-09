from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import HabitFrequency


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    frequency: HabitFrequency = HabitFrequency.daily
    target_days: list[int] | None = Field(default=None, description="Dias da semana (0=segunda .. 6=domingo)")
    color: str = Field(default="#6366F1", max_length=20)
    icon: str = Field(default="check-circle", max_length=50)


class HabitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    frequency: HabitFrequency | None = None
    target_days: list[int] | None = None
    color: str | None = Field(default=None, max_length=20)
    icon: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class HabitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    frequency: HabitFrequency
    target_days: list[int] | None
    color: str
    icon: str
    is_active: bool
    current_streak: int
    longest_streak: int
    completed_today: bool
    created_at: datetime
    updated_at: datetime


class HabitHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    completed: bool
    streak_snapshot: int


class HabitCheckInRequest(BaseModel):
    on_date: date | None = None
