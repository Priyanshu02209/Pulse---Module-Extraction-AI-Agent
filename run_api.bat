@echo off
REM Run the FastAPI server on Windows

python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

