from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import init_db

from app.api.devices import router as devices_router
from app.api.stats import router as stats_router
from app.api.tasks import router as tasks_router
from app.api.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(devices_router)
app.include_router(stats_router)
app.include_router(tasks_router)
app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "ok"}
