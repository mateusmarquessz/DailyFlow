from datetime import date, time

from bot import messages


def test_build_welcome_with_code_includes_code_and_ttl():
    text = messages.build_welcome_with_code("ABC123", 15)
    assert "ABC123" in text
    assert "15 minutos" in text


def test_build_already_linked_includes_name():
    assert "Maria" in messages.build_already_linked("Maria")


def test_build_status_not_linked():
    assert messages.build_status(None) == messages.STATUS_NOT_LINKED


def test_build_status_linked_includes_name():
    text = messages.build_status("João")
    assert "João" in text
    assert "Conectado" in text


def test_build_morning_summary_uses_singular_for_one():
    text = messages.build_morning_summary(name="Ana", pending_tasks=1, habits_today=1, goals_in_progress=1)
    assert "1 tarefa pendente" in text
    assert "1 hábito" in text
    assert "1 meta" in text
    assert "tarefas pendentes" not in text


def test_build_morning_summary_uses_plural_for_many():
    text = messages.build_morning_summary(name="Ana", pending_tasks=3, habits_today=2, goals_in_progress=0)
    assert "3 tarefas pendentes" in text
    assert "2 hábitos" in text
    assert "0 metas" in text


def test_build_evening_summary_celebrates_when_something_done():
    text = messages.build_evening_summary(name="Ana", tasks_completed=2, habits_completed=1)
    assert "Mandou bem hoje" in text


def test_build_evening_summary_encourages_when_nothing_done():
    text = messages.build_evening_summary(name="Ana", tasks_completed=0, habits_completed=0)
    assert "novo dia" in text


def test_build_task_due_soon_with_time():
    text = messages.build_task_due_soon("Relatório", time(14, 30))
    assert "Relatório" in text
    assert "14:30" in text


def test_build_task_due_soon_without_time():
    text = messages.build_task_due_soon("Relatório", None)
    assert "hoje" in text


def test_build_task_overdue_formats_date():
    text = messages.build_task_overdue("Relatório", date(2026, 6, 5))
    assert "Relatório" in text
    assert "05/06" in text


def test_build_habit_reminder_includes_name():
    assert "Meditar" in messages.build_habit_reminder("Meditar")


def test_build_goal_deadline_tomorrow():
    text = messages.build_goal_deadline("Aprender Go", 1)
    assert "amanhã" in text


def test_build_goal_deadline_in_days():
    text = messages.build_goal_deadline("Aprender Go", 5)
    assert "em 5 dias" in text
