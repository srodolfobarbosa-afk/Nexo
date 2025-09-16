#!/usr/bin/env bash
set -e
PYTHON=python3
if command -v python3.11 >/dev/null 2>&1; then PYTHON=python3.11; fi
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install -r requirements.txt
exec gunicorn src.main:app --bind 0.0.0.0:5000 --workers 1
