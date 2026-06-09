from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ThemePreference
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    theme_preference: Mapped[ThemePreference] = mapped_column(
        default=ThemePreference.light, server_default=ThemePreference.light.value
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    habits: Mapped[list["Habit"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["Achievement"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    telegram_account: Mapped["TelegramAccount | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    xp: Mapped["UserXP | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
