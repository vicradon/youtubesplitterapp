#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
exec pip install -r requirements.txt
