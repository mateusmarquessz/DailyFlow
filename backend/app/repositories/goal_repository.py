from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import GoalStatus, GoalType
from app.models.goal import Goal


class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, goal_id: int, user_id: int) -> Goal | None:
        stmt = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(
        self,
        user_id: int,
        *,
        status: GoalStatus | None = None,
        type: GoalType | None = None,
    ) -> list[Goal]:
        stmt = select(Goal).where(Goal.user_id == user_id)
        if status is not None:
            stmt = stmt.where(Goal.status == status)
        if type is not None:
            stmt = stmt.where(Goal.type == type)
        stmt = stmt.order_by(Goal.deadline.is_(None), Goal.deadline, Goal.created_at)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, goal: Goal) -> Goal:
        self.db.add(goal)
        self.db.flush()
        self.db.refresh(goal)
        return goal

    def save(self, goal: Goal) -> Goal:
        self.db.add(goal)
        self.db.flush()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: Goal) -> None:
        self.db.delete(goal)
        self.db.flush()
