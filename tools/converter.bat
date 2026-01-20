@echo off
REM Cross-platform batch script for DevPyLib texture tools (Windows)
REM
REM This script automatically detects its location and runs texture_tools.py
REM without requiring hardcoded paths.
REM
REM Usage: converter.bat [args]

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Check if texture_tools.py exists
if not exist "%SCRIPT_DIR%texture_tools.py" (
    echo Error: texture_tools.py not found at %SCRIPT_DIR%texture_tools.py
    exit /b 1
)

REM Run texture_tools.py with any arguments passed to this script
python "%SCRIPT_DIR%texture_tools.py" %*