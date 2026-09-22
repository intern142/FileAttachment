@echo off
REM WhatsApp Invoice Organizer - Windows Launcher
REM Run this file to start the organizer

echo ============================================
echo WhatsApp Invoice Organizer
echo ============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo Activating environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check config exists
if not exist "config.yaml" (
    echo ERROR: config.yaml not found!
    echo Please configure config.yaml with your WhatsApp folder path
    pause
    exit /b 1
)

echo.
echo Starting WhatsApp Invoice Organizer...
echo Press Ctrl+C to stop
echo.

python main.py

echo.
echo Organizer stopped.
pause