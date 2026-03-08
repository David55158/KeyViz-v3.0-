@echo off
title KeyViz Launcher
echo  ___  ___  _  _  _  _  _  ____
echo ^|  _^^/ __^^|^| ^|^| ^|^| ^|| ^||_  /
echo ^| ^|_^^\__ ^^\^| ^|^| ^|^| ^|^| ^|^| / /
echo ^|_^|  ^|___/^|_^^| ^|___/^|_^^|/___|
echo.
echo KeyViz v4.0 — Made by D.T, Germany Munster
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Checking dependencies...
python -c "import pynput" >nul 2>&1
if errorlevel 1 (
    echo Installing pynput...
    pip install pynput -q
)
python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo Installing psutil...
    pip install psutil -q
)
python -c "import win32gui" >nul 2>&1
if errorlevel 1 (
    echo Installing pywin32...
    pip install pywin32 -q
)

echo Starting KeyViz...
start pythonw "%~dp0keyviz_overlay.py"
exit
