#!/bin/bash
docker run --rm -v "$(pwd)":/app -w /app python:3.12-slim \
  pip install --no-cache-dir -r requirements.txt
