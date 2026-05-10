from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models.statistic import Statistic
from app.services.metrics import build_analytics


def get_device_analytics(
    db: Session,
    device_id: int,
    start: datetime | None = None,
    end: datetime | None = None
):
    query = (
        db.query(Statistic)
        .filter(Statistic.device_id == device_id)
    )

    if start:
        query = query.filter(Statistic.timestamp >= start)

    if end:
        query = query.filter(Statistic.timestamp <= end)

    stats = query.all()

    if not stats:
        return {
            "message": "No statistics"
        }

    return build_analytics(stats)
