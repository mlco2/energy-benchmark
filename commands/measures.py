"""
"""
import os
from click_aliases import ClickAliasedGroup
import click
import datetime
import itertools
import importlib
from typing import List, Optional

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
    