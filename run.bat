@echo off
echo ===============================================
echo Instagram DM Automation System
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo Checking dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo.

REM Check if .env exists
if not exist ".env" (
    if exist "env.example" (
        echo Warning: .env file not found!
        echo Please copy env.example to .env and add your Instagram credentials
        echo.
        pause
    )
)

REM Run the main script
echo Starting Instagram DM Automation...
echo.
python main.py

REM Deactivate virtual environment
deactivate

echo.
echo ===============================================
echo Automation completed.
echo ===============================================
pause
