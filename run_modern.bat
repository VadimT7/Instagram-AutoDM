@echo off
echo ========================================
echo Instagram Automation Pro - Modern UI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import selenium" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Launch the modern GUI
echo Launching Modern UI...
python gui_modern.py

if %errorlevel% neq 0 (
    echo.
    echo Error occurred while running the application
    pause
)
