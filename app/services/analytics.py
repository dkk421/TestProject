from statistics import median
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.statistic import Statistic


def calculate_metrics(values: list[float]):
    return {
        "minimum": min(values),
        "maximum": max(values),
        "count": len(values),
        "sum": sum(values),
        "median": median(values)
    }


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

    x_values = [s.x for s in stats]
    y_values = [s.y for s in stats]
    z_values = [s.z for s in stats]

    return {
        "x": calculate_metrics(x_values),
        "y": calculate_metrics(y_values),
        "z": calculate_metrics(z_values)
    }