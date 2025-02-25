"""
A raspberry with a eGPU
Uses pyamdgpuinfo and vcgencmd to get power measures

rpi part was taken from https://github.com/librerpi/rpi-tools/blob/master/pi5_voltage.py

TODO: split cpu and ram from power measure
"""
import pyamdgpuinfo
import re
import datetime
import os
import requests
from pydantic import BaseModel
from measures.common import BaseMeasure
from subprocess import run
import re
import datetime

class PiradMeasure(BaseModel):
   vram: float
   gpu_power: float
   cpu_power: float
   power: float
   timestamp: str
   source: str



class Measure(BaseMeasure):
    name = "pirad"

    def __init__(self):
        try:
            self.gpu = pyamdgpuinfo.get_gpu(0)
        except:
           self.gpu = None


    def get_measure(self):
        # get raspberry power
        components = {}
        res = run(["vcgencmd","pmic_read_adc"], capture_output=True)
        lines = res.stdout.decode("utf-8").splitlines()
        for line in lines:
            res = re.search('([A-Z_0-9]+)_[VA] (current|volt)\(([0-9]+)\)=([0-9.]+)', line)
            component_name, measure_type, idx, value = res.groups()
            component = components[component_name] = components.get(component_name, {})
            component[measure_type] = float(value)
        pi_power = 0
        
        for component in components.values():
            try:
                component["power"] = component["volt"] * component["current"]
                pi_power += component["power"]
            except:
                ...

        # gpu measures
        gpu_power = self.gpu.query_power() if self.gpu else 0
        vram = self.gpu.query_vram_usage() if self.gpu else 0

        return PiradMeasure(
           vram=vram,
           gpu_power=gpu_power,
           cpu_power=pi_power,
           power=pi_power + gpu_power,
           source=self.name,
           timestamp=datetime.datetime.now().isoformat()
       ).model_dump()

    