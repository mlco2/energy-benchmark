"""
Get machine settings ; 
RAM (total, used...), CPU,...

"""
import os
from click_aliases import ClickAliasedGroup
import click
import datetime
import itertools
from typing import List, Optional
import pynvml
def cli():
    pass

cli.__doc__ = __doc__
cli = click.group(cls=ClickAliasedGroup)(cli)
#######################################################################
import psutil


def _ram():
    try:
        gpu_device = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(gpu_device)
    except:
        gpu_mem = None
        raise

    return {
        "gpu": {"free": gpu_mem.free, "total": gpu_mem.total, "used": gpu_mem.used},
        "gpu_GiB": {"free": gpu_mem.free / 1024**3, "total": gpu_mem.total / 1024**3, "used": gpu_mem.used / 1024**3},
        "ram": psutil.virtual_memory()
    }

@cli.command()
def ram():
    print(_ram())
