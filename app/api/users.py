from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.users import create_user as create_user_service
from app.services.users import get_user_or_404
from app.services.user_analytics import get_user_analytics

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("")
def create_user(
    username: str,
    db: Session = Depends(get_db)
):
    return create_user_service(db, username)


@router.get("/{user_id}/analytics")
def user_analytics(
    user_id: int,
    db: Session = Depends(get_db)
):
    get_user_or_404(db, user_id)

    return get_user_analytics(db, user_id)
