from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.statistic import StatisticCreate
from app.services.analytics import get_device_analytics
from app.services.devices import get_device_or_404
from app.services.statistics import create_statistic

router = APIRouter(prefix="/devices", tags=["stats"])


@router.post("/{device_id}/stats")
def add_stat(
    device_id: int,
    payload: StatisticCreate,
    db: Session = Depends(get_db)
):
    create_statistic(db, device_id, payload)

    return {"status": "ok"}


@router.get("/{device_id}/analytics")
def analytics(
    device_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    get_device_or_404(db, device_id)

    return get_device_analytics(
        db=db,
        device_id=device_id,
        start=start,
        end=end
    )
