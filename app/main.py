from fastapi import FastAPI

from app.core.database import Base, engine

from app.models.device import Device
from app.models.statistic import Statistic
from app.models.user import User

from app.api.devices import router as devices_router
from app.api.stats import router as stats_router
from app.api.users import router as users_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(devices_router)
app.include_router(stats_router)
app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "ok"}