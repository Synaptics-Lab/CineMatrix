#!/usr/bin/env bash
cd /opt/cinematrix
export PYTHONPATH=/opt/cinematrix
exec /opt/cinematrix/.venv/bin/uvicorn cinematrix.server:app --host 0.0.0.0 --port 8312
