@echo off
REM Windows NAS Bootstrap - Run Setup
REM Generated: 2025-11-05 21:04
REM
REM This batch file launches the PowerShell setup script with administrator privileges.
REM Right-click and select "Run as administrator" to execute.

echo ========================================
echo    Windows NAS Bootstrap Setup
echo    Generated: 2025-11-05 21:04
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
if %errorLevel% neq 0 (
    echo.
    echo Setup encountered errors. Exit code: %errorLevel%
    pause
    exit /b %errorLevel%
)

echo.
echo Setup completed successfully!
pause
