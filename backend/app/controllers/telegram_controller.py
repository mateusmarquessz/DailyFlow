from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.telegram import TelegramLinkRequest, TelegramStatusRead
from app.services.exceptions import NotFoundError, ValidationError
from app.services.telegram_service import TelegramService

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.get("/status", response_model=TelegramStatusRead)
def get_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TelegramStatusRead:
    account = TelegramService(db).get_status(current_user)
    if account is None or not account.is_active:
        return TelegramStatusRead(is_linked=False, bot_username=settings.telegram_bot_username)
    return TelegramStatusRead(
        is_linked=True, linked_at=account.linked_at, bot_username=settings.telegram_bot_username
    )


@router.post("/link", response_model=TelegramStatusRead)
def link_account(
    payload: TelegramLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TelegramStatusRead:
    service = TelegramService(db)
    try:
        account = service.link_account(current_user, payload.code)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return TelegramStatusRead(
        is_linked=True, linked_at=account.linked_at, bot_username=settings.telegram_bot_username
    )


@router.delete("/link", response_model=MessageResponse)
def unlink_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    service = TelegramService(db)
    try:
        service.unlink_account(current_user)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return MessageResponse(message="Conta do Telegram desconectada.")
