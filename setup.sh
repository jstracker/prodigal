#!/usr/bin/bash

python3 -m venv env
source env/bin/activate
python3 -m pip install -U pip
pip3 install --upgrade setuptools wheel
pip install pyproject.toml
python -m pip cache purge
# pip install -r requirements.txt
