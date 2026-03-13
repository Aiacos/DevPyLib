@echo off
REM ============================================================================
REM DevPyLib Installer for Autodesk Maya (Windows)
REM
REM Copies Maya.env and userSetup.py to the correct Maya directories.
REM Run from the DevPyLib root directory.
REM
REM Usage:
REM   install.bat              Copy files (default)
REM   install.bat --symlink    Create symlink for userSetup.py instead of copy
REM ============================================================================

setlocal enabledelayedexpansion

set "DEVPYLIB_DIR=%~dp0"
set "MAYA_SCRIPTS_DIR=%USERPROFILE%\Documents\maya\scripts"
set "MAYA_ENV_SRC=%DEVPYLIB_DIR%mayaLib\Maya.env"
set "USERSETUP_SRC=%DEVPYLIB_DIR%mayaLib\userSetup.py"

REM --- Parse arguments ---
set "USE_SYMLINK=0"
if /I "%~1"=="--symlink" set "USE_SYMLINK=1"
if /I "%~1"=="-s" set "USE_SYMLINK=1"

echo.
echo === DevPyLib Installer ===
echo.
echo Source directory: %DEVPYLIB_DIR%
if "%USE_SYMLINK%"=="1" (
    echo Mode:             symlink
) else (
    echo Mode:             copy
)
echo.

REM --- Detect installed Maya versions ---
set "FOUND_MAYA=0"
for %%V in (2022 2023 2024 2025 2026) do (
    set "MAYA_ENV_DIR=%USERPROFILE%\Documents\maya\%%V"
    if exist "%USERPROFILE%\Documents\maya\%%V" (
        echo [OK] Maya %%V detected
        set "FOUND_MAYA=1"

        REM Maya.env is always copied (each version needs different content)
        copy /Y "%MAYA_ENV_SRC%" "%USERPROFILE%\Documents\maya\%%V\Maya.env" >nul 2>&1
        if errorlevel 1 (
            echo [!!] Failed to copy Maya.env to Maya %%V
        ) else (
            REM Replace Maya2024 references with the correct version
            powershell -NoProfile -Command "(Get-Content '%USERPROFILE%\Documents\maya\%%V\Maya.env') -replace 'Maya2024', 'Maya%%V' | Set-Content '%USERPROFILE%\Documents\maya\%%V\Maya.env'"
            echo      Copied Maya.env to maya\%%V\Maya.env (refs updated to Maya%%V)
        )
    )
)

if "%FOUND_MAYA%"=="0" (
    echo [!!] No Maya version directories found in %USERPROFILE%\Documents\maya\
    echo      Please install Maya first, or create the directory manually.
    goto :end
)

REM --- Install userSetup.py to shared scripts directory ---
echo.
if not exist "%MAYA_SCRIPTS_DIR%" (
    mkdir "%MAYA_SCRIPTS_DIR%"
    echo Created directory: %MAYA_SCRIPTS_DIR%
)

set "DEST=%MAYA_SCRIPTS_DIR%\userSetup.py"

if exist "%DEST%" (
    echo [!!] userSetup.py already exists at %MAYA_SCRIPTS_DIR%
    set /p "OVERWRITE=     Overwrite? (y/N): "
    if /I not "!OVERWRITE!"=="y" (
        echo      Skipped userSetup.py
        goto :done
    )
    del "%DEST%" >nul 2>&1
)

if "%USE_SYMLINK%"=="1" (
    mklink "%DEST%" "%USERSETUP_SRC%" >nul 2>&1
    if errorlevel 1 (
        echo [!!] Symlink failed (requires admin privileges). Falling back to copy...
        copy /Y "%USERSETUP_SRC%" "%DEST%" >nul 2>&1
        if errorlevel 1 (
            echo [!!] Failed to copy userSetup.py
        ) else (
            echo [OK] Copied userSetup.py to %MAYA_SCRIPTS_DIR% (symlink failed, used copy)
        )
    ) else (
        echo [OK] Symlinked userSetup.py to %MAYA_SCRIPTS_DIR%
    )
) else (
    copy /Y "%USERSETUP_SRC%" "%DEST%" >nul 2>&1
    if errorlevel 1 (
        echo [!!] Failed to copy userSetup.py
    ) else (
        echo [OK] Copied userSetup.py to %MAYA_SCRIPTS_DIR%
    )
)

:done
echo.
echo === Installation Complete ===
echo.
echo Files installed:
echo   Maya.env     ^-^> maya\{version}\Maya.env  (per-version, always copied)
if "%USE_SYMLINK%"=="1" (
    echo   userSetup.py ^-^> maya\scripts\userSetup.py (symlink)
) else (
    echo   userSetup.py ^-^> maya\scripts\userSetup.py (copy)
)
echo.
echo To disable Luna at startup, ensure Maya.env contains:
echo   DEVPYLIB_DISABLE_LUNA=1
echo.

:end
endlocal
pause
