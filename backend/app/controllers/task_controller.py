from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.enums import TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.exceptions import NotFoundError
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


@router.get("", response_model=list[TaskRead])
def list_tasks(
    status_filter: TaskStatus | None = None,
    due_before: date | None = None,
    due_after: date | None = None,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(_service),
) -> list[TaskRead]:
    tasks = service.list_tasks(current_user.id, status=status_filter, due_before=due_before, due_after=due_after)
    return [TaskRead.model_validate(task) for task in tasks]


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(_service),
) -> TaskRead:
    task = service.create_task(current_user.id, **payload.model_dump())
    return TaskRead.model_validate(task)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(_service),
) -> TaskRead:
    try:
        task = service.get_task(current_user.id, task_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(_service),
) -> TaskRead:
    try:
        task = service.update_task(current_user.id, task_id, **payload.model_dump())
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(_service),
) -> None:
    try:
        service.delete_task(current_user.id, task_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(_service),
) -> TaskRead:
    try:
        task = service.complete_task(current_user.id, task_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskRead.model_validate(task)


@router.post("/{task_id}/reopen", response_model=TaskRead)
def reopen_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(_service),
) -> TaskRead:
    try:
        task = service.reopen_task(current_user.id, task_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskRead.model_validate(task)
