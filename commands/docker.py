"""
ollama helpers
neded env vars:
OLLAMA_MODEL=
OLLAMA_HOST=
"""
import os
from click_aliases import ClickAliasedGroup
import click
import json
import datetime
import itertools
import pathlib
from typing import List, Optional

def cli():
    pass

cli.__doc__ = __doc__
cli = click.group(cls=ClickAliasedGroup)(cli)
#######################################################################


@cli.command()
def build():
    os.system("docker build -t powertest:latest .")

@cli.command()
def run():
    hf_path = os.path.expandvars("${HOME}/.cache/huggingface")
    workdir = os.getcwd()
    os.system(f"""docker run --runtime=nvidia --ipc=host \\
              --gpus all --rm -it \\
              --cap-add CAP_PERFMON --cap-add CAP_SYS_ADMIN --cap-add PERFMON \\
              --privileged \\
              -v /sys/class/powercap:/sys/class/powercap:ro \\
              -v {hf_path}:/root/.cache/huggingface:ro \\
              -v /sys/devices/virtual/powercap:/sys/devices/virtual/powercap:ro \\
              -v {workdir}:/build \\
              --entrypoint=/bin/bash powertest:latest""")
