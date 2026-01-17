@echo off
color 0E
title AI Dependencies Installer
mode con: cols=80 lines=25

echo.
echo  ╔══════════════════════════════════════════════════════════════════════════════╗
echo  ║                        AI DEPENDENCIES INSTALLER                             ║
echo  ║                     Smart Attendance System v2.0                            ║
echo  ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo [INFO] Installing AI dependencies for enhanced face recognition...
echo.

cd backend

echo [STEP 1/4] Installing basic AI packages...
pip install opencv-python>=4.7.0
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install OpenCV
    pause
    exit /b 1
)

echo [STEP 2/4] Installing face recognition...
pip install face-recognition>=1.3.0
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install face-recognition
    pause
    exit /b 1
)

echo [STEP 3/4] Installing TensorFlow...
pip install tensorflow>=2.10.0
if %errorlevel% neq 0 (
    echo [WARNING] TensorFlow installation failed - continuing without deep learning features
)

echo [STEP 4/4] Installing additional dependencies...
pip install dlib numpy scikit-learn pillow websockets aiofiles
if %errorlevel% neq 0 (
    echo [WARNING] Some packages failed to install
)

echo.
echo [SUCCESS] AI dependencies installation completed!
echo.
echo [INFO] You can now use:
echo   • Advanced face recognition with masks/glasses support
echo   • Liveness detection (anti-spoofing)
echo   • Smartphone USB camera integration
echo   • Real-time AI processing
echo.
echo Press any key to continue...
pause >nul