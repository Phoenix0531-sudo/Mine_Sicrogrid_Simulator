@echo off
title Microgrid Simulator

echo ================================================================
echo Smart Microgrid Planning Platform
echo ================================================================
echo.

echo Starting application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "app.py" (
    echo Error: app.py file not found
    echo Please run this script in the correct project directory
    pause
    exit /b 1
)

REM Start Streamlit application
echo Access URL: http://localhost:8501
echo Press Ctrl+C to stop the application
echo.
echo ================================================================
echo.

streamlit run app.py --server.headless false --browser.gatherUsageStats false

echo.
echo Application stopped
pause
