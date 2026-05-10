from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional


from app.core.database import get_db
from app.db.models.device import Device
from app.db.models.statistic import Statistic
from app.schemas.statistic import StatisticCreate
from app.services.analytics import get_device_analytics

router = APIRouter(prefix="/devices", tags=["stats"])


@router.post("/{device_id}/stats")
def add_stat(
    device_id: int,
    payload: StatisticCreate,
    db: Session = Depends(get_db)
):
    device = db.get(Device, device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    stat = Statistic(
        device_id=device_id,
        x=payload.x,
        y=payload.y,
        z=payload.z
    )

    db.add(stat)
    db.commit()

    return {"status": "ok"}

@router.get("/{device_id}/analytics")
def analytics(
    device_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    device = db.get(Device, device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return get_device_analytics(
        db=db,
        device_id=device_id,
        start=start,
        end=end
    )
