@echo off
REM Run Streamlit app
echo Starting Pulse Module Extraction Agent...
echo.
echo The app will open in your browser at http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run src/app.py

