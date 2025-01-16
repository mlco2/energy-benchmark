#!/bin/bash
apt-get update
apt install -y nvtop powercap-utils powertop
pip install codecarbon pynvml poetry 
cd /build
poetry install
poetry install --extras "download measure llm"