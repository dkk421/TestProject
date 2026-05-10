from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models.device import Device
from app.schemas.device import DeviceCreate, DeviceResponse

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=DeviceResponse)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    device = Device(identifier=payload.identifier)

    db.add(device)
    db.commit()
    db.refresh(device)

    return device

@router.post("/{device_id}/assign/{user_id}")
def assign_device(
    device_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    device = db.get(Device, device_id)

    if not device:
        return {"error": "Device not found"}

    device.owner_id = user_id

    db.commit()

    return {"status": "assigned"}