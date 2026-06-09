from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.habit import (
    HabitCheckInRequest,
    HabitCreate,
    HabitHistoryRead,
    HabitRead,
    HabitUpdate,
)
from app.services.exceptions import NotFoundError
from app.services.habit_service import HabitService

router = APIRouter(prefix="/habits", tags=["habits"])


def _service(db: Session = Depends(get_db)) -> HabitService:
    return HabitService(db)


@router.get("", response_model=list[HabitRead])
def list_habits(
    only_active: bool = False,
    current_user: User = Depends(get_current_user),
    service: HabitService = Depends(_service),
) -> list[HabitRead]:
    return [HabitRead.model_validate(habit) for habit in service.list_habits(current_user.id, only_active=only_active)]


@router.post("", response_model=HabitRead, status_code=status.HTTP_201_CREATED)
def create_habit(
    payload: HabitCreate,
    current_user: User = Depends(get_current_user),
    service: HabitService = Depends(_service),
) -> HabitRead:
    return HabitRead.model_validate(service.create_habit(current_user.id, **payload.model_dump()))


@router.get("/{habit_id}", response_model=HabitRead)
def get_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    service: HabitService = Depends(_service),
) -> HabitRead:
    try:
        return HabitRead.model_validate(service.get_habit(current_user.id, habit_id))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{habit_id}", response_model=HabitRead)
def update_habit(
    habit_id: int,
    payload: HabitUpdate,
    current_user: User = Depends(get_current_user),
    service: HabitService = Depends(_service),
) -> HabitRead:
    try:
        return HabitRead.model_validate(service.update_habit(current_user.id, habit_id, **payload.model_dump()))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    service: HabitService = Depends(_service),
) -> None:
    try:
        service.delete_habit(current_user.id, habit_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{habit_id}/history", response_model=list[HabitHistoryRead])
def get_habit_history(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    service: HabitService = Depends(_service),
) -> list[HabitHistoryRead]:
    try:
        history = service.get_history(current_user.id, habit_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [HabitHistoryRead.model_validate(entry) for entry in history]


@router.post("/{habit_id}/check-in", response_model=HabitRead)
def check_in(
    habit_id: int,
    payload: HabitCheckInRequest,
    current_user: User = Depends(get_current_user),
    service: HabitService = Depends(_service),
) -> HabitRead:
    try:
        return HabitRead.model_validate(service.check_in(current_user.id, habit_id, day=payload.on_date))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{habit_id}/check-in", response_model=HabitRead)
def remove_check_in(
    habit_id: int,
    on_date: date | None = None,
    current_user: User = Depends(get_current_user),
    service: HabitService = Depends(_service),
) -> HabitRead:
    try:
        return HabitRead.model_validate(service.remove_check_in(current_user.id, habit_id, day=on_date))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
