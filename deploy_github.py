#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================================
CÔNG CỤ TỰ ĐỘNG HÓA TỐI ĐA UPLOAD GITHUB & PHÁT HÀNH STREAMLIT CLOUD
SCHOLARGRAPH PRO v3.5 Enterprise Commercial SaaS
Tác giả: TRẦN DUY (Lead AI Research Engineer)
Email Quản trị Tối cao: tranduytno@gmail.com
Email Bảo mật: topxtmtkt21@gmail.com & tranduytno@gmail.com
==============================================================================
"""

import os
import sys
import subprocess
import webbrowser
import time
import re

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

def print_banner():
    print("=" * 75)
    print("🚀 SCHOLARGRAPH PRO v3.5 ENTERPRISE - TỰ ĐỘNG HÓA UPLOAD GITHUB & CLOUD")
    print("👤 Tác giả: TRẦN DUY (Lead AI Research Engineer)")
    print("👑 Super Admin Tối cao: tranduytno@gmail.com")
    print("🛡️ Email Phục hồi Bảo mật: topxtmtkt21@gmail.com & tranduytno@gmail.com")
    print("=" * 75)

def run_cmd(cmd, capture=True):
    print(f"\n⚙️ Đang thực thi: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=capture, encoding='utf-8', errors='replace')
    if capture and res.stdout:
        print(res.stdout.strip())
    if capture and res.stderr and res.returncode != 0:
        print(f"⚠️ {res.stderr.strip()}")
    return res.returncode == 0, res.stdout.strip() if capture else ""

def get_github_username():
    """Lấy username GitHub đang đăng nhập qua GitHub CLI hoặc Git config."""
    ok, out = run_cmd("gh api user -q .login", capture=True)
    if ok and out:
        return out.strip()
    return "topxtmtk21"

def main():
    print_banner()

    # BƯỚC 1: KIỂM TRA GIT
    print("\n[1/5] Kiểm tra môi trường Git...")
    ok_git, _ = run_cmd("git --version", capture=True)
    if not ok_git:
        print("❌ Máy tính chưa có Git. Vui lòng cài Git từ https://git-scm.com/")
        input("Nhấn Enter để thoát...")
        sys.exit(1)

    # BƯỚC 2: CẤU HÌNH ĐỊNH DANH TÁC GIẢ
    print("\n[2/5] Thiết lập thông tin tác giả hệ thống...")
    run_cmd('git config user.name "TRAN DUY"')
    run_cmd('git config user.email "topxtmtk21@gmail.com"')
    print("✓ Đã cấu hình: TRAN DUY (topxtmtk21@gmail.com)")

    # BƯỚC 3: ĐÓNG GÓI MÃ NGUỒN VÀ DỮ LIỆU XÁC THỰC
    print("\n[3/5] Khởi tạo kho lưu trữ & đóng gói toàn bộ tính năng thương mại...")
    if not os.path.exists(".git"):
        run_cmd("git init")
        run_cmd("git branch -M main")
    else:
        run_cmd("git branch -M main")

    # Đảm bảo thư mục data/ luôn có file để Git theo dõi
    os.makedirs("data", exist_ok=True)
    gitkeep_p = os.path.join("data", ".gitkeep")
    if not os.path.exists(gitkeep_p):
        with open(gitkeep_p, "w", encoding="utf-8") as f:
            f.write("# Keep data directory in Git\n")

    # Đảm bảo Cổng Xác thực Super Admin ở trạng thái sẵn sàng
    try:
        from utils.auth_manager import init_auth_db
        init_auth_db()
    except Exception:
        pass

    run_cmd("git add .")
    commit_msg = f"Release ScholarGraph Pro v3.5 Enterprise with Super Admin tranduytno@gmail.com - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    run_cmd(f'git commit -m "{commit_msg}"')
    print("✓ Đã commit toàn bộ mã nguồn, bảo mật Auth và 10 Theme.")

    # BƯỚC 4: TỰ ĐỘNG KẾT NỐI VÀ ĐẨY LÊN GITHUB
    print("\n[4/5] Kết nối và đẩy mã nguồn lên GitHub...")
    
    # Kiểm tra remote
    ok_rem, rem_url = run_cmd("git remote get-url origin", capture=True)
    has_remote = ok_rem and bool(rem_url)
    
    # Kiểm tra gh CLI login status
    ok_gh_auth, _ = run_cmd("gh auth status", capture=True)
    
    repo_name = "scholargraph-pro"
    gh_username = "topxtmtk21"

    if not has_remote:
        if not ok_gh_auth:
            print("\n" + "-" * 60)
            print("🔐 BẠN CHƯA ĐĂNG NHẬP GITHUB CLI TRÊN MÁY TÍNH.")
            print("Hệ thống sẽ mở trình duyệt để bạn đăng nhập GitHub 1 lần duy nhất:")
            print("  1. Trình duyệt web sẽ tự động mở trang cấp quyền.")
            print("  2. Nhấn nút 'Authorize github' để hoàn tất xác thực.")
            print("-" * 60)
            input("👉 Nhấn Enter để mở trình duyệt đăng nhập GitHub...")
            subprocess.run("gh auth login --web -h github.com -p https", shell=True)
        
        # Sau khi login xong, lấy username thực tế
        gh_username = get_github_username()
        print(f"\n✓ Tài khoản GitHub xác thực: @{gh_username}")
        
        print(f"Đang tự động tạo kho lưu trữ GitHub '{repo_name}' và đẩy mã nguồn...")
        ok_create, _ = run_cmd(f"gh repo create {repo_name} --public --source=. --remote=origin --push --yes", capture=False)
        if not ok_create:
            # Nếu repo đã tồn tại trên GitHub, set remote và push đè
            fallback_url = f"https://github.com/{gh_username}/{repo_name}.git"
            print(f"Thử kết nối trực tiếp với: {fallback_url}")
            run_cmd(f"git remote add origin {fallback_url}")
            run_cmd("git push -u origin main --force")
    else:
        print(f"✓ Đã kết nối với Remote: {rem_url}")
        # Trích xuất username từ rem_url
        match_u = re.search(r'github\.com[:/]([^/]+)/', rem_url)
        if match_u:
            gh_username = match_u.group(1)
        print("Đang đẩy các cập nhật mới nhất lên GitHub (nhánh main)...")
        run_cmd("git push -u origin main")

    # BƯỚC 5: TỰ ĐỘNG ĐIỀU HƯỚNG ĐẾN STREAMLIT COMMUNITY CLOUD
    print("\n" + "=" * 75)
    print("🎉 ĐÃ TỰ ĐỘNG UPLOAD THÀNH CÔNG TOÀN BỘ MÃ NGUỒN LÊN GITHUB!")
    print(f"🔗 Kho lưu trữ GitHub: https://github.com/{gh_username}/{repo_name}")
    print("=" * 75)

    deploy_url = f"https://share.streamlit.io/deploy?repository={gh_username}/{repo_name}&branch=main&mainModule=app.py"
    
    print("\n🌐 BÂY GIỜ HỆ THỐNG SẼ TỰ ĐỘNG MỞ TRANG PHÁT HÀNH STREAMLIT CLOUD:")
    print(f"👉 Đường dẫn cấu hình sẵn: {deploy_url}")
    print("""
