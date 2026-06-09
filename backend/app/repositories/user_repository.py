from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_xp import UserXP


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, *, email: str, name: str, hashed_password: str) -> User:
        user = User(email=email.lower(), name=name, hashed_password=hashed_password)
        self.db.add(user)
        self.db.flush()
        # Every user starts with an XP/level record so gamification has somewhere to accrue.
        self.db.add(UserXP(user_id=user.id))
        self.db.flush()
        self.db.refresh(user)
        return user

    def update(self, user: User, **fields) -> User:
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        self.db.flush()
        self.db.refresh(user)
        return user

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user
