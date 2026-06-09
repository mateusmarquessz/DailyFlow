from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.email import send_email
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.services.exceptions import ConflictError, UnauthorizedError, ValidationError


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.tokens = TokenRepository(db)

    def register(self, *, name: str, email: str, password: str) -> tuple[User, str, str]:
        if self.users.get_by_email(email):
            raise ConflictError("Já existe uma conta cadastrada com este e-mail.")

        user = self.users.create(email=email, name=name, hashed_password=security.hash_password(password))
        access_token, refresh_token = self._issue_token_pair(user)
        self.db.commit()
        self.db.refresh(user)
        return user, access_token, refresh_token

    def authenticate(self, *, email: str, password: str) -> tuple[User, str, str]:
        user = self.users.get_by_email(email)
        if not user or not security.verify_password(password, user.hashed_password):
            raise UnauthorizedError("E-mail ou senha inválidos.")
        if not user.is_active:
            raise UnauthorizedError("Esta conta está desativada.")

        access_token, refresh_token = self._issue_token_pair(user)
        self.db.commit()
        return user, access_token, refresh_token

    def refresh_access_token(self, refresh_token: str) -> str:
        payload = security.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Token de atualização inválido.")

        token_record = self.tokens.get_active_refresh_token(security.hash_token(refresh_token))
        if not token_record:
            raise UnauthorizedError("Token de atualização inválido ou expirado.")

        user = self.users.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("Usuário não encontrado ou inativo.")

        return security.create_access_token(user.id)

    def logout(self, refresh_token: str) -> None:
        token_record = self.tokens.get_active_refresh_token(security.hash_token(refresh_token))
        if token_record:
            self.tokens.revoke_refresh_token(token_record)
            self.db.commit()

    def request_password_reset(self, email: str) -> None:
        user = self.users.get_by_email(email)
        if not user:
            # Avoid leaking which e-mails are registered.
            return

        raw_token = security.generate_url_safe_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.password_reset_token_expire_minutes
        )
        self.tokens.create_password_reset_token(
            user_id=user.id, token_hash=security.hash_token(raw_token), expires_at=expires_at
        )
        self.db.commit()

        reset_link = f"{settings.frontend_url}/reset-password?token={raw_token}"
        send_email(
            to_email=user.email,
            subject="Redefinição de senha — DailyFlow",
            body=(
                f"Olá, {user.name}!\n\n"
                "Recebemos uma solicitação para redefinir sua senha no DailyFlow.\n"
                f"Clique no link abaixo para escolher uma nova senha (válido por "
                f"{settings.password_reset_token_expire_minutes} minutos):\n\n{reset_link}\n\n"
                "Se você não solicitou isso, pode ignorar este e-mail."
            ),
        )

    def reset_password(self, *, token: str, new_password: str) -> None:
        token_record = self.tokens.get_valid_reset_token(security.hash_token(token))
        if not token_record:
            raise ValidationError("Token de redefinição inválido ou expirado.")

        user = self.users.get_by_id(token_record.user_id)
        if not user:
            raise ValidationError("Token de redefinição inválido ou expirado.")

        user.hashed_password = security.hash_password(new_password)
        self.tokens.mark_reset_token_used(token_record)
        self.db.add(user)
        self.db.commit()

    def _issue_token_pair(self, user: User) -> tuple[str, str]:
        access_token = security.create_access_token(user.id)
        refresh_token = security.create_refresh_token(user.id)
        payload = security.decode_token(refresh_token)
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        self.tokens.create_refresh_token(
            user_id=user.id, token_hash=security.hash_token(refresh_token), expires_at=expires_at
        )
        return access_token, refresh_token
