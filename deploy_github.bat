@echo off
py deploy_github.py 2>nul || python deploy_github.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] An error occurred while executing deploy_github.py.
)
pause
