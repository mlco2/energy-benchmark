"""
Tools to manage model (download/convert)

"""

import datetime
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


@click.argument("model", type=str)
@cli.command()
def get_model(model):
    """
    download model from huggingface and convert it to gguf for llama.cpp
    ex: ./cli.py model get HuggingFaceTB/SmolLM2-135M
    """
    os.system("huggingface-cli download HuggingFaceTB/SmolLM2-135M")