-----------------------------------------------------------------------
📋 CÁC BƯỚC HOÀN TẤT TRÊN TRÌNH DUYỆT (CHỈ CẦN 1 CÚ NHẤP CHUẬT):
1. Trang web Streamlit Cloud sẽ tự động điền sẵn Repo, Branch (main), và Main file (app.py).
2. (Tùy chọn) Nhấn 'Advanced settings' -> 'Secrets' -> dán khóa Gemini:
   GEMINI_API_KEY = "..."
   OPENALEX_EMAIL = "topxtmtk21@gmail.com"
3. Nhấn nút xanh: "Deploy!"
-----------------------------------------------------------------------
🔑 THÔNG TIN ĐĂNG NHẬP SAAS THƯƠNG MẠI TRỰC TUYẾN:
• Super Admin tối cao: tranduytno@gmail.com
• Mật khẩu mặc định: @123 (Hệ thống sẽ yêu cầu bạn đổi pass riêng ngay khi vào)
• Email nhận link/token reset mật khẩu: topxtmtkt21@gmail.com & tranduytno@gmail.com
-----------------------------------------------------------------------
""")

    try:
        webbrowser.open(deploy_url)
    except Exception:
        pass

    input("Nhấn Enter để hoàn tất quá trình xuất bản tự động...")

if __name__ == "__main__":
    main()
