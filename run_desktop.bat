@echo off
chcp 65001 > nul
title ScholarGraph Pro — Nền tảng Trí tuệ Nhân tạo Nghiên cứu Báo chí Học thuật (TRẦN DUY)
color 0B

echo ===============================================================================
echo            SCHOLARGRAPH PRO — HỆ THỐNG MẠNG LƯỚI TRI THỨC HỌC THUẬT
echo               Bản quyền phát triển: TRẦN DUY (Lead AI Research Engineer)
echo ===============================================================================
echo.
echo [1/3] Đang kiểm tra môi trường Python và cơ sở dữ liệu...
python -c "import streamlit, openpyxl, docx, fitz, plotly, sqlite3; print('✓ Các thư viện chuyên dụng đã sẵn sàng 100%!')"
if %errorlevel% neq 0 (
    echo [!] Phát hiện thiếu thư viện, đang tự động cài đặt bổ sung...
    pip install streamlit pymupdf plotly openpyxl python-docx requests pandas
)

echo [2/3] Đang khởi động máy chủ Streamlit...
echo [3/3] Đang tự động mở giao diện ứng dụng trên trình duyệt web...
echo.
echo Ứng dụng đang hoạt động tại: http://localhost:8501
echo Nhấn Ctrl + C để dừng máy chủ.
echo ===============================================================================

start http://localhost:8501
streamlit run app.py --server.headless=true --server.port=8501 --browser.serverAddress="localhost"

pause
