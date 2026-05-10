from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.device import DeviceCreate, DeviceResponse
from app.services.devices import assign_device_to_user
from app.services.devices import create_device as create_device_service

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=DeviceResponse)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    return create_device_service(db, payload)


@router.post("/{device_id}/assign/{user_id}")
def assign_device(
    device_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    assign_device_to_user(db, device_id, user_id)

    return {"status": "assigned"}
