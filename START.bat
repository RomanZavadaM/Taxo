@echo off
setlocal
cd /d "%~dp0"

echo ==============================================
echo   Taxo 10.9-r10 - START
echo ==============================================
echo.

if not exist "requirements.txt" goto :package_incomplete
if not exist "taxo_app.py" goto :package_incomplete
if not exist "main.py" goto :package_incomplete
if not exist "src\taxo\application_context.py" goto :package_incomplete
if not exist "src\taxo\feature_layers.py" goto :package_incomplete
if not exist "src\taxo\workspace.py" goto :package_incomplete
if not exist "src\taxo\vehicle_documents.py" goto :package_incomplete
if not exist "src\taxo\v1099_schema_compatibility.py" goto :package_incomplete
if not exist "assets\Бланк підтвердження.docx" goto :package_incomplete
if not exist "assets\attestation_visual_template.pdf" goto :package_incomplete

set "PYTHONPATH=%CD%\src\taxo;%PYTHONPATH%"
py -3.13 -c "import sys" >nul 2>&1
if errorlevel 1 goto :python_missing

if /I "%TAXO_START_PREFLIGHT_ONLY%"=="1" (
    echo START preflight OK.
    exit /b 0
)

py -3.13 -m pip install -r "requirements.txt"
if errorlevel 1 goto :install_failed

echo.
echo Starting Taxo 10.9-r10...
py -3.13 "taxo_app.py"
if errorlevel 1 goto :app_failed
exit /b 0

:package_incomplete
echo ERROR: Taxo START package is incomplete in this folder.
echo.
echo Extract the ZIP completely before running START.bat.
echo Required layout: main.py, taxo_app.py, src\taxo\..., assets\..., requirements.txt.
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
