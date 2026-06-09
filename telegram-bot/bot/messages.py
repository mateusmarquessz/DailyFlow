"""Pure message-building helpers — no Telegram client, no DB, easy to unit test."""

from datetime import date, time


def _plural(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


WELCOME_NEW_LINK = (
    "👋 Olá! Eu sou o bot do <b>DailyFlow</b>.\n\n"
    "Aqui está seu código de vinculação:\n\n"
    "<b>{code}</b>\n\n"
    "Cole esse código em <b>Configurações → Bot do Telegram</b> no DailyFlow para "
    "concluir a conexão. Ele expira em {ttl_minutes} minutos."
)

ALREADY_LINKED = (
    "✅ Esta conversa já está conectada à conta de <b>{name}</b> no DailyFlow.\n"
    "Use /ajuda para ver os comandos disponíveis."
)

HELP = (
    "<b>Comandos disponíveis</b>\n\n"
    "/start — gera (ou reenvia) seu código de vinculação\n"
    "/status — mostra se esta conversa está conectada a uma conta\n"
    "/ajuda — mostra esta mensagem\n\n"
    "Depois de conectado, você passa a receber lembretes automáticos de tarefas, "
    "hábitos e metas, além dos resumos matinal e noturno da sua produtividade."
)

STATUS_LINKED = "✅ Conectado à conta de <b>{name}</b>."
STATUS_NOT_LINKED = "❌ Esta conversa ainda não está conectada a nenhuma conta. Envie /start para gerar um código."


def build_welcome_with_code(code: str, ttl_minutes: int) -> str:
    return WELCOME_NEW_LINK.format(code=code, ttl_minutes=ttl_minutes)


def build_already_linked(name: str) -> str:
    return ALREADY_LINKED.format(name=name)


def build_help() -> str:
    return HELP


def build_status(name: str | None) -> str:
    if name is None:
        return STATUS_NOT_LINKED
    return STATUS_LINKED.format(name=name)


def build_link_confirmation() -> str:
    return (
        "🎉 Conta conectada com sucesso! A partir de agora você vai receber lembretes "
        "de tarefas, hábitos e metas por aqui — incluindo os resumos matinal e noturno."
    )


def build_morning_summary(*, name: str, pending_tasks: int, habits_today: int, goals_in_progress: int) -> str:
    lines = [f"🌞 Bom dia, {name}! Aqui está o resumo do seu dia:", ""]
    lines.append(f"📋 {pending_tasks} {_plural(pending_tasks, 'tarefa pendente', 'tarefas pendentes')} para hoje")
    lines.append(f"🔁 {habits_today} {_plural(habits_today, 'hábito', 'hábitos')} para manter em dia")
    lines.append(f"🎯 {goals_in_progress} {_plural(goals_in_progress, 'meta', 'metas')} em andamento")
    lines.append("")
    lines.append("Vamos com tudo hoje! 💪")
    return "\n".join(lines)


def build_evening_summary(*, name: str, tasks_completed: int, habits_completed: int) -> str:
    lines = [f"🌙 Boa noite, {name}! Veja o que você realizou hoje:", ""]
    lines.append(f"✅ {tasks_completed} {_plural(tasks_completed, 'tarefa concluída', 'tarefas concluídas')}")
    lines.append(f"🔥 {habits_completed} {_plural(habits_completed, 'hábito registrado', 'hábitos registrados')}")
    lines.append("")
    if tasks_completed + habits_completed > 0:
        lines.append("Mandou bem hoje — descanse, amanhã tem mais! 🌟")
    else:
        lines.append("Amanhã é um novo dia para colocar a rotina em dia. 🙂")
    return "\n".join(lines)


def build_task_due_soon(title: str, due_time: time | None) -> str:
    when = due_time.strftime("%H:%M") if due_time else "hoje"
    return f"⏰ A tarefa <b>{title}</b> vence às {when}. Não esqueça!"


def build_task_overdue(title: str, due_date: date) -> str:
    return f"⚠️ A tarefa <b>{title}</b> está atrasada (venceu em {due_date.strftime('%d/%m')}). Que tal resolver isso agora?"


def build_habit_reminder(name: str) -> str:
    return f"🔁 Você ainda não marcou o hábito <b>{name}</b> hoje. Bora manter a sequência? 🔥"


def build_goal_deadline(title: str, days_left: int) -> str:
    when = "amanhã" if days_left == 1 else f"em {days_left} dias"
    return f"🎯 Sua meta <b>{title}</b> vence {when}. Continue avançando! 🚀"
