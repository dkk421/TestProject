from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User already exists")

    db.refresh(user)

    return user


@router.get("/{user_id}/analytics")
def user_analytics(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_user_analytics(db, user_id)
