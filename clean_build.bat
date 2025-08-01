@echo off
echo Cleaning build directories...

:: Force remove build directory
if exist build (
    echo Removing build\
    rmdir /s /q build 2>nul
    if exist build (
        echo Failed to remove build\ - trying with timeout
        timeout /t 2 /nobreak >nul
        rmdir /s /q build 2>nul
    )
)

:: Force remove dist directory
if exist dist (
    echo Removing dist\
    rmdir /s /q dist 2>nul
    if exist dist (
        echo Failed to remove dist\ - trying with timeout
        timeout /t 2 /nobreak >nul
        rmdir /s /q dist 2>nul
    )
)

:: Remove __pycache__
if exist __pycache__ (
    echo Removing __pycache__\
    rmdir /s /q __pycache__ 2>nul
)

:: Remove spec backup files
echo Removing *.spec.bak files...
del /f /q *.spec.bak 2>nul

echo.
echo Clean complete!
echo If any directories could not be removed, please:
echo 1. Close any programs using these files
echo 2. Disable OneDrive sync temporarily
echo 3. Run this script as Administrator
echo.