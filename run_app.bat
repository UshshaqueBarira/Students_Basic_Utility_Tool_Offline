@echo off
TITLE Utility Hub Setup and Runner
COLOR 0A

echo ===================================================
echo               Utility Hub Local Server             
echo ===================================================
echo.

:: Step 1: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10 or 3.11 from python.org and try again.
    pause
    exit /b
)

:: Step 2: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [1/4] Creating virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
    echo Virtual environment created successfully.
) else (
    echo [1/4] Virtual environment found.
)

:: Step 3: Activate venv and install dependencies
echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Installing / Updating required packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Step 4: Ensure necessary directories exist
if not exist "temp" mkdir temp
if not exist "models" mkdir models
if not exist "outputs" mkdir outputs

:: Step 5: Run application
echo.
echo ===================================================
echo Launching Utility Hub on http://127.0.0.1:7860
echo Press Ctrl+C in this command window to stop server.
echo ===================================================
echo.

python app.py

pause