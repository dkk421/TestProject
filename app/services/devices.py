from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.device import Device
from app.db.models.user import User
from app.schemas.device import DeviceCreate


def get_device_or_404(db: Session, device_id: int) -> Device:
    device = db.get(Device, device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return device


def create_device(db: Session, payload: DeviceCreate) -> Device:
    device = Device(identifier=payload.identifier)

    db.add(device)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Device already exists")

    db.refresh(device)

    return device


def assign_device_to_user(db: Session, device_id: int, user_id: int) -> Device:
    device = get_device_or_404(db, device_id)
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    device.owner_id = user_id
    db.commit()
    db.refresh(device)

    return device
