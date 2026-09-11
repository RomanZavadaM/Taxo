@echo off
cd /d "%~dp0"
echo ==============================================
echo   Driver Worktime App - START
echo ==============================================
echo.
py -3.13 -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: package installation failed.
    pause
    exit /b 1
)
echo.
echo Starting application...
py -3.13 main.py
if errorlevel 1 (
    echo.
    echo ERROR: application stopped with an error.
    pause
)
