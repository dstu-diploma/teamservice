#!/bin/bash
echo "Loading team service..."
aerich upgrade
uvicorn app.main:app --host 0.0.0.0 --port 8000
