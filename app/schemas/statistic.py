from pydantic import BaseModel


class StatisticCreate(BaseModel):
    x: float
    y: float
    z: float