"""
Benchmarking methods and hooks

The hooks are meant to measure free RAM and energy usage 
before/after model load and during inference.
"""

import os
import time
from click_aliases import ClickAliasedGroup
import click
import datetime
import itertools
from typing import List, Optional
from commands import machine
from utils.logging import logger
import requests
import pynvml
import subprocess
import yaml
import platform
from codecarbon import EmissionsTracker
from codecarbon.output_methods.base_output import BaseOutput, EmissionsData

NUM_INFERENCES = 10


def cli():
    pass


cli.__doc__ = __doc__
cli = click.group(cls=ClickAliasedGroup)(cli)
#######################################################################

from measures import tasmota

measures = [tasmota.Measure()]


class MeasuresOutputHandler(BaseOutput):
    """
    use with:
    tracker = EmissionsTracker(output_handlers=[MeasuresOutputHandler()])
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MeasuresOutputHandler, cls).__new__(cls)
            cls._init = False
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self._init = True

        self.step = ""
        self.context = {
            "num_inferences": NUM_INFERENCES,
            "hostname": platform.node(),
        }

    def live_out(self, total: EmissionsData, delta: EmissionsData):
        # logger.info({"message": "OutputHandler.Live out"})
        # logger.info({"total": total.__dict__, "delta": delta.__dict__})
        data = {
            "message": "all measures",
            "context": self.context,
            "step": self.step,
            "codecarbon": {"total": total.__dict__, "delta": delta.__dict__},
        }
        for measure in measures:
            # logger.info(measure.get_measure())
            data[measure.name] = measure.get_measure()
        logger.info(data)

    # def out(self, total: EmissionsData, delta: EmissionsData):
    #     self.live_out(total, delta)


def get_tracker() -> EmissionsTracker:
    return EmissionsTracker(
        project_name="test-project",
        experiment_name="test-experiment",
        measure_power_secs=1,
        api_call_interval=1,
        save_to_api=False,
        save_to_file=True,
        # save_to_logger=True,
        on_csv_write="append",
        logger_preamble="-",
        output_handlers=[MeasuresOutputHandler()],
        tracking_mode="machine",
    )


def get_measures():
    data = {
        "message": "measures",
    }
    for measure in measures:
        data[measure.name] = measure.get_measure()
    return data


measure = measures[0]


def pre_bench_hook():
    logger.info("Starting benchmark")
    pynvml.nvmlInit()
    logger.info(machine._ram())
    logger.info(get_measures())
    MeasuresOutputHandler().step = "benchmark"


def post_model_load_hook():
    logger.info("Model loaded")
    logger.info(machine._ram())
    logger.info(get_measures())
    MeasuresOutputHandler().step = ""


def post_bench_hook():
    MeasuresOutputHandler().step = ""
    logger.info(machine._ram())
    logger.info(get_measures())
    logger.info("Benchmarking finished")


def baseline(tracker):
    MeasuresOutputHandler().step = "baseline"
    logger.info("Getting baseline")
    # tracker.start()
    time.sleep(10)
    # tracker.stop()
    logger.info("Baseline done")
    MeasuresOutputHandler().step = ""


@click.argument("model")
@cli.command()
def llamacpp(model: str):
    """
    runs llama.cpp on model ;
    """
    # check if model is gguf file or hf model
    modelfile = ""
    tracker = get_tracker()
    tracker.start()
    baseline(tracker)
    pre_bench_hook()
    os.system(f"llama-bench -m {modelfile}")
    post_bench_hook()
    baseline(tracker)
    tracker.stop()


@click.argument("model")
@cli.command()
def ollama(model: str):
    """
    using ollama server running on
    OLLAMA_HOST
    ./cli.py bench ollama dolphin-mistral
    """
    OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost:11434")
    tracker = get_tracker()
    tracker.start()
    baseline(tracker)

    # load model
    requests.post(
        f"http://{OLLAMA_HOST}/api/generate",
        json={"model": model, "prompt": "Why is the sky blue?"},
    )
    pre_bench_hook()
    # tracker.stop()

    # tracker.start()

    for i in range(NUM_INFERENCES):
        res = requests.post(
            f"http://{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": "Why is the sky blue?",
                "stream": False,
                "options": {
                    "num_predict": 10_000,  # set a limit
                },
            },
        )

    """
    https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
    "total_duration":1500404361,
    "load_duration":4771393,
    "prompt_eval_count":34,
    "prompt_eval_duration":2000000,
    "eval_count":232,
    "eval_duration":1492000000
    total_duration: time spent generating the response
    load_duration: time spent in nanoseconds loading the model
    prompt_eval_count: number of tokens in the prompt
    prompt_eval_duration: time spent in nanoseconds evaluating the prompt
    eval_count: number of tokens in the response
    eval_duration: time in nanoseconds spent generating the response
    context: an encoding of the conversation used in this response, this can be sent in the next request to keep a conversational memory
    """

    post_bench_hook()
    baseline(tracker)
    tracker.stop()


"""
ollama => jsonl unless stream false
res.content.decode().split("\n")[18]
"""


@click.argument("model_name")
@cli.command()
def torch(model_name: str):
    """
    ./cli.py bench torch HuggingFaceTB/SmolLM2-135M
    """
    _torch(model_name)


def _torch(model_name: str, num_inferences=NUM_INFERENCES):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import sys

    tracker = get_tracker()
    tracker.start()

    pre_bench_hook()
    baseline(tracker)

    def print_gpu_usage(gpu_id):
        print(
            f">>>> GPU memoy: {pynvml.nvmlDeviceGetMemoryInfo(gpu_device).used / 1024**3:.2f} GB on {gpu_mem} GB"
        )
        print(
            f">>>> GPU usage: Load {pynvml.nvmlDeviceGetUtilizationRates(gpu_device).gpu} %, memory {pynvml.nvmlDeviceGetUtilizationRates(gpu_device).memory} %"
        )

    # logging_logger
    # output_handlers
    # ...
    # output_handlers: Optional[List[BaseOutput]] = _sentinel,
    # logging_logger: Optional[LoggerOutput] = _sentinel,
    logger.info("Starting tracker [loading]")
    # tracker.start()

    if torch.cuda.is_available():
        print("Using GPU")
        device = "cuda:0"
        gpu_device = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(gpu_device).total / 1024**3
        print_gpu_usage(gpu_device)
    else:
        print("Using CPU")
        device = "cpu"
        gpu_device = None

    # Load pre-trained model and tokenizer
    MeasuresOutputHandler().step = "loading"
    model = AutoModelForCausalLM.from_pretrained(model_name, force_download=False)
    tokenizer = AutoTokenizer.from_pretrained(model_name, force_download=False)
    post_model_load_hook()

    # tracker.stop()
    logger.info("Tracker stopper")
    logger.info("Starting tracker [inference]")
    # tracker.start()
    MeasuresOutputHandler().step = "benchmark"
    # Generate text
    generated_text = []
    MeasuresOutputHandler().context["total_tokens"] = 0
    for _ in range(num_inferences):
        input_text = "CodeCarbon is a library that "
        input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)
        model.to(device)
        MeasuresOutputHandler().context["device"] = device
        output = model.generate(
            input_ids, max_length=100, num_return_sequences=3, do_sample=True
        )
        num_tokens = output.shape[1]
        MeasuresOutputHandler().context["total_tokens"] += num_tokens
        generated_text.append(tokenizer.batch_decode(output, skip_special_tokens=True))
        if gpu_device:
            print_gpu_usage(gpu_device)

    # Stop tracking
    # tracker.stop()
    logger.info("Tracker stopper")

    print("=" * 30)
    print(generated_text[-1])
    print("=" * 30)
    post_bench_hook()
    baseline(tracker)
    tracker.stop()
    # print(tracker.final_emissions_data)


@click.argument("runner")  # , descriptor="torch|docker|ollama")
@click.argument("config_file")  # , descriptor="YAML configuration file")
@cli.command()
def run(config_file: str, runner: str):
    """
    Run a series of benchmarks described in a yaml
    ex: bench.py config.yaml torch
    """
    import utils.logging

    utils.logging.logHandler
    import pathlib

    with open(pathlib.Path(config_file), "r") as file:
        bench_config = yaml.safe_load(file)

    bench_name = pathlib.Path(config_file).resolve().parts[-1].split(".")[0]
    MeasuresOutputHandler().context["bench"] = bench_name

    log_path = (pathlib.Path(".") / f"bench-{bench_name}.jsonl").resolve()
    # utils.logging.logHandler.baseFilename = log_path

    for idx, run in enumerate(bench_config["runs"]):
        log_path = (pathlib.Path(".") / f"bench-{bench_name}-{idx}.jsonl").resolve()
        # utils.logging.logHandler.baseFilename = log_path
        utils.logging.set_file(log_path)

        MeasuresOutputHandler().context["model"] = model = run["model"]
        MeasuresOutputHandler().context["num_inferences"] = count = run["count"]
        if runner == "torch":
            _torch(model_name=model, num_inferences=count)
        else:
            raise Exception("Only torch runner is supported")
