@echo off
REM Run WhatsApp Invoice Monitor with saved settings
REM Edit the variables below for your default settings

set PERSON=john_doe
set CONTRACTOR=ABC Construction
set PURCHASED_FROM=Home Depot

echo Starting WhatsApp Invoice Monitor...
echo Person: %PERSON%
echo Contractor: %CONTRACTOR%
echo Purchased From: %PURCHASED_FROM%
echo.
echo Press Ctrl+C to stop
echo.

python -m src.whatsapp_monitor --person "%PERSON%" --contractor "%CONTRACTOR%" --purchased-from "%PURCHASED_FROM%"

pause