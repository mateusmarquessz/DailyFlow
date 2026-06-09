from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.achievement import Achievement
from app.models.user_xp import UserXP


class GamificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_xp(self, user_id: int) -> UserXP:
        stmt = select(UserXP).where(UserXP.user_id == user_id)
        xp = self.db.execute(stmt).scalar_one_or_none()
        if xp is None:
            xp = UserXP(user_id=user_id)
            self.db.add(xp)
            self.db.flush()
            self.db.refresh(xp)
        return xp

    def save_xp(self, xp: UserXP) -> UserXP:
        self.db.add(xp)
        self.db.flush()
        self.db.refresh(xp)
        return xp

    def list_achievements(self, user_id: int) -> list[Achievement]:
        stmt = select(Achievement).where(Achievement.user_id == user_id).order_by(Achievement.unlocked_at)
        return list(self.db.execute(stmt).scalars().all())

    def create_achievement(self, achievement: Achievement) -> Achievement:
        self.db.add(achievement)
        self.db.flush()
        self.db.refresh(achievement)
        return achievement
