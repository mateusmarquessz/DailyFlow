import enum


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"


class RecurrenceType(str, enum.Enum):
    none = "none"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class HabitFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"


class GoalType(str, enum.Enum):
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class GoalStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class NotificationType(str, enum.Enum):
    task_due_soon = "task_due_soon"
    task_overdue = "task_overdue"
    habit_reminder = "habit_reminder"
    morning_summary = "morning_summary"
    evening_summary = "evening_summary"
    goal_deadline = "goal_deadline"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class ThemePreference(str, enum.Enum):
    light = "light"
    dark = "dark"
