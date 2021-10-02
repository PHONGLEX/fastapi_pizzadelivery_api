#!/bin/bash
set -e

python init_db.py

uvicorn main:app --host=0.0.0.0 --reload


exec "$@"