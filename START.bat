@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo   Taxo - запуск програми
echo ==============================================
echo.
py -3.13 -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ПОМИЛКА: не вдалося встановити необхідні пакети.
    pause
    exit /b 1
)
echo.
echo Запуск програми...
py -3.13 main.py
if errorlevel 1 (
    echo.
    echo ПОМИЛКА: програма завершила роботу з помилкою.
    pause
)
