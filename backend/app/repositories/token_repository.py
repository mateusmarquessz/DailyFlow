from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime_utils import as_aware_utc
from app.models.tokens import PasswordResetToken, RefreshToken


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    # -- refresh tokens --------------------------------------------------
    def create_refresh_token(self, *, user_id: int, token_hash: str, expires_at: datetime) -> RefreshToken:
        record = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(record)
        self.db.flush()
        return record

    def get_active_refresh_token(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked.is_(False),
        )
        token = self.db.execute(stmt).scalar_one_or_none()
        if token and as_aware_utc(token.expires_at) < datetime.now(timezone.utc):
            return None
        return token

    def revoke_refresh_token(self, token: RefreshToken) -> None:
        token.revoked = True
        self.db.flush()

    # -- password reset tokens -------------------------------------------
    def create_password_reset_token(
        self, *, user_id: int, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        record = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(record)
        self.db.flush()
        return record

    def get_valid_reset_token(self, token_hash: str) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used.is_(False),
        )
        token = self.db.execute(stmt).scalar_one_or_none()
        if token and as_aware_utc(token.expires_at) < datetime.now(timezone.utc):
            return None
        return token

    def mark_reset_token_used(self, token: PasswordResetToken) -> None:
        token.used = True
        self.db.flush()
