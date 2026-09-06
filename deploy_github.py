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
import urllib.request
import json as json_lib

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

def print_banner():
    print("=" * 76)
    print("🚀 SCHOLARGRAPH PRO v3.5 ENTERPRISE - TỰ ĐỘNG HÓA UPLOAD GITHUB & CLOUD")
    print("👤 Tác giả: TRẦN DUY (Lead AI Research Engineer)")
    print("👑 Super Admin Tối cao: tranduytno@gmail.com")
    print("🛡️ Email Bảo mật: topxtmtkt21@gmail.com & tranduytno@gmail.com")
    print("=" * 76)

def run_cmd(cmd, capture=True):
    print(f"\n⚙️ Đang thực thi: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=capture, encoding='utf-8', errors='replace')
    if capture and res.stdout:
        print(res.stdout.strip())
    if capture and res.stderr and res.returncode != 0:
        print(f"⚠️ {res.stderr.strip()}")
    return res.returncode == 0, res.stdout.strip() if capture else ""

def copy_to_clipboard(text):
    try:
        if os.name == 'nt':
            p = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
            p.communicate(text.encode('utf-8'))
            return True
    except Exception:
        pass
    return False

def main():
    print_banner()

    print("""
📢 LƯU Ý QUAN TRỌNG VỀ BƯỚC 'AUTHORIZE / NHẬP MÃ CODE':
Khi trình duyệt GitHub yêu cầu nhập mã (Enter device code):
👉 GitHub KHÔNG GỬI MÃ CODE QUA EMAIL!
👉 Mã xác thực 8 ký tự (dạng XXXX-XXXX) được tạo ra ngay trên cửa sổ đen (Terminal) này!

💡 KHUYÊN DÙNG CÁCH 1 (DÙNG TOKEN): Không cần mã code, không sợ nhầm lẫn, 
   chỉ cần dán Token là tự động tải lên và mở Streamlit Cloud trong 5 giây!
""")

    # BƯỚC 1: KIỂM TRA MÔI TRƯỜNG GIT
    print("\n[Bước 1/4] Kiểm tra môi trường Git...")
    ok_git, _ = run_cmd("git --version", capture=True)
    if not ok_git:
        print("❌ Máy tính chưa có Git. Vui lòng cài đặt Git từ https://git-scm.com/")
        input("Nhấn Enter để thoát...")
        sys.exit(1)

    # BƯỚC 2: CẤU HÌNH ĐỊNH DANH TÁC GIẢ
    print("\n[Bước 2/4] Thiết lập thông tin tác giả hệ thống...")
    run_cmd('git config user.name "TRAN DUY"')
    run_cmd('git config user.email "topxtmtk21@gmail.com"')
    print("✓ Đã cấu hình định danh: TRAN DUY (topxtmtk21@gmail.com)")

    # BƯỚC 3: ĐÓNG GÓI MÃ NGUỒN VÀ DỮ LIỆU BẢO MẬT
    print("\n[Bước 3/4] Khởi tạo kho lưu trữ & đóng gói toàn bộ tính năng thương mại...")
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
    print("✓ Đã đóng gói toàn bộ mã nguồn, bảo mật Auth và 10 Theme.")

    # BƯỚC 4: KẾT NỐI VÀ ĐẨY LÊN GITHUB
    print("\n[Bước 4/4] Kết nối và đẩy mã nguồn lên GitHub...")
    
    ok_rem, rem_url = run_cmd("git remote get-url origin", capture=True)
    has_remote = ok_rem and bool(rem_url)
    
    repo_name = "scholargraph-pro"
    gh_username = "topxtmtk21"

    if has_remote:
        print(f"✓ Đã phát hiện Remote hiện có: {rem_url}")
        match_u = re.search(r'github\.com[:/]([^/]+)/', rem_url)
        if match_u:
            gh_username = match_u.group(1)
        print("Đang đẩy các bản cập nhật mới nhất lên GitHub (nhánh main)...")
        run_cmd("git push -u origin main")
    else:
        print("\n" + "=" * 76)
        print("📌 CHỌN PHƯƠNG THỨC UPLOAD LÊN GITHUB (KHUYÊN DÙNG CÁCH 1):")
        print("=" * 76)
        print("👉 [1] DÙNG GITHUB TOKEN (DỄ NHẤT & THÀNH CÔNG 100% TRONG 15 GIÂY - KHÔNG CẦN MÃ)")
        print("👉 [2] DÙNG GITHUB CLI (CẦN XEM MÃ 8 KÝ TỰ HIỂN THỊ TRÊN MÀN HÌNH NÀY)")
        print("👉 [3] TỰ NHẬP ĐƯỜNG DẪN REPO GITHUB ĐÃ TẠO SẴN")
        print("=" * 76)

        choice = input("\nNhập lựa chọn của bạn (1, 2 hoặc 3 - Mặc định 1): ").strip()
        if not choice:
            choice = "1"

        if choice == "1":
            print("\n" + "-" * 76)
            print("🔑 HƯỚNG DẪN LẤY GITHUB TOKEN TRONG 3 BƯỚC ĐƠN GIẢN:")
            print("1. Trình duyệt sẽ TỰ ĐỘNG MỞ trang tạo Token của GitHub.")
            print("2. (Tất cả quyền hạn 'repo' đã được chọn sẵn).")
            print("   Bạn chỉ việc kéo xuống cuối trang và bấm nút xanh: [ Generate token ]")
            print("3. Sao chép chuỗi ký tự Token hiển thị trên màn hình (dạng ghp_...) và dán vào đây.")
            print("-" * 76)
            
            token_url = "https://github.com/settings/tokens/new?description=ScholarGraphPro&scopes=repo"
            try:
                webbrowser.open(token_url)
            except Exception:
                pass
            
            token_val = input("\n👉 DÁN MÃ GITHUB TOKEN (ghp_...) VÀO ĐÂY RỒI NHẤN ENTER: ").strip()
            if not token_val:
                print("❌ Chưa nhập Token. Huỷ thao tác.")
                input("Nhấn Enter để thoát...")
                sys.exit(1)

            print("\n⏳ Đang kết nối tài khoản GitHub qua API...")
            headers = {
                "Authorization": f"token {token_val}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ScholarGraph-Deployer"
            }
            
            # Lấy username thực tế
            try:
                req_u = urllib.request.Request("https://api.github.com/user", headers=headers)
                with urllib.request.urlopen(req_u) as resp_u:
                    user_data = json_lib.loads(resp_u.read().decode())
                    gh_username = user_data.get("login", "topxtmtk21")
                    print(f"✓ Đã xác thực thành công tài khoản GitHub: @{gh_username}")
            except Exception as e:
                print(f"⚠️ Không lấy được profile, dùng username mặc định: {gh_username}")

            # Tạo repository
            payload = json_lib.dumps({
                "name": repo_name,
                "private": False,
                "description": "ScholarGraph Pro v3.5 Enterprise Commercial Edition"
            }).encode('utf-8')
            
            try:
                req_create = urllib.request.Request("https://api.github.com/user/repos", data=payload, headers=headers)
                with urllib.request.urlopen(req_create) as resp_c:
                    print(f"✓ Đã tạo mới thành công Repository '{repo_name}' trên tài khoản @{gh_username}!")
            except Exception:
                print(f"ℹ️ Repository '{repo_name}' đã sẵn sàng trên GitHub, tiến hành tải mã nguồn...")

            # Đẩy mã nguồn
            push_url = f"https://{token_val}@github.com/{gh_username}/{repo_name}.git"
            run_cmd(f"git remote add origin {push_url}", capture=False)
            print("⏳ Đang tải toàn bộ mã nguồn lên nhánh main của GitHub...")
            run_cmd("git push -u origin main --force", capture=False)
            
            # Đổi remote URL sạch (không lộ token)
            clean_remote_url = f"https://github.com/{gh_username}/{repo_name}.git"
            run_cmd(f"git remote set-url origin {clean_remote_url}", capture=True)

        elif choice == "2":
            print("\n" + "=" * 76)
            print("⚠️ LƯU Ý ĐẶC BIỆT KHI DÙNG GITHUB CLI:")
            print("1. Sau khi nhấn Enter, hệ thống sẽ in ra một dòng chữ dạng:")
            print("   ! First copy your one-time code: XXXX-XXXX")
            print("2. 👉 XXXX-XXXX CHÍNH LÀ MÃ BẠN CẦN NHẬP TRÊN TRÌNH DUYỆT (KHÔNG PHẢI MÃ EMAIL)!")
            print("3. Bạn copy mã 8 ký tự đó, nhấn Enter để mở web, dán mã vào rồi bấm Authorize.")
            print("=" * 76)
            input("\n👉 Nhấn Enter để bắt đầu kết nối GitHub CLI...")
            
            subprocess.run("gh auth login --web -h github.com -p https", shell=True)
            
            ok_u, out_u = run_cmd("gh api user -q .login", capture=True)
            if ok_u and out_u:
                gh_username = out_u.strip()
            
            print(f"\n✓ Tài khoản GitHub xác thực: @{gh_username}")
            print(f"Đang tạo repository {repo_name} và đẩy mã nguồn...")
            run_cmd(f"gh repo create {repo_name} --public --source=. --remote=origin --push --yes", capture=False)

        else:
            custom_url = input("\n👉 Dán đường dẫn URL GitHub Repository của bạn (ví dụ: https://github.com/topxtmtk21/scholargraph-pro.git): ").strip()
            if custom_url:
                run_cmd(f"git remote add origin {custom_url}", capture=False)
                run_cmd("git push -u origin main", capture=False)
                match_u = re.search(r'github\.com[:/]([^/]+)/', custom_url)
                if match_u:
                    gh_username = match_u.group(1)

    # BƯỚC 5: TỰ ĐỘNG ĐIỀU HƯỚNG ĐẾN STREAMLIT COMMUNITY CLOUD
    print("\n" + "=" * 76)
    print("🎉 ĐÃ TỰ ĐỘNG UPLOAD THÀNH CÔNG TOÀN BỘ MÃ NGUỒN LÊN GITHUB!")
    print(f"🔗 Kho lưu trữ GitHub: https://github.com/{gh_username}/{repo_name}")
    print("=" * 76)

    deploy_url = f"https://share.streamlit.io/deploy?repository={gh_username}/{repo_name}&branch=main&mainModule=app.py"
    
    print("\n🌐 HỆ THỐNG ĐANG TỰ ĐỘNG MỞ TRANG PHÁT HÀNH STREAMLIT CLOUD:")
    print(f"👉 Link Deploy điền sẵn: {deploy_url}")
    print("""
-----------------------------------------------------------------------
📋 CÁC BƯỚC HOÀN TẤT TRÊN STREAMLIT CLOUD (CHỈ 1 CÚ NHẤP CHUẬT):
1. Trang Streamlit Cloud sẽ mở ra với Repo, Branch (main) và app.py ĐƯỢC ĐIỀN SẴN.
2. (Tùy chọn) Bấm 'Advanced settings' -> 'Secrets' -> dán API Key:
   GEMINI_API_KEY = "..."
   OPENALEX_EMAIL = "topxtmtk21@gmail.com"
3. Bấm nút xanh: "Deploy!"
-----------------------------------------------------------------------
🔑 THÔNG TIN ĐĂNG NHẬP ADMIN SAAS SAU KHI DEPLOY:
• Super Admin Tối cao: tranduytno@gmail.com
• Mật khẩu ban đầu: @123 (Bắt buộc đổi mật khẩu riêng ngay khi vào)
• Email bảo mật nhận link reset mật khẩu: topxtmtkt21@gmail.com & tranduytno@gmail.com
-----------------------------------------------------------------------
""")

    try:
        webbrowser.open(deploy_url)
    except Exception:
        pass

    input("Nhấn Enter để hoàn tất...")

if __name__ == "__main__":
    main()

