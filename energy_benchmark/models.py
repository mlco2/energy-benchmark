import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class Metadata(BaseModel):
    num_inferences: Optional[int]
    hostname: str


class DataPoint(BaseModel):
    power: float
    timestamp: datetime.datetime
    source: str
    raw: Optional[dict]

    model_config = ConfigDict(
        extra='allow',
    )    