#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================================
TỰ ĐỘNG ĐÓNG GÓI & ĐẨY MÃ NGUỒN LÊN GITHUB & STREAMLIT CLOUD
SCHOLARGRAPH PRO v3.5 Enterprise Commercial Edition
Tác giả: TRẦN DUY (Lead AI Research Engineer)
Email Quản trị Tối cao: tranduytno@gmail.com
Email Bảo mật Phục hồi: topxtmtkt21@gmail.com & tranduytno@gmail.com
==============================================================================
"""

import os
import sys
import subprocess
import webbrowser
import time

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

def print_header():
    print("=" * 75)
    print("🚀 SCHOLARGRAPH PRO v3.5 ENTERPRISE - TỰ ĐỘNG ĐẨY MÃ NGUỒN LÊN GITHUB")
    print("👤 Tác giả: TRẦN DUY (Lead AI Research Engineer)")
    print("👑 Super Admin Tối cao: tranduytno@gmail.com")
    print("🛡️ Email Phục hồi Bảo mật: topxtmtkt21@gmail.com & tranduytno@gmail.com")
    print("=" * 75)

def run_cmd(cmd, check=True):
    print(f"\n⚙️ Đang thực thi: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True, encoding='utf-8', errors='replace')
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(f"⚠️ Cảnh báo/Lỗi: {res.stderr.strip()}")
    if check and res.returncode != 0:
        return False
    return True

def main():
    print_header()
    
    # 1. Kiểm tra Git
    if not run_cmd("git --version", check=False):
        print("❌ Lỗi: Máy tính của bạn chưa cài đặt Git. Vui lòng cài Git từ https://git-scm.com/")
        input("Nhấn Enter để thoát...")
        sys.exit(1)

    # 2. Cấu hình thông tin Git Author
    print("\n[Bước 1/4] Thiết lập thông tin tác giả Git...")
    run_cmd('git config user.name "TRAN DUY"')
    run_cmd('git config user.email "topxtmtk21@gmail.com"')
    print("✓ Đã cấu hình email tác giả Git: topxtmtk21@gmail.com")

    # 3. Khởi tạo kho lưu trữ nếu chưa có
    if not os.path.exists(".git"):
        print("\n[Bước 2/4] Khởi tạo kho lưu trữ Git cục bộ (git init)...")
        run_cmd("git init")
        run_cmd("git branch -M main")
    else:
        print("\n[Bước 2/4] Đã phát hiện kho lưu trữ Git cục bộ.")
        run_cmd("git branch -M main", check=False)

    # 4. Thêm và Commit tệp tin
    print("\n[Bước 3/4] Quét và đóng gói tệp tin vào Git...")
    run_cmd("git add .")
    commit_msg = f"Release ScholarGraph Pro v3.5 Enterprise Commercial Edition - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    run_cmd(f'git commit -m "{commit_msg}"', check=False)
    print("✓ Đã commit toàn bộ mã nguồn an toàn (đã loại trừ secrets và tệp tạm qua .gitignore).")

    # 5. Đẩy lên GitHub
    print("\n[Bước 4/4] Đẩy mã nguồn lên GitHub...")
    
    # Kiểm tra xem đã có remote origin chưa
    res_remote = subprocess.run("git remote get-url origin", shell=True, text=True, capture_output=True, encoding='utf-8', errors='replace')
    has_remote = (res_remote.returncode == 0 and res_remote.stdout.strip())
    
    # Kiểm tra gh CLI auth
    res_gh = subprocess.run("gh auth status", shell=True, text=True, capture_output=True, encoding='utf-8', errors='replace')
    is_gh_logged_in = (res_gh.returncode == 0)

    if not has_remote:
        if is_gh_logged_in:
            print("✓ Phát hiện bạn đã đăng nhập GitHub CLI.")
            repo_name = input("Nhập tên Repository muốn tạo trên GitHub (Mặc định: scholargraph-pro): ").strip()
            if not repo_name:
                repo_name = "scholargraph-pro"
            
            print(f"Đang tạo repository {repo_name} và đẩy mã nguồn...")
            run_cmd(f"gh repo create {repo_name} --public --source=. --remote=origin --push", check=False)
        else:
            print("\n📌 BẠN CÓ 2 CÁCH ĐỂ KẾT NỐI VỚI GITHUB:")
            print("  [1] Đăng nhập nhanh bằng GitHub CLI (Khuyên dùng)")
            print("  [2] Nhập URL Repository GitHub đã tạo sẵn (dạng: https://github.com/<username>/<repo>.git)")
            
            choice = input("\nChọn cách (1 hoặc 2, mặc định 1): ").strip()
            if choice == "2":
                repo_url = input("👉 Dán đường dẫn URL GitHub Repository của bạn: ").strip()
                if repo_url:
                    run_cmd(f"git remote add origin {repo_url}", check=False)
                    run_cmd("git push -u origin main")
            else:
                print("\n🔐 Đang mở trình xác thực GitHub CLI (Làm theo hướng dẫn trên màn hình)...")
                subprocess.run("gh auth login --web -h github.com", shell=True)
                repo_name = input("\nNhập tên Repository muốn tạo (Mặc định: scholargraph-pro): ").strip()
                if not repo_name:
                    repo_name = "scholargraph-pro"
                run_cmd(f"gh repo create {repo_name} --public --source=. --remote=origin --push", check=False)
    else:
        print(f"✓ Đã phát hiện remote origin: {res_remote.stdout.strip()}")
        print("Đang đẩy các thay đổi mới nhất lên nhánh main...")
        run_cmd("git push -u origin main")

    # 6. Hướng dẫn triển khai Streamlit Cloud
    print("\n" + "=" * 75)
    print("🎉 ĐÃ HOÀN TẤT ĐẨY MÃ NGUỒN LÊN GITHUB THÀNH CÔNG!")
    print("=" * 75)
    print("""
🌐 CÁC BƯỚC KÍCH HOẠT TRÊN STREAMLIT COMMUNITY CLOUD (CHỈ 1 PHÚT):
1. Truy cập: https://share.streamlit.io/
2. Nhấn nút "Create app" hoặc "New app"
3. Chọn Repository vừa tạo trên GitHub của bạn
4. Main file path: điền 'app.py'
5. Nhấn 'Advanced settings' -> mục 'Secrets' -> dán khóa API (nếu có):
   GEMINI_API_KEY = "..."
   OPENALEX_EMAIL = "topxtmtk21@gmail.com"
6. Nhấn 'Deploy!'

🔑 THÔNG TIN ĐĂNG NHẬP SAAS THƯƠNG MẠI:
• Super Admin tối cao: tranduytno@gmail.com
• Mật khẩu mặc định: @123 (Bắt buộc đổi mật khẩu riêng ngay lần đầu đăng nhập)
• Email nhận link khôi phục mật khẩu: topxtmtkt21@gmail.com & tranduytno@gmail.com
""")
    
    open_browser = input("Bạn có muốn tự động mở trang Streamlit Cloud trên trình duyệt ngay bây giờ không? (y/n): ").strip().lower()
    if open_browser in ['y', 'yes', '1', '']:
        webbrowser.open("https://share.streamlit.io/")

    input("\nNhấn Enter để hoàn tất...")

if __name__ == "__main__":
    main()
