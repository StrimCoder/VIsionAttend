@echo off
color 0B
title Quick Start - Smart Attendance System
mode con: cols=80 lines=20

echo.
echo  ╔══════════════════════════════════════════════════════════════════════════════╗
echo  ║                          QUICK START MENU                                   ║
echo  ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo  [1] Start System
echo  [2] Install AI Features
echo  [3] View System Status
echo  [4] Exit
echo.
set /p choice="Select option (1-4): "

if "%choice%"=="1" (
    echo Starting system...
    call START_SYSTEM.bat
) else if "%choice%"=="2" (
    echo Installing AI features...
    call INSTALL_AI.bat
) else if "%choice%"=="3" (
    echo Checking system status...
    curl -s http://localhost:8000/health 2>nul || echo Backend not running
    curl -s http://localhost:3000 2>nul || echo Frontend not running
    pause
) else if "%choice%"=="4" (
    exit
) else (
    echo Invalid choice. Please try again.
    timeout /t 2 >nul
    goto :start
)