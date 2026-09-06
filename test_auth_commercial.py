#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Suite: Enterprise Authentication, RBAC & Dual-Recovery Routing
SCHOLARGRAPH PRO v3.5 Enterprise Commercial Edition
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

from utils.auth_manager import (
    SUPER_ADMIN_EMAIL,
    SECURITY_RECOVERY_EMAILS,
    DEFAULT_SUPER_ADMIN_PASS,
    authenticate_user,
    change_user_password,
    request_password_reset,
    verify_and_reset_password,
    add_user_by_admin,
    get_all_users,
    toggle_user_status,
    update_user_role,
    delete_user_by_admin,
    get_audit_logs
)

def run_auth_tests():
    print("=" * 70)
    print("🧪 KIỂM THỬ HỆ THỐNG XÁC THỰC DOANH NGHIỆP & PHÂN QUYỀN (AUTH & RBAC)")
    print("=" * 70)

    # Re-init fresh state
    db_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "scholargraph_auth.db")
    if os.path.exists(db_p):
        try:
            os.remove(db_p)
        except Exception:
            pass
    from utils.auth_manager import init_auth_db
    init_auth_db()

    # 1. Test Super Admin Default Login
    print("\n--- [1/6] Kiểm tra Đăng nhập Super Admin Mặc định ---")
    ok, u, msg = authenticate_user(SUPER_ADMIN_EMAIL, DEFAULT_SUPER_ADMIN_PASS)
    assert ok, f"Lỗi đăng nhập Super Admin: {msg}"
    assert u["role"] == "super_admin", "Vai trò không phải super_admin"
    print(f"✓ Đăng nhập thành công Super Admin: {u['email']} | Role: {u['role']} | Bắt buộc đổi pass: {bool(u['must_change_password'])}")


    # 2. Test Mandatory Password Change
    print("\n--- [2/6] Kiểm tra Đổi mật khẩu lần đầu ---")
    new_pass = "@SuperAdmin2026!"
    ok_c, msg_c = change_user_password(SUPER_ADMIN_EMAIL, DEFAULT_SUPER_ADMIN_PASS, new_pass, is_first_time=True)
    assert ok_c, f"Lỗi đổi mật khẩu: {msg_c}"
    
    # Verify new password works
    ok_new, u_new, _ = authenticate_user(SUPER_ADMIN_EMAIL, new_pass)
    assert ok_new, "Không thể đăng nhập bằng mật khẩu mới"
    assert u_new["must_change_password"] == 0, "Cờ must_change_password chưa được reset về 0"
    print(f"✓ Đã đổi mật khẩu thành công! must_change_password = {u_new['must_change_password']}")

    # 3. Test Non-whitelisted Email Login Rejection
    print("\n--- [3/6] Kiểm tra Chặn Email Chưa Cấp Phép ---")
    ok_hack, _, msg_hack = authenticate_user("stranger@unknown.com", "any_password")
    assert not ok_hack, "Email lạ không được phép đăng nhập!"
    print(f"✓ Chặn thành công email ngoài danh sách: {msg_hack}")

    # 4. Test Super Admin adding new User & RBAC
    print("\n--- [4/6] Kiểm tra Super Admin Thêm & Phân Quyền Người Dùng ---")
    test_user_email = "scholar.test@academic.vn"
    ok_add, msg_add = add_user_by_admin(test_user_email, "TS. Trần Nghiên Cứu", "researcher", SUPER_ADMIN_EMAIL)
    assert ok_add, f"Lỗi thêm user: {msg_add}"
    print(f"✓ Đã thêm tài khoản mới: {test_user_email}")
    
    # User logs in with default temp pass
    ok_u_login, u_temp, _ = authenticate_user(test_user_email, "@123")
    assert ok_u_login, "User mới không đăng nhập được bằng pass tạm"
    assert u_temp["must_change_password"] == 1, "User mới phải bắt buộc đổi pass"
    print(f"✓ Tài khoản mới đăng nhập thành công với pass tạm (@123), cờ đổi pass = 1")

    # 5. Test Password Reset Dual-Email Dispatch
    print("\n--- [5/6] Kiểm tra Phục hồi Mật khẩu & Điều hướng Email ---")
    ok_req, msg_req, token = request_password_reset(test_user_email)
    assert ok_req and token, f"Lỗi tạo token reset: {msg_req}"
    print(f"✓ Đã tạo Token: {token[:12]}... Định tuyến gửi về: {SECURITY_RECOVERY_EMAILS}")

    # Reset with token
    user_new_pass = "@ScholarPass999!"
    ok_reset, msg_reset = verify_and_reset_password(token, user_new_pass)
    assert ok_reset, f"Lỗi reset pass: {msg_reset}"
    print(f"✓ Khôi phục mật khẩu thành công qua Token: {msg_reset}")

    # Login with reset pass
    ok_after_reset, u_after, _ = authenticate_user(test_user_email, user_new_pass)
    assert ok_after_reset, "Không thể đăng nhập sau khi reset"
    print("✓ Đăng nhập thành công với mật khẩu mới sau khi khôi phục!")

    # 6. Test Audit Logs
    print("\n--- [6/6] Kiểm tra Nhật ký Kiểm toán Bảo mật (Audit Logs) ---")
    logs = get_audit_logs(10)
    assert len(logs) > 0, "Không có nhật ký kiểm toán"
    print(f"✓ Đã ghi nhận {len(logs)} sự kiện kiểm toán gần nhất:")
    for l in logs[:4]:
        print(f"   • [{l['timestamp'][:19]}] {l['actor_email']} -> {l['action']}: {l['details']}")

    # Clean up test user
    delete_user_by_admin(test_user_email, SUPER_ADMIN_EMAIL)
    
    # Reset database back to pristine initial state for real app usage
    if os.path.exists(db_p):
        try:
            os.remove(db_p)
        except Exception:
            pass
    init_auth_db()

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ CÁC BÀI TEST BẢO MẬT & PHÂN QUYỀN ĐÃ ĐẠT 100% XUẤT SẮC!")
    print("=" * 70)

if __name__ == "__main__":
    run_auth_tests()
