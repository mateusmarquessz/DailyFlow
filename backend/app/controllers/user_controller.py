from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.user import ChangePasswordRequest, UserRead, UserUpdate
from app.services.exceptions import ValidationError
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_profile(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    service = UserService(db)
    updated = service.update_profile(
        current_user,
        name=payload.name,
        avatar_url=payload.avatar_url,
        theme_preference=payload.theme_preference,
    )
    return UserRead.model_validate(updated)


@router.post("/me/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    service = UserService(db)
    try:
        service.change_password(
            current_user, current_password=payload.current_password, new_password=payload.new_password
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return MessageResponse(message="Senha alterada com sucesso.")
