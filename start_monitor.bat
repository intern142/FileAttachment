@echo off
REM WhatsApp Invoice Monitor - Auto Startup Script
REM Run this to start monitoring WhatsApp downloads automatically

echo ============================================
echo WhatsApp Invoice Organizer - Auto Monitor
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Check if dependencies installed
pip show watchdog >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Select mode:
echo 1. WhatsApp (Personal) - Auto detect folder
echo 2. WhatsApp Business - Auto detect folder
echo 3. Custom folder path
echo.

set /p choice="Enter choice (1/2/3): "

if "%choice%"=="1" (
    set FOLDER_ARG=
    set BUSINESS_ARG=
) else if "%choice%"=="2" (
    set FOLDER_ARG=
    set BUSINESS_ARG=--business
) else if "%choice%"=="3" (
    set /p FOLDER_ARG="Enter full path to WhatsApp downloads folder: "
    set FOLDER_ARG=--download-folder "%FOLDER_ARG%"
    set BUSINESS_ARG=
) else (
    echo Invalid choice
    pause
    exit /b 1
)

echo.
echo Enter accounts team member name:
set /p PERSON="Person: "

echo Enter contractor name:
set /p CONTRACTOR="Contractor: "

echo Enter purchased from (store/vendor):
set /p PURCHASED_FROM="Purchased From: "

echo.
echo Starting monitor...
echo Press Ctrl+C to stop
echo.

python -m src.whatsapp_monitor %FOLDER_ARG% %BUSINESS_ARG% --person "%PERSON%" --contractor "%CONTRACTOR%" --purchased-from "%PURCHASED_FROM%"

echo.
echo Monitor stopped.
pause