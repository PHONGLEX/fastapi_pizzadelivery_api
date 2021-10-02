#!/bin/bash
set -e

python init_db.py

uvicorn main:app --reload


exec "$@"