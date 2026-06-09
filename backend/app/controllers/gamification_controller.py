from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.gamification import GamificationProfileRead
from app.services.gamification_service import GamificationService

router = APIRouter(prefix="/gamification", tags=["gamification"])


def _service(db: Session = Depends(get_db)) -> GamificationService:
    return GamificationService(db)


@router.get("/profile", response_model=GamificationProfileRead)
def get_profile(
    current_user: User = Depends(get_current_user),
    service: GamificationService = Depends(_service),
) -> GamificationProfileRead:
    return GamificationProfileRead.model_validate(service.get_profile(current_user.id))
