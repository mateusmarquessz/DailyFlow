from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.telegram_account import TelegramAccount


class TelegramAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> TelegramAccount | None:
        stmt = select(TelegramAccount).where(TelegramAccount.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_link_code(self, code: str) -> TelegramAccount | None:
        stmt = select(TelegramAccount).where(TelegramAccount.link_code == code)
        return self.db.execute(stmt).scalar_one_or_none()

    def delete(self, account: TelegramAccount) -> None:
        self.db.delete(account)
        self.db.flush()

    def save(self, account: TelegramAccount) -> TelegramAccount:
        self.db.add(account)
        self.db.flush()
        self.db.refresh(account)
        return account
