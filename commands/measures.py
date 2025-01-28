"""
"""

import datetime
import importlib
import itertools
import os
from typing import List, Optional

import click
from click_aliases import ClickAliasedGroup


def cli():
    pass


cli.__doc__ = __doc__
cli = click.group(cls=ClickAliasedGroup)(cli)
#######################################################################


@click.argument("name")
@cli.command()
def get(name: str):
    """
    ./cli.py measures get tasmota
    """

    # check if model is gguf file or hf model
    module = importlib.import_module(f"measures.{name}")
    data = module.Measure().get_measure()
    print(data)
