@echo off
echo ========================================================
echo Starting AI Support Ticket Analytics Platform...
echo ========================================================

echo.
echo [1/2] Starting FastAPI Backend on port 8000...
start "FastAPI Backend" cmd /k "uvicorn app.main:app --reload"

:: Wait 3 seconds to ensure backend starts before the frontend opens
timeout /t 3 /nobreak >nul

echo [2/2] Starting Streamlit UI on port 8501...
start "Streamlit Frontend" cmd /k "streamlit run ui/streamlit_app.py"

echo.
echo Both services are booting up in separate windows!
echo Close this window at any time (the services will remain running in their respective windows).
pause
