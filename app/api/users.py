from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models.user import User
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
    user = User(username=username)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/{user_id}/analytics")
def user_analytics(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_user_analytics(db, user_id)