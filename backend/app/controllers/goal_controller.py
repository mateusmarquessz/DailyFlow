from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.enums import GoalStatus, GoalType
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.services.exceptions import NotFoundError
from app.services.goal_service import GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


def _service(db: Session = Depends(get_db)) -> GoalService:
    return GoalService(db)


@router.get("", response_model=list[GoalRead])
def list_goals(
    status_filter: GoalStatus | None = None,
    type_filter: GoalType | None = None,
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(_service),
) -> list[GoalRead]:
    goals = service.list_goals(current_user.id, status=status_filter, type=type_filter)
    return [GoalRead.model_validate(goal) for goal in goals]


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(_service),
) -> GoalRead:
    goal = service.create_goal(current_user.id, **payload.model_dump())
    return GoalRead.model_validate(goal)


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(_service),
) -> GoalRead:
    try:
        goal = service.get_goal(current_user.id, goal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return GoalRead.model_validate(goal)


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(_service),
) -> GoalRead:
    try:
        goal = service.update_goal(current_user.id, goal_id, **payload.model_dump())
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return GoalRead.model_validate(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(_service),
) -> None:
    try:
        service.delete_goal(current_user.id, goal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
