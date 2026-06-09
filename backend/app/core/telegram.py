import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("dailyflow.telegram")


def send_telegram_message(chat_id: int, text: str) -> None:
    """Sends a message via the Telegram Bot API when a token is configured.

    Falls back to logging the message in development so the linking flow can be
    exercised without a real bot. Set TELEGRAM_BOT_TOKEN (created via @BotFather)
    in production to deliver real messages.
    """
    if not settings.telegram_bot_token:
        logger.info("Telegram bot token not configured — logging message instead.\nChat ID: %s\n%s", chat_id, text)
        return

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        httpx.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except httpx.HTTPError:
        logger.exception("Failed to send Telegram message to chat %s", chat_id)
