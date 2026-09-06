#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================================
HỆ THỐNG XÁC THỰC, PHÂN QUYỀN & QUẢN TRỊ NGƯỜI DÙNG DOANH NGHIỆP (ENTERPRISE AUTH & RBAC)
SCHOLARGRAPH PRO v3.5 Enterprise Commercial Edition
Tác giả: TRẦN DUY (Lead AI Research Engineer)
==============================================================================
"""

import os
import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Cấu hình địa chỉ Email Quản trị & Bảo mật Tối cao
SUPER_ADMIN_EMAILS = [
    "tranduytno@gmail.com",
    "topxtmtk21@gmail.com",
    "topxtmtkt21@gmail.com"
]
SUPER_ADMIN_EMAIL = "tranduytno@gmail.com"
SECURITY_RECOVERY_EMAILS = ["topxtmtk21@gmail.com", "topxtmtkt21@gmail.com", "tranduytno@gmail.com"]
DEFAULT_SUPER_ADMIN_PASS = "@123"

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
AUTH_DB_PATH = os.path.join(DB_DIR, "scholargraph_auth.db")

def _get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(AUTH_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Băm mật khẩu an toàn chuẩn PBKDF2-HMAC-SHA256 với Salt 32 bytes."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex(), salt

def _verify_password(password: str, stored_hash: str, salt: str) -> bool:
    new_hash, _ = _hash_password(password, salt)
    return secrets.compare_digest(new_hash, stored_hash)

def init_auth_db():
    """Khởi tạo cấu trúc bảng xác thực và đảm bảo tài khoản Super Admin sẵn sàng."""
    conn = _get_db()
    cur = conn.cursor()
    
    # 1. Bảng Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL COLLATE NOCASE,
        full_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'researcher', -- super_admin, admin, researcher, viewer
        is_active INTEGER NOT NULL DEFAULT 1,
        must_change_password INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        last_login TEXT,
        created_by TEXT
    )
    """)
    
    # 2. Bảng Password Resets (Mã phục hồi mật khẩu bảo mật)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL COLLATE NOCASE,
        token TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        used INTEGER NOT NULL DEFAULT 0,
        dispatched_to TEXT NOT NULL
    )
    """)
    
    # 3. Bảng Audit Logs (Nhật ký truy cập và bảo mật)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        actor_email TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT DEFAULT '127.0.0.1'
    )
    """)
    conn.commit()

    now_str = datetime.now().isoformat()
    
    # Đảm bảo tất cả các tài khoản Quản trị tối cao đều được khởi tạo và sẵn sàng đăng nhập với pass mặc định @123
    for admin_mail in SUPER_ADMIN_EMAILS:
        cur.execute("SELECT * FROM users WHERE email = ?", (admin_mail,))
        row = cur.fetchone()
        if not row:
            p_hash, p_salt = _hash_password(DEFAULT_SUPER_ADMIN_PASS)
            cur.execute("""
            INSERT INTO users (email, full_name, password_hash, password_salt, role, is_active, must_change_password, created_at, created_by)
            VALUES (?, ?, ?, ?, 'super_admin', 1, 1, ?, 'SYSTEM_INIT')
            """, (admin_mail, f"TRẦN DUY ({admin_mail})", p_hash, p_salt, now_str))
            
            cur.execute("""
            INSERT INTO audit_logs (timestamp, actor_email, action, details)
            VALUES (?, 'SYSTEM', 'INIT_SUPER_ADMIN', ?)
            """, (now_str, f"Khởi tạo Super Admin {admin_mail}"))
            conn.commit()
    conn.close()

# Tự động khởi tạo DB khi nạp module
init_auth_db()

