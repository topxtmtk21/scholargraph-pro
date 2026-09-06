@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title ScholarGraph Pro v3.5 - He Thong AI Nghien Cuu Hoc Thuat (Lead: TRAN DUY)

:: Chuyen thu muc hien hanh ve dung thu muc cua file batch nay
cd /d "%~dp0"

echo ==============================================================================
echo     SCHOLARGRAPH PRO v3.5 ENTERPRISE - TAC GIA: TRAN DUY
echo     He Thong AI Nghien Cuu & Phan Tich Mang Luoi Tri Thuc Hoc Thuat
echo ==============================================================================
echo.
echo [1/3] Kiem tra moi truong Python...

set "PYTHON_CMD="
where python >nul 2>&1 && set "PYTHON_CMD=python"
if "%PYTHON_CMD%"=="" (
    where py >nul 2>&1 && set "PYTHON_CMD=py -3"
)
if "%PYTHON_CMD%"=="" (
    where python3 >nul 2>&1 && set "PYTHON_CMD=python3"
)

if "%PYTHON_CMD%"=="" (
    echo [LOI] Khong tim thay Python tren he thong!
    echo Vui long cai dat Python 3.10 tro len tai https://www.python.org/ va tick chon "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo Dang su dung: %PYTHON_CMD%
%PYTHON_CMD% --version

echo.
echo [2/3] Kiem tra va cap nhat thu vien can thiet...
%PYTHON_CMD% -m pip install -r requirements.txt --quiet --no-warn-script-location

echo.
echo [3/3] Dang khoi chay giao dien ScholarGraph Pro tren trinh duyet...
echo Dia chi trinh duyet: http://localhost:8501
echo.
echo ==============================================================================
echo [LUU Y] Giu nguyen cua so nay trong suot qua trinh lam viec.
echo         Nhan Ctrl+C de dung ung dung khi muon thoat.
echo ==============================================================================
echo.

%PYTHON_CMD% -m streamlit run app.py --server.port=8501 --server.headless=false --browser.gatherUsageStats=false

echo.
echo ==============================================================================
echo Chuong trinh da ket thuc.
pause

