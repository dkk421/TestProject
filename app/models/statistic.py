from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from datetime import datetime

from app.core.database import Base


class Statistic(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True)

    device_id = Column(Integer, ForeignKey("devices.id"))

    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

    timestamp = Column(DateTime, default=datetime.utcnow)