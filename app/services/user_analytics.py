from sqlalchemy.orm import Session

from app.db.models.device import Device
from app.db.models.statistic import Statistic
from app.services.metrics import build_analytics


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
