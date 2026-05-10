from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.analytics import get_device_analytics
from app.services.user_analytics import get_user_analytics


@celery_app.task
def analyze_device_task(
    device_id: int,
    start: str | None = None,
    end: str | None = None,
):
    from datetime import datetime

    db = SessionLocal()

    try:
        start_dt = datetime.fromisoformat(start) if start else None
        end_dt = datetime.fromisoformat(end) if end else None

        return get_device_analytics(
            db=db,
            device_id=device_id,
            start=start_dt,
            end=end_dt,
        )
    finally:
        db.close()


@celery_app.task
def analyze_user_task(user_id: int):
    db = SessionLocal()

    try:
        return get_user_analytics(db=db, user_id=user_id)
    finally:
        db.close()