from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelegramStatusRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_linked: bool
    linked_at: datetime | None = None
    bot_username: str | None = None


class TelegramLinkRequest(BaseModel):
    code: str = Field(min_length=4, max_length=12)
