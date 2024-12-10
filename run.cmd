@echo off
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please download it from:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)
start "" pythonw zonepaq
exit
