from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.users import create_user as create_user_service
from app.services.users import get_user_or_404
from app.tasks.analytics import analyze_user_task

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("", response_model=UserResponse)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user_service(db, payload)


@router.post("/{user_id}/analytics/tasks")
def start_user_analytics_task(
    user_id: int,
    db: Session = Depends(get_db)
):
    get_user_or_404(db, user_id)

    task = analyze_user_task.delay(user_id)

    return {
        "task_id": task.id,
        "status": "started",
    }
