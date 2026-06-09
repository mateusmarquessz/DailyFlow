from datetime import datetime

from pydantic import BaseModel


class AchievementCatalogEntry(BaseModel):
    code: str
    title: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: datetime | None


class GamificationProfileRead(BaseModel):
    xp_total: int
    level: int
    xp_for_next_level: int
    level_progress_percent: float
    current_streak: int
    longest_streak: int
    achievements: list[AchievementCatalogEntry]
