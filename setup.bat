@echo off
REM Quick Setup Script for WhatsApp Invoice Organizer
REM Run this once to set up the project

echo ============================================
echo WhatsApp Invoice Organizer - Setup
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8+ not found!
    echo Download from: https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv
        pause
        exit /b 1
    )
)

REM Install dependencies
echo.
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo NEXT STEPS:
echo 1. Edit config.yaml with your paths:
echo    - whatsapp_download_folder: Path to WhatsApp Images folder
echo    - destination_root: Where to store organized invoices
echo    - contractor_mappings: Add your contractor names and short codes
echo.
echo 2. Find your WhatsApp Images folder:
echo    - Usually: C:\Users\%USERNAME%\AppData\Local\WhatsApp\Media\WhatsApp Images
echo    - Or: C:\Users\%USERNAME%\Pictures\WhatsApp Images
echo.
echo 3. Run the organizer:
echo    - Double-click run.bat
echo    - Or run: venv\Scripts\python.exe main.py
echo.
echo 4. Test with: venv\Scripts\python.exe test_organizer.py
echo.
pause