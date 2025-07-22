@echo off
setlocal enabledelayedexpansion

set VENV_DIR=venv_temp_build
set ICON=icon.ico
set SCRIPT=App.py
set APP_NAME=AegisConnect

echo *** Starting build process ***

REM 1. Remove existing temporary venv if it exists
if exist "%VENV_DIR%" (
    echo Removing existing virtual environment...
    REM Make sure no Python processes are running that lock files
    tasklist /FI "IMAGENAME eq python.exe" /FO LIST | findstr /I "%CD%\%VENV_DIR%" >nul
    if not errorlevel 1 (
        echo ERROR: Python processes are running from %VENV_DIR%. Please close them before continuing.
        pause
        exit /b 1
    )
    rmdir /s /q "%VENV_DIR%"
    if exist "%VENV_DIR%" (
        echo ERROR: Could not remove %VENV_DIR%. Please close any programs using it.
        pause
        exit /b 1
    )
)

REM 2. Create a new virtual environment
echo Creating new virtual environment...
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

REM 3. Activate the virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM 4. Upgrade pip and install requirements
echo Upgrading pip and installing requirements...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip.
    call deactivate
    rmdir /s /q "%VENV_DIR%"
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install required packages.
    call deactivate
    rmdir /s /q "%VENV_DIR%"
    pause
    exit /b 1
)

REM 5. Run PyInstaller to build the app
echo Building application with PyInstaller...
pyinstaller --onefile --clean --icon="%ICON%" --add-data "data;data" --add-data "templates;templates" --name "%APP_NAME%" "%SCRIPT%"
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    call deactivate
    rmdir /s /q "%VENV_DIR%"
    pause
    exit /b 1
)

REM 6. Deactivate virtual environment
echo Deactivating virtual environment...
call deactivate

REM 7. Clean up by removing the temporary venv
echo Cleaning up virtual environment...
rmdir /s /q "%VENV_DIR%"
if exist "%VENV_DIR%" (
    echo WARNING: Could not remove virtual environment folder completely. Please remove manually.
) else (
    echo Cleanup successful.
)

echo *** Build process complete! ***
pause
endlocal
