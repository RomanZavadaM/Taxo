@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo ==============================================
echo   Driver Worktime App - START
echo ==============================================
echo.

if not exist "requirements.txt" goto :package_incomplete
if not exist "taxo_app.py" goto :package_incomplete

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python launcher "py" not found.
    echo Install Python 3.13 x64 and enable the Python launcher, then run START.bat again.
    pause
    exit /b 3
)

py -3.13 -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: package installation failed.
    pause
    exit /b 1
)

echo.
echo Starting application...
py -3.13 taxo_app.py
if errorlevel 1 (
    echo.
    echo ERROR: application stopped with an error.
    pause
    exit /b 1
)
exit /b 0

:package_incomplete
echo ERROR: Taxo START package is incomplete in this folder.
echo.
echo Найчастіша причина: START.bat запущено прямо з ZIP-архіву.
echo ZIP потрібно СПОЧАТКУ ПОВНІСТЮ РОЗПАКУВАТИ.
echo.
echo 1. Закрийте це вікно.
echo 2. У Провіднику Windows або 7-Zip виберіть "Видобути все / Extract all".
echo 3. Відкрийте розпаковану папку Taxo_v9_1_candidate_r9_5_START.
echo 4. Запустіть START.bat вже з цієї папки.
echo.
echo Поруч із START.bat обов'язково мають бути requirements.txt і taxo_app.py.
pause
exit /b 2
