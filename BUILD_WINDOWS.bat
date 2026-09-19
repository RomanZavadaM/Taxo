@echo off
setlocal
cd /d "%~dp0"
echo [Taxo 10.0] Installing build dependencies...
py -3.13 -m pip install -r requirements.txt pyinstaller==6.22.2
if errorlevel 1 goto :fail

echo [Taxo 10.0] Building portable onedir...
py -3.13 -m PyInstaller --noconfirm --clean Taxo.spec
if errorlevel 1 goto :fail
move "dist\Taxo" "dist\Taxo_v10_0_Windows_x64"
if errorlevel 1 goto :fail

echo Portable build ready: dist\Taxo_v10_0_Windows_x64\Taxo.exe
echo User data remains in the selected Taxo workspace.
exit /b 0

:fail
echo Build failed.
exit /b 1
