from collections.abc import Callable
from dataclasses import dataclass

from app.models.enums import TaskPriority

TASK_COMPLETION_XP: dict[TaskPriority, int] = {
    TaskPriority.low: 10,
    TaskPriority.medium: 20,
    TaskPriority.high: 30,
}
HABIT_CHECKIN_XP = 15
GOAL_COMPLETION_XP = 100


@dataclass(frozen=True)
class GamificationContext:
    tasks_completed: int
    habit_checkins: int
    current_streak: int
    longest_streak: int
    level: int
    goals_completed: int


@dataclass(frozen=True)
class AchievementRule:
    code: str
    title: str
    description: str
    icon: str
    is_unlocked: Callable[[GamificationContext], bool]


ACHIEVEMENT_RULES: tuple[AchievementRule, ...] = (
    AchievementRule(
        "first_task", "Primeiro Passo", "Conclua sua primeira tarefa.", "check-circle-2",
        lambda c: c.tasks_completed >= 1,
    ),
    AchievementRule(
        "tasks_10", "Em Ritmo", "Conclua 10 tarefas.", "list-checks",
        lambda c: c.tasks_completed >= 10,
    ),
    AchievementRule(
        "tasks_50", "Imparável", "Conclua 50 tarefas.", "rocket",
        lambda c: c.tasks_completed >= 50,
    ),
    AchievementRule(
        "tasks_100", "Lenda da Produtividade", "Conclua 100 tarefas.", "crown",
        lambda c: c.tasks_completed >= 100,
    ),
    AchievementRule(
        "first_habit", "Hábito Iniciado", "Faça o check-in de um hábito pela primeira vez.", "sparkles",
        lambda c: c.habit_checkins >= 1,
    ),
    AchievementRule(
        "streak_7", "Uma Semana Forte", "Alcance uma sequência de 7 dias em um hábito.", "flame",
        lambda c: c.longest_streak >= 7,
    ),
    AchievementRule(
        "streak_30", "Hábito Consolidado", "Alcance uma sequência de 30 dias em um hábito.", "flame",
        lambda c: c.longest_streak >= 30,
    ),
    AchievementRule(
        "streak_100", "Mestre da Constância", "Alcance uma sequência de 100 dias em um hábito.", "flame",
        lambda c: c.longest_streak >= 100,
    ),
    AchievementRule(
        "level_5", "Em Ascensão", "Alcance o nível 5.", "star",
        lambda c: c.level >= 5,
    ),
    AchievementRule(
        "level_10", "Veterano", "Alcance o nível 10.", "trophy",
        lambda c: c.level >= 10,
    ),
    AchievementRule(
        "first_goal", "Meta Cumprida", "Conclua sua primeira meta.", "target",
        lambda c: c.goals_completed >= 1,
    ),
)
