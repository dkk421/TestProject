from statistics import median

from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.statistic import Statistic


def calculate_metrics(values: list[float]):
    return {
        "minimum": min(values),
        "maximum": max(values),
        "count": len(values),
        "sum": sum(values),
        "median": median(values)
    }


def build_analytics(stats):
    x_values = [s.x for s in stats]
    y_values = [s.y for s in stats]
    z_values = [s.z for s in stats]

    return {
        "x": calculate_metrics(x_values),
        "y": calculate_metrics(y_values),
        "z": calculate_metrics(z_values)
    }


def get_user_analytics(db: Session, user_id: int):
    devices = (
        db.query(Device)
        .filter(Device.owner_id == user_id)
        .all()
    )

    if not devices:
        return {
            "message": "User has no devices"
        }

    result = {}

    all_stats = []

    for device in devices:
        stats = (
            db.query(Statistic)
            .filter(Statistic.device_id == device.id)
            .all()
        )

        if stats:
            result[device.identifier] = build_analytics(stats)
            all_stats.extend(stats)

    if all_stats:
        result["all_devices"] = build_analytics(all_stats)

    return result