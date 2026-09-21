@echo off
setlocal
cd /d "%~dp0"

echo ==============================================
echo   Driver Worktime App - START
echo ==============================================
echo.

if not exist "requirements.txt" goto :package_incomplete
if not exist "taxo_app.py" goto :package_incomplete
if not exist "main.py" goto :package_incomplete
if not exist "workspace.py" goto :package_incomplete
if not exist "vehicle_documents.py" goto :package_incomplete

py -3.13 -c "import sys" >nul 2>&1
if errorlevel 1 goto :python_missing

if /I "%TAXO_START_PREFLIGHT_ONLY%"=="1" (
    echo START preflight OK.
    exit /b 0
)

py -3.13 -m pip install -r "requirements.txt"
if errorlevel 1 goto :install_failed

echo.
echo Starting application...
py -3.13 "taxo_app.py"
if errorlevel 1 goto :app_failed
exit /b 0

:package_incomplete
echo ERROR: Taxo START package is incomplete in this folder.
echo.
echo Extract the ZIP completely before running START.bat.
echo Use Windows "Extract all" or 7-Zip "Extract to...".
echo Then open the extracted Taxo folder and run START.bat there.
echo Required files: requirements.txt, taxo_app.py, main.py, workspace.py, vehicle_documents.py
pause
exit /b 2

:python_missing
echo ERROR: Python 3.13 with the py launcher was not found.
echo Install Python 3.13 x64 with the Python launcher and run START.bat again.
pause
exit /b 3

:install_failed
echo.
echo ERROR: Python package installation failed.
pause
exit /b 1

:app_failed
echo.
echo ERROR: Taxo stopped with an error.
pause
exit /b 1
