#!/bin/bash
set -e

apt-get update
apt install -y nvtop powercap-utils powertop
pip install codecarbon pynvml poetry 
cd /build
poetry config virtualenvs.create false --local
poetry install --no-root --all-groups --all-extras
