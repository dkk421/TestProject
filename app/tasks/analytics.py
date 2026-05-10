from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.db.models.device import Device
from app.db.models.user import User
from app.services.analytics import get_device_analytics
from app.services.user_analytics import get_user_analytics


ANALYTICS_TASK_OPTIONS = {
    "autoretry_for": (Exception,),
    "retry_kwargs": {"max_retries": 3, "countdown": 5},
    "retry_backoff": True,
    "retry_jitter": True,
    "soft_time_limit": 30,
    "time_limit": 40,
}


@celery_app.task(**ANALYTICS_TASK_OPTIONS)
def analyze_device_task(
    device_id: int,
    start: str | None = None,
    end: str | None = None,
):
    from datetime import datetime

    db = SessionLocal()

    try:
        device = db.get(Device, device_id)

        if not device:
            return {"error": "Device not found"}

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


@celery_app.task(**ANALYTICS_TASK_OPTIONS)
def analyze_user_task(user_id: int):
    db = SessionLocal()

    try:
        user = db.get(User, user_id)

        if not user:
            return {"error": "User not found"}

        return get_user_analytics(db=db, user_id=user_id)
    finally:
        db.close()
