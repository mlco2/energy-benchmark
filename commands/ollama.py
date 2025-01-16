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
from typing import List, Optional

def cli():
    pass

cli.__doc__ = __doc__
cli = click.group(cls=ClickAliasedGroup)(cli)
#######################################################################
import requests
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ollama_host: str
    # ollama_url: str 
    ollama_model: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    @property
    def ollama_url(self):
        return f"http://{self.ollama_host.replace('0.0.0.0', '127.0.0.1')}/api"

def _load_model():
    os.system("ollama pull " + Settings().ollama_model)
    return requests.post(f"{Settings().ollama_url}/generate", json={
        "model":Settings().ollama_model, 
        "prompt":"Write a paragraph about half-life 3",
        "keep_alive": "1h",
        })

def _test():
    res = requests.post(f"{Settings().ollama_url}/generate", json={
        "model":Settings().ollama_model, 
        "prompt":"Write a paragraph about half-life 3",
        "stream": False,
        "options": {
            "temperature": 0.9,
        },
        })
    return res.json()


@cli.command()
def load_model():
    _load_model()


@cli.command()
def test():
    print(Settings().ollama_url, Settings().ollama_model)
    result = _test()["response"]
    print(result)
