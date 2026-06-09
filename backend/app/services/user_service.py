from sqlalchemy.orm import Session

from app.core import security
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.exceptions import ValidationError


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def update_profile(self, user: User, *, name: str | None, avatar_url: str | None, theme_preference) -> User:
        updated = self.users.update(user, name=name, avatar_url=avatar_url, theme_preference=theme_preference)
        self.db.commit()
        return updated

    def change_password(self, user: User, *, current_password: str, new_password: str) -> None:
        if not security.verify_password(current_password, user.hashed_password):
            raise ValidationError("Senha atual incorreta.")

        user.hashed_password = security.hash_password(new_password)
        self.users.save(user)
        self.db.commit()
