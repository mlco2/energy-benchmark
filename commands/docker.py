"""
ollama helpers
neded env vars:
OLLAMA_MODEL=
OLLAMA_HOST=
"""

import datetime
import itertools
import json
import os
import pathlib
from typing import List, Optional

import click
from click_aliases import ClickAliasedGroup


def cli():
    pass


cli.__doc__ = __doc__
cli = click.group(cls=ClickAliasedGroup)(cli)
#######################################################################


@cli.command()
def build():
    os.system("docker build -f docker/Dockerfile -t powertest:latest .")


@cli.command()
def shell():
    hf_path = os.path.expandvars("${HOME}/.cache/huggingface")
    workdir = os.getcwd()
    command = f"""docker run --runtime=nvidia --ipc=host \\
              --gpus all --rm -it \\
              --cap-add CAP_PERFMON --cap-add CAP_SYS_ADMIN --cap-add PERFMON \\
              --privileged \\
              -v /sys/class/powercap:/sys/class/powercap:ro \\
              -v {hf_path}:/root/.cache/huggingface:ro \\
              -v /sys/devices/virtual/powercap:/sys/devices/virtual/powercap:ro \\
              -v {workdir}:/build \\
              --entrypoint=/bin/bash powertest:latest"""
    os.system(command)


@click.argument("args", required=False, nargs=-1)
@cli.command()
def run(args):
    args = " ".join(args)
    hf_path = os.path.expandvars("${HOME}/.cache/huggingface")
    workdir = os.getcwd()
    command = f"""docker run --runtime=nvidia --ipc=host \\
              --gpus all --rm -it \\
              --cap-add CAP_PERFMON --cap-add CAP_SYS_ADMIN --cap-add PERFMON \\
              --privileged \\
              -v /sys/class/powercap:/sys/class/powercap:ro \\
              -v /sys/devices/virtual/powercap:/sys/devices/virtual/powercap:ro \\
              -v {workdir}:/build \\
              --entrypoint= powertest:latest ./cli.py {args}"""
    os.system(command)
