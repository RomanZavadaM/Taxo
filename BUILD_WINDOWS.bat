@echo off
setlocal
cd /d "%~dp0"
echo [Taxo v8.70 TEST r5] Installing build dependencies...
py -3.13 -m pip install -r requirements.txt pyinstaller==6.22.2
if errorlevel 1 goto :fail

echo [Taxo v8.70 TEST r5] Building portable onedir...
py -3.13 -m PyInstaller --noconfirm --clean Taxo.spec
if errorlevel 1 goto :fail
move "dist\Taxo" "dist\Taxo_v8_70_TEST_r5_Windows_x64"
if errorlevel 1 goto :fail

echo Portable build ready: dist\Taxo_v8_70_TEST_r5_Windows_x64\Taxo.exe
echo User data remains in %%USERPROFILE%%\Documents\DriverWorktime\
exit /b 0

:fail
echo Build failed.
exit /b 1
