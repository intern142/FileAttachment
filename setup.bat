@echo off
REM One-time Setup Script for Invoice Organizer
REM Run this once on each office desktop

echo ============================================
echo Invoice Organizer - Office Setup
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    echo Download from: https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install
    pause
    exit /b 1
)

echo Python found: 
python --version

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo Creating folder structure...
python -m src.organizer
if errorlevel 1 (
    echo ERROR: Failed to create folders
    pause
    exit /b 1
)

echo.
echo Verifying WhatsApp download folder...
python -c "from src.whatsapp_monitor import get_whatsapp_download_folder; print('Found:', get_whatsapp_download_folder())"

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To start monitoring, run: start_monitor.bat
echo To use GUI: python -m src.gui
echo To use CLI: python -m src.cli --help
echo.
pause