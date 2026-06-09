import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot import handlers
from bot.config import settings
from bot.scheduler import build_scheduler

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("dailyflow.bot.main")


async def _on_startup(application: Application) -> None:
    scheduler = build_scheduler(application.bot)
    scheduler.start()
    application.bot_data["scheduler"] = scheduler
    logger.info("Scheduler started")


async def _on_shutdown(application: Application) -> None:
    scheduler = application.bot_data.get("scheduler")
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def build_application() -> Application:
    if not settings.telegram_bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN não configurado. Defina a variável de ambiente "
            "com o token gerado pelo @BotFather."
        )

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(_on_startup)
        .post_shutdown(_on_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", handlers.handle_start))
    application.add_handler(CommandHandler("status", handlers.handle_status))
    application.add_handler(CommandHandler(["ajuda", "help"], handlers.handle_help))
    application.add_handler(MessageHandler(filters.ALL, handlers.handle_unknown))

    return application


def _start_health_server() -> None:
    """Minimal HTTP server so Render/UptimeRobot can keep the process alive."""
    port = int(os.environ.get("PORT", 8080))

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    HTTPServer(("0.0.0.0", port), _Handler).serve_forever()


def main() -> None:
    threading.Thread(target=_start_health_server, daemon=True).start()
    application = build_application()
    logger.info("Starting DailyFlow Telegram bot (polling)")
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
