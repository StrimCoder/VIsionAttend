@echo off
color 0A
title Smart Attendance System Launcher
mode con: cols=80 lines=30

:: Enable delayed variable expansion
setlocal EnableDelayedExpansion

:: Clear screen and show header
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════════════════════╗
echo  ║                    SMART ATTENDANCE SYSTEM LAUNCHER                          ║
echo  ║                           Version 2.0 Enhanced                              ║
echo  ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Check if directories exist
echo [INFO] Checking system requirements...
if not exist "backend" (
    color 0C
    echo [ERROR] Backend directory not found!
    echo Please ensure you're running this from the project root directory.
    pause
    exit /b 1
)

if not exist "frontend" (
    color 0C
    echo [ERROR] Frontend directory not found!
    echo Please ensure you're running this from the project root directory.
    pause
    exit /b 1
)

echo [✓] Directory structure verified
echo.

:: Progress bar function
echo [INFO] Initializing system components...
for /l %%i in (1,1,20) do (
    set /a progress=%%i*5
    set "bar="
    for /l %%j in (1,1,%%i) do set "bar=!bar!█"
    for /l %%k in (%%i,1,19) do set "bar=!bar!░"
    <nul set /p "=[!progress!%%] !bar!"
    timeout /t 0 >nul 2>&1
    echo.
)

echo.
echo [INFO] Installing Backend Dependencies (Minimal)...
cd backend
pip install -r requirements_minimal.txt
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Failed to install backend dependencies!
    echo Please check your Python installation and internet connection.
    pause
    exit /b 1
)
cd ..

echo [INFO] Starting Backend Server...
echo ┌─ Backend Configuration:
echo │  • Module: app.simple_main_no_face
echo │  • Port: 8001
echo │  • Status: Initializing...
echo └─
start "SAS Backend" cmd /k "title SAS Backend Server && color 0B && cd backend && python simple_server.py"

echo.
echo [INFO] Waiting for backend initialization...
for /l %%i in (5,-1,1) do (
    echo [WAIT] Backend starting in %%i seconds...
    timeout /t 1 /nobreak >nul
)

echo.
echo [INFO] Starting Frontend Server...
echo ┌─ Frontend Configuration:
echo │  • Framework: React
echo │  • Port: 3000
echo │  • Status: Installing dependencies...
echo └─
start "SAS Frontend" cmd /k "title SAS Frontend Server && color 0E && cd frontend && npm install && npm start"

echo.
echo [INFO] System startup sequence completed!
echo.
echo  ╔══════════════════════════════════════════════════════════════════════════════╗
echo  ║                           SYSTEM READY!                                     ║
echo  ╠══════════════════════════════════════════════════════════════════════════════╣
echo  ║  🌐 Backend API:     http://localhost:8001                                  ║
echo  ║  🖥️  Frontend UI:     http://localhost:3000                                  ║
echo  ║  📊 API Docs:        http://localhost:8001/docs                             ║
echo  ║  📋 Health Check:    http://localhost:8001/health                           ║
echo  ╠══════════════════════════════════════════════════════════════════════════════╣
echo  ║  💡 Quick Start:                                                             ║
echo  ║     1. Open http://localhost:3000 in your browser                           ║
echo  ║     2. Register a new account or login                                       ║
echo  ║     3. Upload face encoding in settings                                      ║
echo  ║     4. Start marking attendance!                                             ║
echo  ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Press any key to open the application in your default browser...
pause >nul

:: Open browser automatically
start "" "http://localhost:3000"

echo.
echo [SUCCESS] Application launched successfully!
echo [INFO] Press any key to exit this launcher...
pause >nul