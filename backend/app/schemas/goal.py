from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import GoalStatus, GoalType


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    type: GoalType = GoalType.weekly
    target_value: float = Field(default=1.0, gt=0)
    deadline: date | None = None


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    type: GoalType | None = None
    status: GoalStatus | None = None
    target_value: float | None = Field(default=None, gt=0)
    current_value: float | None = Field(default=None, ge=0)
    deadline: date | None = None


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    type: GoalType
    status: GoalStatus
    target_value: float
    current_value: float
    progress_percent: float
    deadline: date | None
    created_at: datetime
    updated_at: datetime
