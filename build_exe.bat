@echo off
echo ========================================
echo  Instagram DM Automation - Build Script
echo ========================================
echo.

:: Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

:: Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build the executable
echo.
echo Building executable...
echo This may take a few minutes...
echo.

pyinstaller --clean instagram_automation.spec

:: Check if build was successful
if exist "dist\Instagram DM Automation.exe" (
    echo.
    echo ========================================
    echo  Build Successful!
    echo ========================================
    echo.
    echo Executable created at: dist\Instagram DM Automation.exe
    echo.
    echo Next steps:
    echo 1. Run "Instagram DM Automation.exe" from the dist folder
    echo 2. Enter your Instagram credentials in Settings tab
    echo 3. Import profiles via Flow Manager
    echo 4. Start automation!
    echo.
    echo To create a desktop shortcut, run: create_shortcut.bat
    echo.
) else (
    echo.
    echo ========================================
    echo  Build Failed!
    echo ========================================
    echo Please check the error messages above.
)

pause

