from sqlalchemy.orm import Session

from app.db.models.statistic import Statistic
from app.schemas.statistic import StatisticCreate
from app.services.devices import get_device_or_404


def create_statistic(
    db: Session,
    device_id: int,
    payload: StatisticCreate
) -> Statistic:
    get_device_or_404(db, device_id)

    stat = Statistic(
        device_id=device_id,
        x=payload.x,
        y=payload.y,
        z=payload.z
    )

    db.add(stat)
    db.commit()
    db.refresh(stat)

    return stat
