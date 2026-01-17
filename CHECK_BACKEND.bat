@echo off
color 0C
title Backend Connection Checker

echo.
echo ==========================================
echo    BACKEND CONNECTION CHECKER
echo ==========================================
echo.

echo [INFO] Checking if backend is running...
echo.

curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    color 0A
    echo [SUCCESS] Backend is running on port 8000!
    echo.
    curl -s http://localhost:8000/health
    echo.
) else (
    echo [ERROR] Backend is NOT running!
    echo.
    echo Please:
    echo 1. Run START_SYSTEM.bat first
    echo 2. Wait for backend to fully start
    echo 3. Check if port 8000 is available
    echo.
)

echo.
echo [INFO] Checking if frontend is accessible...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Frontend is running on port 3000!
) else (
    echo [ERROR] Frontend is NOT running!
)

echo.
echo ==========================================
pause