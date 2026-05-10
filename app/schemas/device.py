from pydantic import BaseModel


class DeviceCreate(BaseModel):
    identifier: str


class DeviceResponse(BaseModel):
    id: int
    identifier: str

    class Config:
        from_attributes = True