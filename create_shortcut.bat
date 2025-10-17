@echo off
echo ========================================
echo  Creating Desktop Shortcut
echo ========================================
echo.

:: Get the current directory
set "CURRENT_DIR=%~dp0"

:: Check if executable exists
if not exist "%CURRENT_DIR%dist\Instagram DM Automation.exe" (
    echo Error: Executable not found!
    echo Please run build_exe.bat first.
    echo.
    pause
    exit /b 1
)

:: Create VBScript to make shortcut
set "SCRIPT=%TEMP%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%SCRIPT%"
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Instagram DM Automation.lnk" >> "%SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%SCRIPT%"
echo oLink.TargetPath = "%CURRENT_DIR%dist\Instagram DM Automation.exe" >> "%SCRIPT%"
echo oLink.WorkingDirectory = "%CURRENT_DIR%dist" >> "%SCRIPT%"
echo oLink.Description = "Instagram DM Automation - Modern UI" >> "%SCRIPT%"
echo oLink.Save >> "%SCRIPT%"

:: Run the VBScript
cscript //nologo "%SCRIPT%"
del "%SCRIPT%"

echo.
echo ========================================
echo  Shortcut Created Successfully!
echo ========================================
echo.
echo Desktop shortcut created: Instagram DM Automation.lnk
echo.
echo You can now launch the application from your desktop!
echo.

pause

