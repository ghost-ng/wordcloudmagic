@echo off
echo Clearing Windows icon cache...
echo.

:: Kill explorer
taskkill /f /im explorer.exe

:: Delete icon cache
del /a /q "%localappdata%\IconCache.db"
del /a /f /q "%localappdata%\Microsoft\Windows\Explorer\iconcache*"

:: Restart explorer
start explorer.exe

echo.
echo Icon cache cleared! The taskbar icon should now update.
echo You may need to restart your computer for full effect.
pause