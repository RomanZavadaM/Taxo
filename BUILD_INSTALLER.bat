@echo off
setlocal
cd /d "%~dp0"
call BUILD_WINDOWS.bat
if errorlevel 1 exit /b 1
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo Inno Setup 6 not found. Portable build is ready in dist\Taxo.
  exit /b 2
)
"%ISCC%" installer\Taxo.iss
if errorlevel 1 exit /b 1
echo Installer ready in release_out\Taxo_v8_64_Setup_Windows_x64.exe
