@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Academic Research AI Pipeline - He Thong Tro Ly Nghien Cuu AI

:: Chuyen thu muc hien hanh ve dung thu muc cua file batch nay
cd /d "%~dp0"

echo ==============================================================================
echo       HE THONG DOI NGU TRO LY NGHIEN CUU AI (1 DOI -> 11 PHUT 03 GIAY)
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
echo [2/3] Kiem tra va cai dat thu vien (requirements.txt)...
%PYTHON_CMD% -m pip install -r requirements.txt --quiet --no-warn-script-location

echo.
echo [3/3] Khoi chay giao dien Streamlit...
echo Dia chi trinh duyet: http://localhost:8501
echo.
echo (Giu nguyen cua so nay khi dang su dung ung dung, nhan Ctrl+C de dung)
echo ==============================================================================
echo.

%PYTHON_CMD% -m streamlit run app.py --server.port=8501 --server.headless=false

echo.
echo ==============================================================================
echo Chuong trinh da ket thuc.
pause
