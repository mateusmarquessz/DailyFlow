from sqlalchemy.orm import Session

from app.models.enums import GoalStatus, GoalType
from app.models.goal import Goal
from app.repositories.goal_repository import GoalRepository
from app.services.exceptions import NotFoundError
from app.services.gamification_service import GamificationService


class GoalService:
    def __init__(self, db: Session):
        self.db = db
        self.goals = GoalRepository(db)
        self.gamification = GamificationService(db)

    def list_goals(self, user_id: int, *, status: GoalStatus | None = None, type: GoalType | None = None) -> list[Goal]:
        return self.goals.list_for_user(user_id, status=status, type=type)

    def get_goal(self, user_id: int, goal_id: int) -> Goal:
        goal = self.goals.get_by_id(goal_id, user_id)
        if goal is None:
            raise NotFoundError("Meta não encontrada.")
        return goal

    def create_goal(self, user_id: int, **fields) -> Goal:
        goal = Goal(user_id=user_id, **fields)
        created = self.goals.create(goal)
        self.db.commit()
        return created

    def update_goal(self, user_id: int, goal_id: int, **fields) -> Goal:
        goal = self.get_goal(user_id, goal_id)
        was_completed = goal.status == GoalStatus.completed

        for key, value in fields.items():
            if value is not None:
                setattr(goal, key, value)

        if goal.status == GoalStatus.in_progress and goal.current_value >= goal.target_value:
            goal.status = GoalStatus.completed

        updated = self.goals.save(goal)
        if not was_completed and updated.status == GoalStatus.completed:
            self.gamification.register_goal_completed(user_id)
        self.db.commit()
        return updated

    def delete_goal(self, user_id: int, goal_id: int) -> None:
        goal = self.get_goal(user_id, goal_id)
        self.goals.delete(goal)
        self.db.commit()
