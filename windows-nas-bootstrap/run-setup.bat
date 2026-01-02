@echo off
REM Windows NAS Bootstrap - Run Setup
REM This batch file launches the PowerShell setup script with administrator privileges.
REM Right-click and select "Run as administrator" to execute.

echo ========================================
echo    Windows NAS Bootstrap Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as administrator!
    echo.
    echo Please:
    echo   1. Right-click on run-setup.bat
    echo   2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Running setup script...
echo.

REM Run PowerShell script with execution policy bypass
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

REM Check if PowerShell script succeeded
set "exitCode=%errorLevel%"
if %exitCode% neq 0 (
    echo.
    echo Setup encountered errors. Exit code: %exitCode%
    pause
    exit /b %exitCode%
)

echo.
echo Setup completed successfully!
pause
