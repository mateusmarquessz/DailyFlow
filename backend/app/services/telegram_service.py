from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.datetime_utils import as_aware_utc
from app.core.telegram import send_telegram_message
from app.models.telegram_account import TelegramAccount
from app.models.user import User
from app.repositories.telegram_repository import TelegramAccountRepository
from app.services.exceptions import NotFoundError, ValidationError


class TelegramService:
    def __init__(self, db: Session):
        self.db = db
        self.accounts = TelegramAccountRepository(db)

    def get_status(self, user: User) -> TelegramAccount | None:
        return self.accounts.get_by_user_id(user.id)

    def link_account(self, user: User, code: str) -> TelegramAccount:
        pending = self.accounts.get_by_link_code(code.strip().upper())
        if pending is None or pending.user_id is not None:
            raise NotFoundError("Código de vinculação inválido ou já utilizado.")

        now = datetime.now(timezone.utc)
        expires_at = pending.link_code_expires_at
        if expires_at is not None and as_aware_utc(expires_at) < now:
            raise ValidationError("Este código expirou. Gere um novo enviando /start ao bot.")

        existing = self.accounts.get_by_user_id(user.id)
        if existing is not None:
            self.accounts.delete(existing)

        pending.user_id = user.id
        pending.is_active = True
        pending.linked_at = now
        pending.link_code = None
        pending.link_code_expires_at = None
        linked = self.accounts.save(pending)
        self.db.commit()

        send_telegram_message(
            linked.chat_id,
            "✅ Conta conectada com sucesso! A partir de agora você receberá lembretes "
            "de tarefas, hábitos e metas diretamente por aqui.",
        )
        return linked

    def unlink_account(self, user: User) -> None:
        existing = self.accounts.get_by_user_id(user.id)
        if existing is None:
            raise NotFoundError("Nenhuma conta do Telegram conectada.")
        self.accounts.delete(existing)
        self.db.commit()