def authenticate_user(email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Xác thực đăng nhập người dùng."""
    email = email.strip().lower()
    if not email or not password:
        return False, None, "Vui lòng nhập đầy đủ Email và Mật khẩu."

    conn = _get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        log_audit_event(email, "LOGIN_FAILED", "Email không tồn tại trong danh sách cấp phép")
        return False, None, "Tài khoản không tồn tại hoặc chưa được Super Admin cấp phép truy cập."

    if not user["is_active"]:
        conn.close()
        log_audit_event(email, "LOGIN_BLOCKED", "Tài khoản đang bị tạm khóa")
        return False, None, "Tài khoản của bạn đã bị khóa bởi Quản trị viên."

    if not _verify_password(password, user["password_hash"], user["password_salt"]):
        conn.close()
        log_audit_event(email, "LOGIN_FAILED", "Sai mật khẩu")
        return False, None, "Mật khẩu không chính xác."

    # Cập nhật thời điểm đăng nhập
    now_str = datetime.now().isoformat()
    cur.execute("UPDATE users SET last_login = ? WHERE id = ?", (now_str, user["id"]))
    conn.commit()
    
    user_dict = dict(user)
    conn.close()
    
    log_audit_event(email, "LOGIN_SUCCESS", f"Đăng nhập thành công với vai trò {user['role']}")
    return True, user_dict, "Đăng nhập thành công!"

def change_user_password(email: str, old_password: str, new_password: str, is_first_time: bool = False) -> Tuple[bool, str]:
    """Đổi mật khẩu người dùng."""
    email = email.strip().lower()
    if len(new_password) < 6:
        return False, "Mật khẩu mới phải có tối thiểu 6 ký tự."
    
    if new_password == DEFAULT_SUPER_ADMIN_PASS:
        return False, "Vui lòng chọn mật khẩu mới khác với mật khẩu mặc định (@123)."

    conn = _get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return False, "Tài khoản không tồn tại."

    if not _verify_password(old_password, user["password_hash"], user["password_salt"]):
        conn.close()
        return False, "Mật khẩu hiện tại không chính xác."

    new_hash, new_salt = _hash_password(new_password)
    cur.execute("""
    UPDATE users 
    SET password_hash = ?, password_salt = ?, must_change_password = 0 
    WHERE email = ?
    """, (new_hash, new_salt, email))
    conn.commit()
    conn.close()
    
    log_audit_event(email, "PASSWORD_CHANGED", "Đã thay đổi mật khẩu thành công")
    return True, "Đổi mật khẩu thành công! Bạn có thể sử dụng hệ thống ngay bây giờ."

def request_password_reset(target_email: str) -> Tuple[bool, str, Optional[str]]:
    """Tạo mã phục hồi mật khẩu và điều hướng đến 2 email bảo mật chỉ định."""
    target_email = target_email.strip().lower()
    conn = _get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (target_email,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return False, "Email này chưa được cấp quyền trong hệ thống ScholarGraph Pro.", None

    # Sinh Token bí mật 32 ký tự
    token = secrets.token_urlsafe(24)
    now = datetime.now()
    expires = now + timedelta(hours=2) # Hết hạn sau 2 giờ
    dispatched_str = ", ".join(SECURITY_RECOVERY_EMAILS)

    cur.execute("""
    INSERT INTO password_resets (email, token, created_at, expires_at, used, dispatched_to)
    VALUES (?, ?, ?, ?, 0, ?)
    """, (target_email, token, now.isoformat(), expires.isoformat(), dispatched_str))
    conn.commit()
    conn.close()

    log_audit_event(
        target_email, 
        "RESET_REQUESTED", 
        f"Yêu cầu cấp lại mật khẩu. Mã Token gửi về: {dispatched_str}"
    )

    msg = (
        f"Đã phát lệnh đặt lại mật khẩu cho tài khoản: {target_email}.\n"
        f"Liên kết và mã Token xác thực đã được định tuyến gửi về 2 hòm thư bảo mật tối cao:\n"
        f"1. {SECURITY_RECOVERY_EMAILS[0]}\n"
        f"2. {SECURITY_RECOVERY_EMAILS[1]}"
    )
    return True, msg, token

def verify_and_reset_password(token: str, new_password: str) -> Tuple[bool, str]:
    """Xác thực Token và đổi mật khẩu mới."""
    token = token.strip()
    if len(new_password) < 6:
        return False, "Mật khẩu mới phải có tối thiểu 6 ký tự."

    conn = _get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM password_resets WHERE token = ? AND used = 0", (token,))
    reset_record = cur.fetchone()
    
    if not reset_record:
        conn.close()
        return False, "Mã Token không hợp lệ hoặc đã được sử dụng."

    expires_at = datetime.fromisoformat(reset_record["expires_at"])
    if datetime.now() > expires_at:
        conn.close()
        return False, "Mã Token đã hết hạn sử dụng (quá 2 giờ). Vui lòng yêu cầu cấp lại mã mới."

    target_email = reset_record["email"]
    new_hash, new_salt = _hash_password(new_password)
    
    # Cập nhật mật khẩu và đánh dấu Token đã dùng
    cur.execute("""
    UPDATE users 
    SET password_hash = ?, password_salt = ?, must_change_password = 0 
    WHERE email = ?
    """, (new_hash, new_salt, target_email))
    
    cur.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (reset_record["id"],))
    conn.commit()
    conn.close()

    log_audit_event(target_email, "PASSWORD_RESET_SUCCESS", "Khôi phục mật khẩu thành công qua Token")
    return True, f"Khôi phục mật khẩu thành công cho tài khoản {target_email}! Hãy đăng nhập lại."

def add_user_by_admin(email: str, full_name: str, role: str, actor_email: str, temp_password: str = "@123") -> Tuple[bool, str]:
    """Admin thêm tài khoản được chỉ định mới."""
    email = email.strip().lower()
    full_name = full_name.strip()
    if not email or "@" not in email:
        return False, "Địa chỉ Email không hợp lệ."
    if not full_name:
        full_name = email.split("@")[0].title()

    if role not in ["super_admin", "admin", "researcher", "viewer"]:
        role = "researcher"

    conn = _get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return False, f"Tài khoản {email} đã tồn tại trên hệ thống."

    p_hash, p_salt = _hash_password(temp_password)
    now_str = datetime.now().isoformat()
    cur.execute("""
    INSERT INTO users (email, full_name, password_hash, password_salt, role, is_active, must_change_password, created_at, created_by)
    VALUES (?, ?, ?, ?, ?, 1, 1, ?, ?)
    """, (email, full_name, p_hash, p_salt, role, now_str, actor_email))
    conn.commit()
    conn.close()

    log_audit_event(actor_email, "USER_CREATED", f"Thêm tài khoản mới {email} với quyền {role}")
    return True, f"✓ Đã cấp phép thành công cho tài khoản: {email} (Mật khẩu tạm thời: {temp_password})."

def get_all_users() -> List[Dict[str, Any]]:
    """Lấy danh sách toàn bộ người dùng trong hệ thống."""
    conn = _get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, email, full_name, role, is_active, must_change_password, created_at, last_login, created_by FROM users ORDER BY id ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def toggle_user_status(target_email: str, is_active: bool, actor_email: str) -> Tuple[bool, str]:
    """Khóa hoặc Mở khóa tài khoản."""
    target_email = target_email.strip().lower()
    if target_email == SUPER_ADMIN_EMAIL:
        return False, "Không thể khóa tài khoản Super Admin tối cao."

    conn = _get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_active = ? WHERE email = ?", (1 if is_active else 0, target_email))
    conn.commit()
    conn.close()

    action = "USER_ACTIVATED" if is_active else "USER_SUSPENDED"
    log_audit_event(actor_email, action, f"Đã {'mở khóa' if is_active else 'khóa'} tài khoản {target_email}")
    return True, f"Đã cập nhật trạng thái tài khoản {target_email} thành công."

def update_user_role(target_email: str, new_role: str, actor_email: str) -> Tuple[bool, str]:
    """Cập nhật phân quyền tài khoản."""
    target_email = target_email.strip().lower()
    if target_email == SUPER_ADMIN_EMAIL and new_role != "super_admin":
        return False, "Không thể hạ quyền Super Admin tối cao."

    conn = _get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = ? WHERE email = ?", (new_role, target_email))
    conn.commit()
    conn.close()

    log_audit_event(actor_email, "ROLE_UPDATED", f"Cập nhật vai trò {target_email} thành {new_role}")
    return True, f"Đã cập nhật vai trò {target_email} sang: {new_role}."

def delete_user_by_admin(target_email: str, actor_email: str) -> Tuple[bool, str]:
    """Xóa tài khoản khỏi danh sách cấp phép."""
    target_email = target_email.strip().lower()
    if target_email == SUPER_ADMIN_EMAIL:
        return False, "Tuyệt đối không thể xóa tài khoản Super Admin tối cao."

    conn = _get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE email = ?", (target_email,))
    conn.commit()
    conn.close()

    log_audit_event(actor_email, "USER_DELETED", f"Xóa tài khoản {target_email}")
    return True, f"Đã xóa vĩnh viễn quyền truy cập của tài khoản {target_email}."

def log_audit_event(actor_email: str, action: str, details: str):
    """Ghi nhận sự kiện bảo mật vào Audit Log."""
    try:
        conn = _get_db()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        cur.execute("""
        INSERT INTO audit_logs (timestamp, actor_email, action, details)
        VALUES (?, ?, ?, ?)
        """, (now_str, actor_email, action, details))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Lấy danh sách nhật ký kiểm toán hệ thống mới nhất."""
    conn = _get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
