@echo off
title Instagram DM Automation - Quick Build
color 0A

echo.
echo  ========================================================
echo    Instagram DM Automation - Quick Build Setup
echo  ========================================================
echo.
echo  This script will:
echo  1. Build the executable
echo  2. Setup required files
echo  3. Create desktop shortcut
echo  4. Launch the application
echo.
echo  Press any key to continue or Ctrl+C to cancel...
pause >nul

:: Step 1: Build
echo.
echo [1/4] Building executable...
echo ========================================================
call build_exe.bat

if not exist "dist\Instagram DM Automation.exe" (
    echo.
    echo Build failed! Please check the errors above.
    pause
    exit /b 1
)

:: Step 2: Setup files
echo.
echo [2/4] Setting up files...
echo ========================================================

:: Note about credentials
echo.
echo NOTE: Credentials are now stored in the application.
echo No .env file needed!
echo Just enter your Instagram username and password in Settings tab.
echo.

:: Copy CSV if it exists
if exist "InstagramProfiles.csv" (
    echo Copying InstagramProfiles.csv...
    copy /y "InstagramProfiles.csv" "dist\InstagramProfiles.csv" >nul
    echo CSV copied successfully!
)

:: Step 3: Create shortcut
echo.
echo [3/4] Creating desktop shortcut...
echo ========================================================
call create_shortcut.bat

:: Step 4: Launch option
echo.
echo [4/4] Setup Complete!
echo ========================================================
echo.
echo The application is ready to use!
echo.
echo Desktop shortcut created: Instagram DM Automation
echo Executable location: %~dp0dist\Instagram DM Automation.exe
echo.

set /p launch="Would you like to launch the application now? (Y/N): "
if /i "%launch%"=="Y" (
    echo.
    echo Launching application...
    start "" "%~dp0dist\Instagram DM Automation.exe"
    echo.
    echo Application launched!
) else (
    echo.
    echo You can launch it later from the desktop shortcut.
)

echo.
echo ========================================================
echo  Setup Complete! 
echo ========================================================
echo.
echo Next steps:
echo 1. If you haven't already, configure your Instagram credentials in Settings
echo 2. Import your profiles via Flow Manager
echo 3. Select a step and start automation!
echo.
echo For detailed instructions, see: DESKTOP_APP_GUIDE.md
echo.

pause

