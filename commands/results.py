"""
Tools to parse and analyze json files generated
"""
import os
from click_aliases import ClickAliasedGroup
import click
from typing import List, Optional
import numpy as np
import json
import datetime

def cli():
    pass

cli.__doc__ = __doc__
cli = click.group(cls=ClickAliasedGroup)(cli)
#######################################################################


def get_power(line):
    try:
        delta = line["codecarbon"]["delta"]
        return delta["cpu_power"] + delta["gpu_power"] + delta["ram_power"]
    except:
        return 0


def get_power_tasmota(line):
    try:
        return line["tasmota"]["data"]["Power"]        
    except:
        return 0


def _parse_results(filename: str):
    lines = []
    with open(filename) as f:
        for line in f.readlines():
            lines.append(json.loads(line))

    timeline_data = [
        (
            datetime.datetime.fromisoformat(l["timestamp"]), 
            l.get("step", ""),
            get_power(l),
            get_power_tasmota(l),
        )
        for l in lines
    ]

    baseline_data = [x for x in timeline_data if x[1] == "baseline"]
    measures_data = [x for x in timeline_data if x[1] == "benchmark"]
    loading_data = [x for x in timeline_data if x[1] == "loading"]
    other_data = [x for x in timeline_data if x[1] == ""]

    # get average baseline power
    baseline_power = sum([get_power(x) for x in baseline_data])/len(baseline_data)

    # inference duration
    inference_start = datetime.datetime.fromisoformat([l for l in lines if l["message"] ==  'Starting tracker [inference]'][0]["timestamp"])
    inference_stop = datetime.datetime.fromisoformat([l for l in lines if l["message"] ==  'Benchmarking finished'][0]["timestamp"])
    inference_duration_s = (inference_stop-inference_start).total_seconds()
    print(f"{inference_duration_s=}")

    # power use during inference
    inference_data = [get_power(l) for l in lines if l.get("step") == "benchmark"]
    inference_power = sum(inference_data)/len(inference_data)
    print(f"{inference_power=}")

    # energy use
    energy_use = ( inference_power - baseline_power ) * inference_duration_s
    print(f"{energy_use=} J")

    # per inference
    num_inferences =  [l for l in lines if l.get("step") == "baseline"][0]["context"]["num_inferences"]
    print(f"=> {energy_use/num_inferences=} J per inference")

    # per token
    num_tokens =  [l for l in lines if l.get("step") == "baseline"][-1]["context"]["total_tokens"]
    print(f"=> {energy_use/num_tokens=} J per token")

    # tokens per second
    print(f"=> {num_tokens/inference_duration_s=} tokens per second")

    return {
        "energy": energy_use,
        "energy_per_token": energy_use/num_tokens,
        "energy_per_inference": energy_use/num_inferences,
        "inference_time": inference_duration_s,
        "num_tokens": num_tokens,
        "num_inferences": num_inferences,
    }

@click.argument('filename', type=str)
@cli.command()
def parse_results(filename):
    """
    parse jsonl file
    """
    results = _parse_results(filename)
    print(json.dumps(results, indent=4))


