from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.achievement import Achievement
from app.models.enums import GoalStatus, TaskPriority, TaskStatus
from app.models.goal import Goal
from app.models.habit import Habit
from app.models.habit_history import HabitHistory
from app.models.task import Task
from app.models.user_xp import UserXP
from app.repositories.gamification_repository import GamificationRepository
from app.repositories.habit_repository import HabitRepository
from app.services.gamification_rules import (
    ACHIEVEMENT_RULES,
    GOAL_COMPLETION_XP,
    HABIT_CHECKIN_XP,
    TASK_COMPLETION_XP,
    GamificationContext,
)
from app.services.habit_streaks import compute_streaks


@dataclass(frozen=True)
class GamificationEvent:
    xp_awarded: int
    xp_total: int
    level: int
    leveled_up: bool
    unlocked_achievements: list[Achievement]


class GamificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = GamificationRepository(db)

    def get_profile(self, user_id: int) -> dict:
        xp = self.repo.get_or_create_xp(user_id)
        unlocked_by_code = {achievement.code: achievement for achievement in self.repo.list_achievements(user_id)}
        catalog = [
            {
                "code": rule.code,
                "title": rule.title,
                "description": rule.description,
                "icon": rule.icon,
                "unlocked": rule.code in unlocked_by_code,
                "unlocked_at": unlocked_by_code[rule.code].unlocked_at if rule.code in unlocked_by_code else None,
            }
            for rule in ACHIEVEMENT_RULES
        ]
        return {
            "xp_total": xp.xp_total,
            "level": xp.level,
            "xp_for_next_level": xp.xp_for_next_level,
            "level_progress_percent": xp.level_progress_percent,
            "current_streak": xp.current_streak,
            "longest_streak": xp.longest_streak,
            "achievements": catalog,
        }

    def register_task_completed(self, user_id: int, *, priority: TaskPriority) -> GamificationEvent:
        return self._apply_event(user_id, TASK_COMPLETION_XP[priority])

    def register_habit_checked_in(self, user_id: int) -> GamificationEvent:
        xp = self.repo.get_or_create_xp(user_id)
        current, longest = self._streak_stats(user_id)
        xp.current_streak = current
        xp.longest_streak = max(xp.longest_streak, longest)
        self.repo.save_xp(xp)
        return self._apply_event(user_id, HABIT_CHECKIN_XP, xp=xp)

    def register_goal_completed(self, user_id: int) -> GamificationEvent:
        return self._apply_event(user_id, GOAL_COMPLETION_XP)

    def _apply_event(self, user_id: int, amount: int, *, xp: UserXP | None = None) -> GamificationEvent:
        xp = xp if xp is not None else self.repo.get_or_create_xp(user_id)
        xp.xp_total += amount
        level_before = xp.level
        while xp.xp_total >= xp.level * 100:
            xp.level += 1
        self.repo.save_xp(xp)

        context = self._build_context(user_id, xp)
        unlocked = self._unlock_new_achievements(user_id, context)

        return GamificationEvent(
            xp_awarded=amount,
            xp_total=xp.xp_total,
            level=xp.level,
            leveled_up=xp.level > level_before,
            unlocked_achievements=unlocked,
        )

    def _unlock_new_achievements(self, user_id: int, context: GamificationContext) -> list[Achievement]:
        already_unlocked = {achievement.code for achievement in self.repo.list_achievements(user_id)}
        unlocked: list[Achievement] = []
        for rule in ACHIEVEMENT_RULES:
            if rule.code in already_unlocked or not rule.is_unlocked(context):
                continue
            achievement = Achievement(
                user_id=user_id,
                code=rule.code,
                title=rule.title,
                description=rule.description,
                icon=rule.icon,
            )
            unlocked.append(self.repo.create_achievement(achievement))
        return unlocked

    def _build_context(self, user_id: int, xp: UserXP) -> GamificationContext:
        return GamificationContext(
            tasks_completed=self._count(Task, Task.user_id == user_id, Task.status == TaskStatus.completed),
            habit_checkins=self._count_habit_checkins(user_id),
            current_streak=xp.current_streak,
            longest_streak=xp.longest_streak,
            level=xp.level,
            goals_completed=self._count(Goal, Goal.user_id == user_id, Goal.status == GoalStatus.completed),
        )

    def _count(self, model: type, *clauses) -> int:
        stmt = select(func.count()).select_from(model).where(*clauses)
        return self.db.execute(stmt).scalar_one()

    def _count_habit_checkins(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(HabitHistory)
            .join(Habit, HabitHistory.habit_id == Habit.id)
            .where(Habit.user_id == user_id, HabitHistory.completed.is_(True))
        )
        return self.db.execute(stmt).scalar_one()

    def _streak_stats(self, user_id: int) -> tuple[int, int]:
        habits = HabitRepository(self.db).list_for_user(user_id)
        today = date.today()
        best_current = best_longest = 0
        for habit in habits:
            current, longest = compute_streaks(habit, habit.history, today)
            best_current = max(best_current, current)
            best_longest = max(best_longest, longest)
        return best_current, best_longest
