@echo off
chcp 65001 > nul
title Tự động Upload GitHub & Streamlit Cloud - ScholarGraph Pro v3.5
color 0B

echo ==============================================================================
echo   🚀 SCHOLARGRAPH PRO v3.5 - TỰ ĐỘNG HÓA TỐI ĐA UPLOAD GITHUB & CLOUD
echo   👤 Tác giả: TRẦN DUY (Lead AI Research Engineer)
echo   👑 Super Admin: tranduytno@gmail.com
echo   🛡️ Email Bảo mật: topxtmtkt21@gmail.com ^& tranduytno@gmail.com
echo ==============================================================================
echo.

python deploy_github.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Đã xảy ra lỗi trong quá trình tự động hóa. Vui lòng kiểm tra lại kết nối mạng hoặc Git.
)

pause
