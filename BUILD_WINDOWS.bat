@echo off
setlocal
cd /d "%~dp0"
echo [Taxo v8.66 TEST r4] Installing build dependencies...
py -3.13 -m pip install -r requirements.txt pyinstaller==6.15.0
if errorlevel 1 goto :fail

echo [Taxo v8.66 TEST r4] Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [Taxo v8.66 TEST r4] Building portable onedir...
py -3.13 -m PyInstaller --noconfirm --clean Taxo.spec
if errorlevel 1 goto :fail
move "dist\Taxo" "dist\Taxo_v8_66_TEST_r4_Windows_x64"
if errorlevel 1 goto :fail

echo.
echo Portable build ready: dist\Taxo_v8_66_TEST_r4_Windows_x64\Taxo.exe
echo User data remains in %%USERPROFILE%%\Documents\DriverWorktime\
exit /b 0

:fail
echo Build failed.
exit /b 1
