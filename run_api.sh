#!/bin/bash
# Run the FastAPI server

python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

