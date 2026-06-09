import logging
import secrets
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot import messages, repository
from bot.config import settings
from bot.db import session_scope

logger = logging.getLogger("dailyflow.bot.handlers")

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no ambiguous 0/O/1/I
CODE_LENGTH = 6


def generate_link_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


async def _reply(update: Update, text: str) -> None:
    if update.effective_message is not None:
        await update.effective_message.reply_html(text)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat is None:
        return

    with session_scope() as db:
        account = repository.get_account_by_chat_id(db, chat.id)
        if account is not None and account.is_active and account.user_id is not None:
            user = repository.get_user(db, account.user_id)
            await _reply(update, messages.build_already_linked(user.name.split(" ")[0] if user else "você"))
            return

        code = generate_link_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.link_code_ttl_minutes)
        repository.upsert_pending_link(db, chat_id=chat.id, code=code, expires_at=expires_at)

    await _reply(update, messages.build_welcome_with_code(code, settings.link_code_ttl_minutes))


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat is None:
        return

    with session_scope() as db:
        account = repository.get_account_by_chat_id(db, chat.id)
        name = None
        if account is not None and account.is_active and account.user_id is not None:
            user = repository.get_user(db, account.user_id)
            name = user.name.split(" ")[0] if user else None

    await _reply(update, messages.build_status(name))


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _reply(update, messages.build_help())


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message is not None:
        await update.effective_message.reply_html(
            "🤔 Não entendi essa mensagem. Envie /ajuda para ver os comandos disponíveis."
        )
