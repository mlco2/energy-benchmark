"""
Measure using a tasmota smart plug
https://tasmota.github.io/docs/
ex: https://www.mylocalbytes.com/en-eu/products/smart-plug-pm?variant=41600621543615
"""
import datetime
import requests
import os
from pydantic import BaseModel

from measures.common import BaseMeasure

class TasmotaEnergyResponse(BaseModel):
    TotalStartTime: datetime.datetime
    Total: float
    Yesterday: float
    Today: float
    Power: float
    ApparentPower: float
    ReactivePower: float
    Factor: float
    Voltage: float
    Current: float

class TasmotaStatusResponse(BaseModel):
    Time: datetime.datetime
    ENERGY: TasmotaEnergyResponse

class TasmotaResponse(BaseModel):
    StatusSNS: TasmotaStatusResponse


class Measure(BaseMeasure):
    name = "tasmota"

    def __init__(self):
        self.url = os.environ.get("TASMOTA_URL", "http://192.168.0.151")
    def get_measure(self):
        response = requests.get(f"{self.url}/cm", params={"cmnd":"STATUS+10"}).json()
        data = TasmotaResponse(**response)
        return {
            #"raw": response, 
            "data": {
                **data.StatusSNS.ENERGY.model_dump(),
                "timestamp": data.StatusSNS.Time.isoformat(),
                "TotalStartTime": data.StatusSNS.ENERGY.TotalStartTime.isoformat(),
            }
        }