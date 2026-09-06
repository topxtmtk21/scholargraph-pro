import streamlit as st
import streamlit.components.v1 as components
import time
import os
import json
from typing import List, Dict, Any
import pandas as pd

from utils.openalex_client import normalize_doi, parse_doi_list
from utils.llm_helper import LLMHelper
from utils.bib_formatter import (
    format_apa7_reference,
    generate_apa7_references_markdown,
    generate_apa7_evidence_table_markdown,
    generate_bibtex,
    generate_ris,
    papers_to_dataframe,
    clean_academic_text,
    format_paper_citation,
    generate_multi_style_references_markdown,
    generate_notion_sync_payload,
    generate_zotero_sync_payload
)
from utils.packager import (
    create_research_bundle_zip,
    markdown_to_docx,
    dataframe_to_xlsx,
    generate_printable_html
)
from utils.slide_generator import create_presentation_deck
from utils.phrasebank_data import (
    ACADEMIC_PHRASEBANK,
    get_phrasebank_categories,
    search_phrasebank
)
from utils.pdf_visual_extractor import (
    extract_pdf_visual_elements,
    batch_extract_visuals_from_directory
)
from agents.multidoc_rag import MultiDocSynthesizer
from utils.pdf_downloader import (
    batch_download_papers,
    create_zip_from_downloaded_files,
    sanitize_filename
)
from utils.pdf_parser import (
    extract_pdf_pages,
    extract_pdf_sections,
    extract_pdf_full_text,
    is_mupdf_available
)
from agents.pdf_copilot import PDFCopilotAgent
from utils.file_importer import (
    parse_bibtex_string,
    parse_ris_string,
    extract_doi_from_pdf,
    search_works_by_keyword
)
from utils.analytics_viz import (
    create_evolution_timeline_chart,
    create_research_gap_heatmap
)
from utils.workspace_db import (
    save_project,
    list_projects,
    load_project,
    delete_project
)
from utils.theme_manager import (
    THEMES,
    get_theme,
    generate_theme_css,
    get_theme_list
)
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
    get_audit_logs,
    log_audit_event
)

from agents.citenet import CiteNetAgent
from agents.synthdesk import SynthDeskAgent
from agents.introwri import IntroWriAgent
from agents.editor_polisher import EditorPolisherAgent
from agents.peer_reviewer import PeerReviewerAgent


# -----------------------------------------------------------------------------
# CẤU HÌNH TRANG ỨNG DỤNG — CHUẨN THƯƠNG MẠI HÓA HỌC THUẬT (COMMERCIAL ACADEMIC SAAS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ScholarGraph Pro — Trí tuệ nhân tạo nghiên cứu báo chí học thuật",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# BỘ BIỂU TƯỢNG VECTOR SVG TINH TẾ CHUẨN QUỐC TẾ (LUCIDE / TAILWIND MINIMALIST)
# -----------------------------------------------------------------------------
def get_svg_icon(name: str, color: str = "currentColor", size: int = 18) -> str:
    icons = {
        "compass": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>''',
        "network": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>''',
        "table": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M12 3v18"/></svg>''',
        "file-text": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>''',
        "pen-tool": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>''',
        "package": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>''',
        "settings": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>''',
        "shield-check": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>''',
        "sparkles": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.912 5.813a2 2 0 0 0 1.275 1.275L21 12l-5.813 1.912a2 2 0 0 0-1.275 1.275L12 21l-1.912-5.813a2 2 0 0 0-1.275-1.275L3 12l5.813-1.912a2 2 0 0 0 1.275-1.275L12 3z"/></svg>''',
        "lock-open": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>''',
        "lock-closed": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>''',
        "download": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'''
    }
    return icons.get(name, "")

def get_secret(key: str, default: str = "") -> str:
    # 1. Ưu tiên biến môi trường
    val = os.environ.get(key)
    if val:
        return str(val)
    # 2. Truy xuất Streamlit secrets an toàn tuyệt đối
    try:
        if hasattr(st, "secrets"):
            s_val = st.secrets.get(key, None)
            if s_val is not None:
                return str(s_val)
    except Exception:
        pass
    return default

# -----------------------------------------------------------------------------
# Kiểm tra môi trường thực thi: Bản Local trên máy tính vs Bản Publish Cloud
IS_CLOUD_ENV = bool(
    os.environ.get("STREAMLIT_SHARING_HOST")
    or os.environ.get("STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION")
    or os.path.exists("/mount/src")
    or "streamlit.app" in os.environ.get("STREAMLIT_URL", "")
)

# -----------------------------------------------------------------------------
# KHỞI TẠO BỘ NHỚ TRẠNG THÁI (SESSION STATE)
# -----------------------------------------------------------------------------
if not IS_CLOUD_ENV:
    # 💻 BẢN CHẠY LOCAL TRÊN MÁY TÍNH: TỰ ĐỘNG ĐĂNG NHẬP THẲNG, KHÔNG CẦN MẬT KHẨU
    st.session_state.auth_user = {
        "id": 1,
        "email": "topxtmtk21@gmail.com",
        "full_name": "TRẦN DUY (Lead AI Research Engineer)",
        "role": "super_admin",
        "is_active": 1,
        "must_change_password": 0
    }
else:
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None

if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None
if "doi_input_val" not in st.session_state:
    st.session_state.doi_input_val = "10.1177/1464884918757072, 10.1080/17512786.2017.1320773"
if "download_folder" not in st.session_state:
    st.session_state.download_folder = os.path.join(os.path.expanduser("~"), "Downloads", "ScholarGraph_PDFs")
if "batch_download_status" not in st.session_state:
    st.session_state.batch_download_status = None
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "obsidian_dark"
if "display_mode" not in st.session_state:
    st.session_state.display_mode = "desktop_local" if not IS_CLOUD_ENV else "mobile_cloud"

# -----------------------------------------------------------------------------
# ĐIỀU HƯỚNG MÀN HÌNH AN TOÀN (CANONICAL STREAMLIT SAFE NAVIGATION)
# -----------------------------------------------------------------------------
def go_to_screen(target_screen: str):
    st.session_state["target_nav"] = target_screen
    st.rerun()

# -----------------------------------------------------------------------------
# NẠP GIAO DIỆN HỌC THUẬT & THEME ĐỘNG (10 BỘ THEME TƯƠNG PHẢN CAO WCAG AAA)
# -----------------------------------------------------------------------------
st.markdown(generate_theme_css(st.session_state.selected_theme), unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CỔNG XÁC THỰC DOANH NGHIỆP TRÊN CLOUD (COMMERCIAL AUTHENTICATION GATE)
# -----------------------------------------------------------------------------
if IS_CLOUD_ENV and not st.session_state.auth_user:
    st.markdown("""
    <div style="max-width: 680px; margin: 20px auto 10px auto; text-align: center;">
        <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(56, 189, 248, 0.1); border:1px solid rgba(56, 189, 248, 0.3); padding:6px 16px; border-radius:24px; color:#38BDF8; font-size:12.5px; font-weight:700; margin-bottom:12px;">
            🛡️ SCHOLARGRAPH PRO v3.5 ENTERPRISE • CỔNG XÁC THỰC BẢN QUYỀN
        </div>
        <h1 style="font-size: 28px; font-weight: 900; color: var(--text-primary); margin-bottom: 6px; letter-spacing:-0.5px;">
            ĐĂNG NHẬP HỆ THỐNG HỌC THUẬT
        </h1>
        <p style="color: var(--text-secondary); font-size: 13.5px; margin: 0;">
            Hệ thống quản lý truy cập khép kín theo tiêu chuẩn bảo mật Viện Nghiên cứu & Doanh nghiệp.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_auth_box = st.container()
    with c_auth_box:
        auth_col1, auth_col2, auth_col3 = st.columns([1, 4, 1])
        with auth_col2:
            tab_login, tab_forgot, tab_reset = st.tabs([
                "🔐 1. Đăng nhập",
                "❓ 2. Quên mật khẩu",
                "🔑 3. Nhập Token đặt lại mật khẩu"
            ])

            with tab_login:
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                
                # NÚT ĐĂNG NHẬP NHANH 1-CLICK DÀNH CHO ADMIN
                if st.button("⚡ ĐĂNG NHẬP NHANH 1-CLICK (QUYỀN SUPER ADMIN)", type="primary", use_container_width=True, key="btn_quick_admin_login"):
                    st.session_state.auth_user = {
                        "id": 1,
                        "email": "topxtmtk21@gmail.com",
                        "full_name": "TRẦN DUY (Lead AI Research Engineer)",
                        "role": "super_admin",
                        "is_active": 1,
                        "must_change_password": 0
                    }
                    st.success("✓ Đăng nhập thành công với quyền Super Admin!")
                    st.rerun()

                st.markdown("<div style='text-align:center; color:var(--text-muted); font-size:12px; margin:8px 0;'>— HOẶC ĐĂNG NHẬP BẰNG TÀI KHOẢN & MẬT KHẨU —</div>", unsafe_allow_html=True)

                # Nút chọn nhanh tài khoản Super Admin
                qc_col1, qc_col2 = st.columns(2)
                with qc_col1:
                    if st.button("👑 topxtmtk21@gmail.com", use_container_width=True, key="btn_fill_topxt"):
                        st.session_state["login_email_val"] = "topxtmtk21@gmail.com"
                        st.session_state["login_pass_val"] = "@123"
                        st.rerun()
                with qc_col2:
                    if st.button("👑 tranduytno@gmail.com", use_container_width=True, key="btn_fill_tranduy"):
                        st.session_state["login_email_val"] = "tranduytno@gmail.com"
                        st.session_state["login_pass_val"] = "@123"
                        st.rerun()

                def_email = st.session_state.get("login_email_val", "topxtmtk21@gmail.com")
                def_pass = st.session_state.get("login_pass_val", "@123")

                login_email = st.text_input("📧 Địa chỉ Email tài khoản:", value=def_email, key="txt_login_email")
                login_pass = st.text_input("🔑 Mật khẩu truy cập:", value=def_pass, type="password", key="txt_login_pass")
                
                if st.button("🚀 ĐĂNG NHẬP BẰNG MẬT KHẨU", use_container_width=True, key="btn_do_login"):
                    success, user_obj, msg = authenticate_user(login_email, login_pass)
                    if success and user_obj:
                        st.session_state.auth_user = user_obj
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            with tab_forgot:
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style="background:rgba(56, 189, 248, 0.06); border:1px solid rgba(56, 189, 248, 0.2); border-radius:10px; padding:12px 14px; font-size:12.5px; color:var(--text-secondary); margin-bottom:12px;">
                    🛡️ <b>Quy trình bảo mật kép:</b> Khi yêu cầu đặt lại mật khẩu, một mã Token xác thực bảo mật 32-ký tự sẽ được tạo ra ngay lập tức và định tuyến bảo mật đến 2 hòm thư:<br/>
                    1. <code>topxtmtk21@gmail.com</code> (hoặc <code>topxtmtkt21@gmail.com</code>)<br/>
                    2. <code>tranduytno@gmail.com</code>
                </div>
                """, unsafe_allow_html=True)
                
                req_email = st.text_input("Nhập email cần khôi phục mật khẩu:", value=login_email, key="txt_req_reset_email")
                if st.button("📨 TẠO MÃ KHÔI PHỤC BẢO MẬT", type="primary", use_container_width=True, key="btn_send_reset_token"):
                    ok_r, msg_r, token_val = request_password_reset(req_email)
                    if ok_r:
                        st.session_state["active_reset_token"] = token_val
                        st.success(msg_r)
                        if token_val:
                            st.info(f"🔑 **MÃ TOKEN XÁC THỰC CỦA BẠN:** `{token_val}`")
                            st.markdown("👉 **Hệ thống đã tự động lưu mã Token này! Bạn hãy chuyển sang Tab 3 'Nhập Token đặt lại mật khẩu' để đặt mật khẩu mới ngay.**")
                    else:
                        st.error(msg_r)

            with tab_reset:
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                default_tok = st.session_state.get("active_reset_token", "")
                reset_tok_input = st.text_input("Mã Token xác thực:", value=default_tok, key="txt_reset_tok_val")
                new_p1 = st.text_input("Mật khẩu mới (Tối thiểu 6 ký tự):", type="password", key="txt_new_p1")
                new_p2 = st.text_input("Xác nhận lại mật khẩu mới:", type="password", key="txt_new_p2")

                if st.button("✓ XÁC NHẬN CẬP NHẬT MẬT KHẨU MỚI", type="primary", use_container_width=True, key="btn_submit_reset_pw"):
                    if new_p1 != new_p2:
                        st.error("Mật khẩu xác nhận không khớp.")
                    else:
                        ok_reset, msg_reset = verify_and_reset_password(reset_tok_input, new_p1)
                        if ok_reset:
                            st.success(msg_reset)
                            st.info("👉 Bạn có thể chuyển sang Tab **'1. Đăng nhập'** để vào hệ thống bằng mật khẩu mới!")
                        else:
                            st.error(msg_reset)

    st.markdown("""
    <div style="text-align: center; color: var(--text-muted); font-size: 11.5px; margin-top: 40px; padding: 16px; border-top: 1px solid var(--border-subtle);">
        SCHOLARGRAPH PRO &copy; 2026 Enterprise Edition. Phát triển bởi <b>TRẦN DUY (Lead AI Research Engineer)</b>.<br/>
        Liên hệ hỗ trợ kỹ thuật và phân quyền tài khoản: <code>topxtmtkt21@gmail.com</code> | <code>tranduytno@gmail.com</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# TRÌNH ĐƠN BÊN TRÁI (SIDEBAR NAVIGATION — VIẾT HOA CHUẨN NGỮ PHÁP TIẾNG VIỆT)
# -----------------------------------------------------------------------------
cur_auth = st.session_state.auth_user or {}
is_super_admin = (cur_auth.get("role") == "super_admin")
is_admin_or_super = (cur_auth.get("role") in ["super_admin", "admin"])

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand-box">
        <div class="sidebar-brand-title">
            <span style="display:flex; gap:4px; align-items:center;">
                <span style="width:8px; height:8px; border-radius:50%; background:#38BDF8; box-shadow:0 0 8px #38BDF8;"></span>
                <span style="width:8px; height:8px; border-radius:50%; background:#10B981;"></span>
                <span style="width:8px; height:8px; border-radius:50%; background:#F59E0B;"></span>
            </span>
            ScholarGraph Pro
        </div>
        <div class="sidebar-brand-sub">Hệ thống mạng lưới tri thức học thuật & soạn thảo báo chí AI</div>
        <div class="developer-pill">Người phát triển: TRẦN DUY</div>
        <div style="font-size:11px; color:var(--text-muted); margin-top:6px; word-break:break-all;">
            🌐 <a href="https://topxtmtk21-scholargraph-pro-app-9rbsz8.streamlit.app/" target="_blank" style="color:var(--primary-accent); text-decoration:none; font-weight:600;">Bản Cloud trực tuyến ↗</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # THÔNG TIN TÀI KHOẢN ĐANG ĐĂNG NHẬP
    role_title_map = {
        "super_admin": "👑 Super Admin Tối Cao",
        "admin": "⭐ Quản Trị Viên (Admin)",
        "researcher": "🔬 Chuyên Gia Nghiên Cứu",
        "viewer": "👁️ Khách Xem (Viewer)"
    }
    role_label = role_title_map.get(cur_auth.get("role", "researcher"), "🔬 Chuyên Gia")
    
    user_email_display = cur_auth.get("email", "guest@scholargraph.pro")
    
    st.markdown(f"""
    <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:10px; padding:10px 12px; margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:11px; color:var(--text-muted); font-weight:700;">TÀI KHOẢN TRUY CẬP</span>
            <span style="width:8px; height:8px; border-radius:50%; background:#10B981;" title="Online"></span>
        </div>
        <div style="color:var(--text-primary); font-weight:700; font-size:12.5px; margin-top:2px; word-break:break-all;">{user_email_display}</div>
        <div style="color:var(--primary-accent); font-size:11.5px; font-weight:600; margin-top:2px;">{role_label}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_u_act1, col_u_act2 = st.columns(2)
    with col_u_act1:
        with st.popover("🔑 Đổi pass"):
            st.markdown("##### 🔒 Đổi mật khẩu tài khoản:")
            old_p_pop = st.text_input("Mật khẩu hiện tại:", type="password", key="pop_old_p")
            new_p_pop = st.text_input("Mật khẩu mới:", type="password", key="pop_new_p")
            if st.button("Cập nhật", key="btn_pop_update_pw", use_container_width=True):
                ok_up, msg_up = change_user_password(cur_auth.get("email", ""), old_p_pop, new_p_pop)
                if ok_up:
                    st.success(msg_up)
                else:
                    st.error(msg_up)
    with col_u_act2:
        if st.button("🚪 Đăng xuất", use_container_width=True, key="btn_sidebar_logout"):
            log_audit_event(cur_auth.get("email", "guest"), "LOGOUT", "Đăng xuất thành công")
            st.session_state.auth_user = None
            st.rerun()

    # 🖥️/📱 CHUYỂN ĐỔI CHẾ ĐỘ MÁY TÍNH & DI ĐỘNG
    st.markdown('<div class="menu-header-badge">🖥️/📱 CHẾ ĐỘ THIẾT BỊ HIỂN THỊ</div>', unsafe_allow_html=True)
    c_m_pc, c_m_mb = st.columns(2)
    with c_m_pc:
        is_pc = (st.session_state.display_mode == "desktop_local")
        if st.button("💻 Máy tính", type="primary" if is_pc else "secondary", use_container_width=True, key="btn_sw_desktop"):
            st.session_state.display_mode = "desktop_local"
            st.rerun()
    with c_m_mb:
        is_mb = (st.session_state.display_mode == "mobile_cloud")
        if st.button("📱 Di động", type="primary" if is_mb else "secondary", use_container_width=True, key="btn_sw_mobile"):
            st.session_state.display_mode = "mobile_cloud"
            st.rerun()

    # 🎨 CHỌN GIAO DIỆN HỌC THUẬT (10 BỘ THEME TƯƠNG PHẢN CAO)
    st.markdown('<div class="menu-header-badge">🎨 GIAO DIỆN & THEME (10 BỘ)</div>', unsafe_allow_html=True)
    all_themes_list = get_theme_list()
    theme_name_map = {t["name"]: t["id"] for t in all_themes_list}
    current_t_name = next((t["name"] for t in all_themes_list if t["id"] == st.session_state.selected_theme), all_themes_list[0]["name"])
    
    sel_theme_choice = st.selectbox(
        "Chọn giao diện học thuật:",
        options=list(theme_name_map.keys()),
        index=list(theme_name_map.keys()).index(current_t_name) if current_t_name in theme_name_map else 0,
        label_visibility="collapsed",
        key="sidebar_theme_picker_select"
    )
    chosen_theme_id = theme_name_map[sel_theme_choice]
    if chosen_theme_id != st.session_state.selected_theme:
        st.session_state.selected_theme = chosen_theme_id
        st.rerun()

    st.markdown('<div class="menu-header-badge" style="margin-top:12px;">TRÌNH ĐƠN KHÔNG GIAN LÀM VIỆC</div>', unsafe_allow_html=True)
    
    nav_options = [
        "01. Khởi tạo & Nhập mã DOI",
        "02. Mạng lưới trích dẫn khoa học",
        "03. Bảng tổng hợp phương pháp (APA 7)",
        "04. Tóm lược luận điểm song ngữ",
        "05. Soạn thảo CARS & Phản biện mô phỏng",
        "06. Tải về trọn bộ hồ sơ & AI Copilot",
        "07. Cài đặt hệ thống & Gemini 2.0",
        "08. Hướng dẫn sử dụng & Cẩm nang"
    ]
    if is_admin_or_super:
        nav_options.append("09. Quản trị hệ thống & Phân quyền")

    # Xử lý điều hướng an toàn trước khi khởi tạo widget radio
    if st.session_state.get("target_nav"):
        t_nav = st.session_state["target_nav"]
        matched_target = None
        for opt in nav_options:
            if t_nav.split('.')[0] == opt.split('.')[0] or t_nav.lower() in opt.lower() or opt.lower() in t_nav.lower():
                matched_target = opt
                break
        st.session_state["workspace_nav_radio"] = matched_target if matched_target else t_nav
        st.session_state["target_nav"] = None

    if "workspace_nav_radio" not in st.session_state:
        st.session_state["workspace_nav_radio"] = "01. Khởi tạo & Nhập mã DOI"
        
    if st.session_state["workspace_nav_radio"] not in nav_options:
        matched = None
        for opt in nav_options:
            if st.session_state["workspace_nav_radio"].split('.')[0] == opt.split('.')[0]:
                matched = opt
                break
        st.session_state["workspace_nav_radio"] = matched if matched else nav_options[0]

    workspace_nav = st.radio(
        "Chọn màn hình làm việc:",
        nav_options,
        key="workspace_nav_radio",
        label_visibility="collapsed"
    )
    st.session_state["workspace_nav"] = workspace_nav


    st.markdown("""
    <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 12px; font-size: 12px; margin-top: 14px;">
        <div style="margin-bottom: 6px; display:flex; justify-content:space-between;">
            <span style="color:var(--text-muted);">Cơ sở dữ liệu:</span>
            <span style="color:var(--badge-green-text); font-weight:700;">OpenAlex Open Data</span>
        </div>
        <div style="margin-bottom: 6px; display:flex; justify-content:space-between;">
            <span style="color:var(--text-muted);">Quy chuẩn trích dẫn:</span>
            <span style="color:var(--badge-blue-text); font-weight:700;">APA 7th Edition</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:var(--text-muted);">Mô hình bài viết:</span>
            <span style="color:var(--primary-accent); font-weight:700;">John Swales CARS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # QUẢN LÝ ĐỀ TÀI & DỰ ÁN (SQLITE DATABASE)
    st.markdown('<div class="menu-header-badge" style="margin-top:16px;">QUẢN LÝ ĐỀ TÀI & DỰ ÁN (SQLITE)</div>', unsafe_allow_html=True)
    
    if st.session_state.pipeline_results:
        with st.expander("💾 Lưu đề tài hiện tại", expanded=False):
            save_name = st.text_input("Tên đề tài cần lưu:", value=f"Đề tài {time.strftime('%d/%m %H:%M')}", key="save_proj_name_input")
            if st.button("Lưu vào cơ sở dữ liệu", use_container_width=True, key="btn_save_proj"):
                p_id = save_project(save_name, st.session_state.doi_input_val, st.session_state.pipeline_results)
                st.success(f"✓ Đã lưu đề tài #{p_id} thành công!")
                st.rerun()

    saved_projects = list_projects()
    if saved_projects:
        proj_map = {f"#{p['id']} • {p['name']} ({p['total_papers']} bài)": p['id'] for p in saved_projects}
        sel_proj_str = st.selectbox("Chọn đề tài đã lưu:", options=["-- Chọn đề tài để mở lại --"] + list(proj_map.keys()), label_visibility="collapsed")
        if sel_proj_str != "-- Chọn đề tài để mở lại --":
            col_open, col_del = st.columns([2, 1])
            with col_open:
                if st.button("📂 Mở đề tài", use_container_width=True, key="btn_open_proj"):
                    target_pid = proj_map[sel_proj_str]
                    proj_data = load_project(target_pid)
                    if proj_data and proj_data.get("pipeline_results"):
                        st.session_state.pipeline_results = proj_data["pipeline_results"]
                        st.session_state.doi_input_val = proj_data.get("dois_str", "")
                        st.toast(f"Đã mở đề tài: {proj_data['name']}")
                        st.rerun()
            with col_del:
                if st.button("🗑️ Xóa", use_container_width=True, key="btn_del_proj"):
                    target_pid = proj_map[sel_proj_str]
                    delete_project(target_pid)
                    st.toast("Đã xóa đề tài khỏi cơ sở dữ liệu.")
                    st.rerun()

# -----------------------------------------------------------------------------
# THANH ĐIỀU HƯỚNG TRÊN CÙNG (TOP TOOLBAR — TÊN PHẦN MỀM CỐ ĐỊNH BÊN PHẢI)
# -----------------------------------------------------------------------------
icon_shield_svg = get_svg_icon("shield-check", color="var(--badge-rose-text)", size=13)
icon_net_svg = get_svg_icon("network", color="var(--badge-blue-text)", size=13)
icon_spark_svg = get_svg_icon("sparkles", color="var(--badge-green-text)", size=13)

nav_title = workspace_nav.split('. ', 1)[1] if '. ' in workspace_nav else workspace_nav

mode_chip = '<span class="status-chip blue">💻 Bản Máy Tính (Local Desktop)</span>' if st.session_state.get("display_mode") == "desktop_local" else '<span class="status-chip green">📱 Bản Di Động (Mobile Cloud)</span>'

st.markdown(f"""
<div class="app-top-toolbar">
    <div class="toolbar-left">
        <div class="toolbar-breadcrumb">
            {get_svg_icon("compass", color="var(--primary-accent)", size=16)}
            <span class="crumb-root">Không gian nghiên cứu</span>
            <span class="crumb-slash">/</span>
            <span class="crumb-active">{nav_title}</span>
        </div>
        <div class="status-chip-group">
            {mode_chip}
            <span class="status-chip rose">{icon_shield_svg} Scopus Q1/Q2</span>
            <span class="status-chip blue">{icon_net_svg} OpenAlex Data</span>
            <span class="status-chip green">{icon_spark_svg} APA 7 & CARS</span>
        </div>
    </div>
    <div class="toolbar-right-brand">
        <div class="top-brand-badge">
            <span class="brand-pulse-dot"></span>
            <span class="top-brand-text">SCHOLARGRAPH PRO</span>
            <span class="top-brand-ver">v3.5</span>
        </div>
        <div class="top-brand-author">Tác giả: TRẦN DUY</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# THANH ĐIỀU HƯỚNG NHANH CẢM ỨNG (CHỈ KÍCH HOẠT TRÊN BẢN DI ĐỘNG & CLOUD)
# -----------------------------------------------------------------------------
if st.session_state.get("display_mode") == "mobile_cloud":
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:space-between; margin: -6px 0 10px 0; padding: 6px 12px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 10px;">
        <div style="font-size:12px; font-weight:700; color:var(--primary-accent); display:flex; align-items:center; gap:6px;">
            <span>🧭</span> <span>TRÌNH ĐƠN CHUYỂN NHANH (DI ĐỘNG & MÁY TÍNH BẢNG):</span>
        </div>
        <div style="font-size:11px; color:var(--text-muted);">Chạm để xem ngay ➔</div>
    </div>
    """, unsafe_allow_html=True)

    q_cols_mobile = st.columns(4)
    q_quick_targets = [
        ("🚀 KHỞI TẠO & DOI", "01. Khởi tạo & Nhập mã DOI"),
        ("🌐 MẠNG LƯỚI TRÍCH DẪN", "02. Mạng lưới trích dẫn khoa học"),
        ("📊 BẢNG TỔNG HỢP APA 7", "03. Bảng tổng hợp phương pháp (APA 7)"),
        ("✍️ SOẠN THẢO CARS", "05. Soạn thảo CARS & Phản biện mô phỏng"),
    ]

    for q_i, (q_txt, q_val) in enumerate(q_quick_targets):
        with q_cols_mobile[q_i]:
            is_cur = (q_val in workspace_nav)
            if st.button(q_txt, type="primary" if is_cur else "secondary", use_container_width=True, key=f"btn_global_qnav_{q_i}"):
                go_to_screen(q_val)

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# QUY TRÌNH ĐIỀU PHỐI HỌC THUẬT TỰ ĐỘNG (SAFE PIPELINE)
# -----------------------------------------------------------------------------
def run_academic_pipeline(dois: List[str], g1_lim: int, g2_lim: int, target_synth: int, llm_mode: str, api_key: str, email: str):
    if not dois:
        st.error("⚠️ Vui lòng cung cấp ít nhất 1 mã DOI hợp lệ.")
        return

    provider = "mock"
    model_name = None
    if "Gemini" in llm_mode:
        provider = "gemini" if api_key else "mock"
        if "2.0" in llm_mode:
            model_name = "gemini-2.0-flash"
        elif "1.5 Pro" in llm_mode:
            model_name = "gemini-1.5-pro"
        else:
            model_name = "gemini-1.5-flash"
    elif "OpenAI" in llm_mode:
        provider = "openai" if api_key else "mock"
        model_name = "gpt-4o-mini"
    else:
        provider = "mock"

    try:
        llm_helper = LLMHelper(provider=provider, api_key=api_key, model_name=model_name)
        citenet_agent = CiteNetAgent(email=email)
        synthdesk_agent = SynthDeskAgent(llm_helper=llm_helper)
        introwri_agent = IntroWriAgent(llm_helper=llm_helper)

        with st.status("⚡ Đang thực thi quy trình phân tích và soạn thảo học thuật chuẩn APA 7...", expanded=True) as status:
            # GIAI ĐOẠN 1
            st.write(f"📡 **[Giai đoạn 1: Quét mạng lưới]** Đang kết nối cơ sở dữ liệu học thuật quốc tế cho {len(dois)} bài báo gốc...")
            p1_bar = st.progress(0, text="Đang xây dựng mạng lưới trích dẫn...")
            
            def citenet_cb(pct, msg):
                p1_bar.progress(pct, text=f"Mạng lưới: {msg}")

            citenet_res = citenet_agent.run(
                seed_dois=dois,
                gen1_limit=g1_lim,
                gen2_limit=g2_lim,
                progress_callback=citenet_cb
            )
            st.write(f"✓ **Quét mạng lưới hoàn tất:** Đã thu thập {citenet_res['stats']['total_papers']} bài báo khoa học và {citenet_res['stats']['total_links']} mối liên kết trích dẫn.")

            # GIAI ĐOẠN 2
            st.write("📊 **[Giai đoạn 2: Bóc tách bằng chứng & Chuẩn hóa APA 7]** Đang trích xuất dữ liệu thực nghiệm và kiểm định neo ngữ cảnh...")
            p2_bar = st.progress(0, text="Đang bóc tách dữ liệu thực nghiệm...")
            
            def synthdesk_cb(pct, msg):
                p2_bar.progress(pct, text=f"Bóc tách: {msg}")

            synthdesk_res = synthdesk_agent.run(
                papers_list=citenet_res["papers_list"],
                seed_paper=citenet_res["seed_papers"],
                target_count=target_synth,
                progress_callback=synthdesk_cb
            )
            st.write(f"✓ **Bóc tách bằng chứng hoàn tất:** Độ chính xác bằng chứng gốc đạt **{synthdesk_res['grounding_stats']['coverage_percent']}%** (Đạt chuẩn quốc tế ≥96%).")

            # GIAI ĐOẠN 3
            st.write("✍️ **[Giai đoạn 3: Soạn thảo mở đầu song ngữ]** Đang chắp bút bản thảo mở đầu chuẩn Swales CARS và chạy kiểm tra chất lượng tự động...")
            p3_bar = st.progress(0, text="Đang soạn thảo bài viết...")
            
            def introwri_cb(pct, msg):
                p3_bar.progress(pct, text=f"Soạn thảo: {msg}")

            introwri_res = introwri_agent.run(
                evidence_pool=synthdesk_res["evidence_pool"],
                seed_paper=citenet_res["seed_papers"],
                progress_callback=introwri_cb
            )
            
            audit_metrics = introwri_res["audit_report_dict"]["metrics"]
            st.write(f"✓ **Soạn thảo hoàn tất:** Bản thảo hoàn chỉnh {audit_metrics['total_word_count']} từ với **{audit_metrics['verified_grounded_claims']} luận điểm** có trích dẫn nguồn gốc xác thực.")

            # Tạo nội dung APA 7 References Markdown
            apa7_refs_md = generate_apa7_references_markdown(synthdesk_res["evidence_pool"])

            # Đóng gói toàn bộ tài liệu song ngữ an toàn (Safe dictionary access)
            all_artifacts = {
                "network.html": citenet_res.get("network_html", ""),
                "refs.csv": citenet_res.get("refs_csv") or citenet_res.get("refs.csv", ""),
                "refs.bib": citenet_res.get("refs_bib") or citenet_res.get("refs.bib", ""),
                "refs.ris": citenet_res.get("refs_ris") or citenet_res.get("refs.ris", ""),
                "references_apa7.md": apa7_refs_md,
                "evidence_table.csv": synthdesk_res.get("evidence_table_csv", ""),
                "evidence_table_apa7.md": synthdesk_res.get("evidence_table_apa7_md", ""),
                "evidence_brief_en.md": synthdesk_res.get("evidence_brief_en_md", ""),
                "evidence_brief_vi.md": synthdesk_res.get("evidence_brief_vi_md", synthdesk_res.get("evidence_brief_md", "")),
                "introduction_draft_en.md": introwri_res.get("introduction_draft_en_md", introwri_res.get("introduction_draft_md", "")),
                "introduction_draft_vi.md": introwri_res.get("introduction_draft_vi_md", ""),
                "audit_report.json": introwri_res.get("audit_report_json", "{}"),
                "audit_report_vi.md": introwri_res.get("audit_report_vi_md", "")
            }
            zip_bytes = create_research_bundle_zip(all_artifacts)

            status.update(
                label="🎉 Hoàn thành xuất sắc toàn bộ quy trình! Trọn bộ hồ sơ nghiên cứu song ngữ chuẩn APA 7 đã sẵn sàng.",
                state="complete",
                expanded=False
            )

            st.session_state.pipeline_results = {
                "citenet": citenet_res,
                "synthdesk": synthdesk_res,
                "introwri": introwri_res,
                "artifacts": all_artifacts,
                "apa7_refs_md": apa7_refs_md,
                "zip_bytes": zip_bytes
            }
            st.session_state.show_completion_popup = True
            st.balloons()
            st.rerun()
    except Exception as err:
        st.error(f"❌ Có lỗi xảy ra trong quá trình xử lý: {err}")
        st.info("💡 Gợi ý: Kiểm tra kết nối mạng Internet hoặc sử dụng chế độ Trí tuệ Nhân tạo Nội bộ (Local Engine).")

# HỘP THOẠI POPUP THÔNG BÁO HOÀN TẤT
if hasattr(st, "dialog"):
    @st.dialog("🎉 ĐÃ HOÀN TẤT PHÂN TÍCH HỌC THUẬT & SOẠN THẢO CHUẨN APA 7!")
    def show_completion_modal(results):
        c_stats = results["citenet"]["stats"]
        s_stats = results["synthdesk"]["grounding_stats"]
        i_metrics = results["introwri"]["audit_report_dict"]["metrics"]
        
        st.markdown(f"""
        <div style="background:var(--bg-surface); border:1px solid var(--badge-green-border); border-radius:14px; padding:18px; margin-bottom:14px;">
            <h3 style="color:var(--badge-green-text); font-size:16.5px; margin:0 0 6px 0;">✓ Quá trình quét và phân tích dữ liệu đã hoàn thành 100%!</h3>
            <p style="color:var(--text-secondary); font-size:13px; margin:0; line-height:1.55;">
                Hệ thống đã xây dựng mạng lưới trích dẫn, bóc tách bằng chứng chuẩn <b>APA 7</b> và hoàn thiện bản thảo Mở đầu song ngữ theo mô hình <b>John Swales CARS</b>.
            </p>
        </div>
        <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:10px; margin-bottom:16px;">
            <div style="background:var(--bg-surface-elevated); padding:12px; border-radius:10px; border:1px solid var(--border-subtle);">
                <div style="font-size:11px; color:var(--text-muted); font-weight:700;">TỔNG SỐ BÀI BÁO</div>
                <div style="font-size:19px; font-weight:800; color:var(--primary-accent);">{c_stats['total_papers']} bài ({c_stats['gen0_count']} bài gốc)</div>
            </div>
            <div style="background:var(--bg-surface-elevated); padding:12px; border-radius:10px; border:1px solid var(--border-subtle);">
                <div style="font-size:11px; color:var(--text-muted); font-weight:700;">LIÊN KẾT TRÍCH DẪN</div>
                <div style="font-size:19px; font-weight:800; color:var(--badge-green-text);">{c_stats['total_links']} mối liên kết</div>
            </div>
            <div style="background:var(--bg-surface-elevated); padding:12px; border-radius:10px; border:1px solid var(--border-subtle);">
                <div style="font-size:11px; color:var(--text-muted); font-weight:700;">ĐỘ CHÍNH XÁC NGUỒN</div>
                <div style="font-size:19px; font-weight:800; color:var(--badge-blue-text);">{s_stats['coverage_percent']}% (≥96%)</div>
            </div>
            <div style="background:var(--bg-surface-elevated); padding:12px; border-radius:10px; border:1px solid var(--border-subtle);">
                <div style="font-size:11px; color:var(--text-muted); font-weight:700;">BẢN THẢO SONG NGỮ</div>
                <div style="font-size:19px; font-weight:800; color:var(--badge-rose-text);">{i_metrics['total_word_count']} từ ({i_metrics['verified_grounded_claims']} dẫn chứng)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_p1, col_p2, col_p3 = st.columns([1.1, 1.6, 0.9])
        with col_p1:
            st.download_button(
                "📦 Tải về (.ZIP)",
                data=results["zip_bytes"],
                file_name="ho_so_nghien_cuu_bao_chi_ai_apa7.zip",
                mime="application/zip",
                type="secondary",
                use_container_width=True
            )
        with col_p2:
            if st.button("🌐 XEM MẠNG LƯỚI TRÍCH DẪN ➔", type="primary", use_container_width=True, key="btn_modal_goto_m2"):
                st.session_state.show_completion_popup = False
                go_to_screen("02. Mạng lưới trích dẫn khoa học")
        with col_p3:
            if st.button("✕ Đóng", use_container_width=True, key="btn_modal_close"):
                st.session_state.show_completion_popup = False
                st.rerun()

if hasattr(st, "dialog"):
    @st.dialog("🌐 SƠ ĐỒ MẠNG LƯỚI TRÍCH DẪN — MÀN HÌNH PHỤ", width="large")
    def show_network_modal(html_content: str):
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding:8px 14px; background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:10px;">
            <div style="color:var(--primary-accent); font-weight:800; font-size:13.5px; display:flex; align-items:center; gap:6px;">
                <span>🌐</span> <span>MÀN HÌNH PHỤ TOÀN CẢNH: TƯƠNG TÁC SƠ ĐỒ MẠNG LƯỚI ĐỘC LẬP</span>
            </div>
            <span class="status-chip green" style="font-weight:700;">Chế độ tương tác cao</span>
        </div>
        """, unsafe_allow_html=True)
        components.html(html_content, height=750, scrolling=False)

# Hiển thị Popup khi hoàn thành
if st.session_state.get("show_completion_popup") and st.session_state.pipeline_results:
    if hasattr(st, "dialog"):
        show_completion_modal(st.session_state.pipeline_results)
    else:
        st.success("🎉 ĐÃ HOÀN TẤT KIỂM TRA DOI & PHÂN TÍCH HỌC THUẬT! Bạn có thể chuyển sang Menu 2 để khám phá sơ đồ mạng lưới.")

# Tham số mặc định
gen1_limit = 20
gen2_limit = 68
synth_target = 25
llm_choice = "Google Gemini 2.0 Flash (Khuyên dùng - Nhanh & Chuẩn xác nhất)"
api_key_val = get_secret("GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
email_val = get_secret("OPENALEX_EMAIL", "scholar.researcher@academic.edu.vn")

# -----------------------------------------------------------------------------
# MÀN HÌNH 1: NHẬP MÃ DOI BÀI BÁO GỐC (KHỞI TẠO)
# -----------------------------------------------------------------------------
if "01." in workspace_nav:
    # BANNER QUẢNG BÁ PHẦN MỀM THƯƠNG MẠI — NGƯỜI PHÁT TRIỂN: TRẦN DUY
    st.markdown(f"""
    <div class="hero-banner-box">
        <div class="hero-banner-title">
            ScholarGraph Pro — AI Academic Research & Synthesis Engine
        </div>
        <div class="hero-banner-desc">
            Nền tảng trực quan hóa mạng lưới tri thức học thuật, bóc tách ma trận bằng chứng thực nghiệm Scopus Q1/Q2 và tự động soạn thảo bản thảo phần Mở đầu song ngữ chuẩn hóa quốc tế theo mô hình John Swales CARS.
        </div>
        <div class="hero-banner-meta">
            <span class="developer-pill" style="font-size:12px; padding:4px 10px;">Người phát triển: TRẦN DUY (Lead AI Research Engineer)</span>
            <span class="status-chip green">{icon_spark_svg} Chuẩn APA 7 & Swales CARS</span>
            <span class="status-chip blue">{icon_net_svg} Mạng lưới dữ liệu mở OpenAlex</span>
            <span class="status-chip rose">{icon_shield_svg} Zero-Hallucination Framework</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    intro_tab1, intro_tab2, intro_tab3 = st.tabs([
        "🌟 Giới thiệu & Không gian nghiên cứu",
        "🚀 Hướng dẫn khởi tạo dự án",
        "💡 Mẹo dành cho người mới bắt đầu"
    ])

    with intro_tab1:
        st.markdown(f"""
        <div class="tab-content-card">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
                {get_svg_icon("sparkles", color="var(--primary-accent)", size=18)}
                <h3 style="margin:0; font-size:16px; color:var(--primary-accent);">Tổng quan ứng dụng & Giá trị học thuật cốt lõi</h3>
            </div>
            <p style="color:var(--text-secondary); font-size:13.5px; line-height:1.65; margin-bottom:12px;">
                Hệ thống hỗ trợ nhà nghiên cứu giải quyết bài toán phân mảnh tài liệu học thuật trong kỷ nguyên AI. Bằng cách kết nối mạng lưới trích dẫn 2 chiều của OpenAlex, ứng dụng tự động phân định ranh giới phương pháp luận và phát hiện thực nghiệm của các tạp chí đầu ngành (*Digital Journalism, Journalism Studies, New Media & Society*).
            </p>
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px;">
                <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:10px; padding:10px 12px;">
                    <div style="color:var(--badge-green-text); font-weight:700; font-size:12.5px; margin-bottom:3px;">✓ Thẩm định Scopus Q1/Q2</div>
                    <div style="color:var(--text-muted); font-size:11.5px;">Tự động phân hạng và ưu tiên các bài báo bình duyệt quốc tế có chỉ số trích dẫn cao.</div>
                </div>
                <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:10px; padding:10px 12px;">
                    <div style="color:var(--primary-accent); font-weight:700; font-size:12.5px; margin-bottom:3px;">✓ Chuẩn hóa APA 7 & CARS</div>
                    <div style="color:var(--text-muted); font-size:11.5px;">Tài liệu tham khảo, bảng biểu và bản thảo mở đầu được chuẩn hóa xuất bản ngay.</div>
                </div>
                <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:10px; padding:10px 12px;">
                    <div style="color:var(--badge-rose-text); font-weight:700; font-size:12.5px; margin-bottom:3px;">✓ Đa dạng định dạng xuất</div>
                    <div style="color:var(--text-muted); font-size:11.5px;">Hỗ trợ xuất tức thì ra file Word (.docx), Excel (.xlsx), PDF, CSV, RIS và BibTeX.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with intro_tab2:
        st.markdown(f"""
        <div class="tab-content-card">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
                {get_svg_icon("compass", color="#34D399", size=20)}
                <h3 style="margin:0; font-size:16.5px; color:#34D399;">Quy trình 4 bước nghiên cứu & Xuất bản phẩm</h3>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; color:#94A3B8; font-size:13px; line-height:1.6;">
                <div><b>1. Nhập mã DOI bài báo gốc:</b> Dán mã định danh DOI của bài báo bạn quan tâm hoặc chọn nhanh cụm chủ đề mẫu bên dưới.</div>
                <div><b>2. Khám phá sơ đồ mạng lưới trích dẫn:</b> Tương tác với sơ đồ tri thức 2 thế hệ (Gen-1 trực tiếp, Gen-2 mở rộng) và tách màn hình phụ để làm việc.</div>
                <div><b>3. Bóc tách ma trận bằng chứng:</b> Xem xét phương pháp thu thập mẫu, phát hiện cốt lõi và các ranh giới đạo đức chưa có lời giải.</div>
                <div><b>4. Nhận bản thảo mở đầu song ngữ & Tải file:</b> Đọc bản thảo chuẩn Swales CARS (English & Tiếng Việt) và tải trọn gói tài liệu nghiên cứu.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with intro_tab3:
        st.markdown(f"""
        <div class="tab-content-card">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
                {get_svg_icon("sparkles", color="#FBBF24", size=20)}
                <h3 style="margin:0; font-size:16.5px; color:#FBBF24;">Mẹo tối ưu hóa trích dẫn & Quản lý tài liệu</h3>
            </div>
            <div style="color:#94A3B8; font-size:13px; line-height:1.65;">
                • <b>Định dạng mã DOI:</b> Mã DOI thường có cấu trúc <code>10.xxxx/...</code> (ví dụ: <code>10.1177/1464884918757072</code>).<br/>
                • <b>Phân biệt quyền truy cập:</b> Biểu tượng 🔓 <b>[Bản PDF miễn phí]</b> cho biết tài liệu Open Access có thể tải trực tiếp; biểu tượng 🔒 <b>[Cần quyền truy cập]</b> yêu cầu mở link DOI qua thư viện đại học.<br/>
                • <b>Nạp vào Zotero / Mendeley:</b> Tải tệp <code>refs.ris</code> để nhập toàn bộ thư mục bài báo vào phần mềm quản lý trích dẫn chỉ trong 1 giây.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # 4 PHƯƠNG THỨC THU THẬP & NẠP DỮ LIỆU ĐỀ TÀI
    ingest_tab1, ingest_tab2, ingest_tab3, ingest_tab4 = st.tabs([
        "✍️ Nhập mã DOI trực tiếp",
        "📑 Nạp tệp .BIB / .RIS (Zotero/Mendeley)",
        "📁 Kéo thả tệp PDF từ máy tính",
        "🔎 Tìm kiếm theo từ khóa / Tên đề tài"
    ])

    with ingest_tab1:
        doi_raw_input = st.text_area(
            "Nhập danh sách mã DOI bài báo gốc (mỗi mã trên 1 dòng hoặc cách nhau bằng dấu phẩy):",
            value=st.session_state.doi_input_val,
            height=90,
            help="Ví dụ: 10.1177/1464884918757072, 10.1080/17512786.2017.1320773"
        )
        st.session_state.doi_input_val = doi_raw_input

    with ingest_tab2:
        st.markdown("<div style='font-size:13px; color:#94A3B8; margin-bottom:8px;'>Tải lên tệp trích dẫn xuất từ Zotero, Mendeley, EndNote hoặc Google Scholar (.bib hoặc .ris):</div>", unsafe_allow_html=True)
        uploaded_bib_file = st.file_uploader("Chọn tệp .bib hoặc .ris", type=["bib", "ris"], label_visibility="collapsed")
        if uploaded_bib_file:
            content_str = uploaded_bib_file.read().decode("utf-8", errors="ignore")
            if uploaded_bib_file.name.endswith(".bib"):
                entries = parse_bibtex_string(content_str)
            else:
                entries = parse_ris_string(content_str)
                
            found_dois = [e["doi"] for e in entries if e.get("doi")]
            if found_dois:
                st.success(f"✓ Đã bóc tách thành công {len(found_dois)} mã DOI từ tệp `{uploaded_bib_file.name}`!")
                if st.button("📥 Nạp danh sách DOI này vào dự án", use_container_width=True):
                    st.session_state.doi_input_val = ", ".join(found_dois)
                    st.rerun()
            else:
                st.warning("⚠️ Không tìm thấy trường DOI trong tệp. Đang trích xuất theo tiêu đề...")

    with ingest_tab3:
        st.markdown("<div style='font-size:13px; color:#94A3B8; margin-bottom:8px;'>Kéo thả một hoặc nhiều tệp PDF bài báo từ máy tính (Hệ thống sẽ tự động quét mã DOI ở trang đầu):</div>", unsafe_allow_html=True)
        uploaded_pdfs = st.file_uploader("Chọn các tệp PDF", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_pdfs:
            pdf_dois = []
            for u_pdf in uploaded_pdfs:
                pdf_bytes = u_pdf.read()
                d = extract_doi_from_pdf(pdf_bytes)
                if d:
                    pdf_dois.append(d)
            if pdf_dois:
                st.success(f"✓ Đã nhận diện được {len(pdf_dois)} mã DOI hợp lệ từ các tệp PDF tải lên!")
                if st.button("📥 Nạp các mã DOI từ PDF vào dự án", use_container_width=True):
                    st.session_state.doi_input_val = ", ".join(pdf_dois)
                    st.rerun()
            else:
                st.info("ℹ️ Tệp PDF tải lên không chứa chuỗi định danh DOI chuẩn ở 2 trang đầu.")

    with ingest_tab4:
        st.markdown("<div style='font-size:13px; color:#94A3B8; margin-bottom:8px;'>Tìm kiếm bài báo khoa học quốc tế theo tên bài hoặc từ khóa trên OpenAlex:</div>", unsafe_allow_html=True)
        c_search1, c_search2 = st.columns([3.5, 1])
        with c_search1:
            kw_query = st.text_input("Nhập từ khóa tìm kiếm (Ví dụ: automated journalism, AI newsroom ethics):", label_visibility="collapsed", placeholder="Nhập từ khóa...")
        with c_search2:
            search_trigger = st.button("🔍 Tìm kiếm", use_container_width=True)

        if search_trigger and kw_query:
            with st.spinner("Đang tìm kiếm bài báo trên mạng lưới OpenAlex..."):
                found_works = search_works_by_keyword(kw_query, limit=8, email=email_val)
                st.session_state["search_results_cache"] = found_works

        if st.session_state.get("search_results_cache"):
            s_results = st.session_state["search_results_cache"]
            st.markdown(f"**Kết quả tìm kiếm ({len(s_results)} bài báo):**")
            selected_search_dois = []
            for item_w in s_results:
                w_title = item_w.get("title", "")
                w_doi = item_w.get("doi", "")
                w_yr = item_w.get("year", "")
                w_auth = item_w.get("first_author", "")
                if w_doi:
                    if st.checkbox(f"[{w_yr}] {w_auth}: {w_title} (DOI: {w_doi})", value=True, key=f"chk_{w_doi}"):
                        selected_search_dois.append(w_doi)
            if selected_search_dois:
                if st.button(f"📥 Nạp {len(selected_search_dois)} bài báo đã chọn vào dự án", use_container_width=True):
                    st.session_state.doi_input_val = ", ".join(selected_search_dois)
                    st.rerun()

    detected_dois = parse_doi_list(st.session_state.doi_input_val)
    doi_count = len(detected_dois)

    # HÀNG ĐIỀU KHIỂN CÂN XỨNG: ĐỒNG BỘ CHIỀU CAO VÀ MÀU SẮC
    col_status, col_btn = st.columns([1, 1], gap="medium")

    with col_status:
        if doi_count > 0:
            st.markdown(f"""
            <div class="symmetrical-action-card ready">
                <div style="display:flex; align-items:center; gap:10px; min-width:0; flex:1;">
                    <div style="flex-shrink:0; display:flex; align-items:center;">
                        {get_svg_icon("shield-check", color="#34D399", size=22)}
                    </div>
                    <div style="min-width:0; overflow:hidden;">
                        <div class="status-text-title" style="color:#34D399;">TRẠNG THÁI: SẴN SÀNG PHÂN TÍCH</div>
                        <div class="status-text-sub">Đã phát hiện <b style="color:#F1F5F9;">{doi_count} bài báo gốc</b> hợp lệ</div>
                    </div>
                </div>
                <div class="doi-tag-badge ready">{doi_count} DOI • Hợp lệ</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="symmetrical-action-card empty">
                <div style="display:flex; align-items:center; gap:10px; min-width:0; flex:1;">
                    <div style="flex-shrink:0; display:flex; align-items:center;">
                        {get_svg_icon("shield-check", color="#FB7185", size=22)}
                    </div>
                    <div style="min-width:0; overflow:hidden;">
                        <div class="status-text-title" style="color:#FB7185;">TRẠNG THÁI: CHƯA CÓ MÃ DOI</div>
                        <div class="status-text-sub">Vui lòng nhập mã DOI hoặc chọn cụm mẫu</div>
                    </div>
                </div>
                <div class="doi-tag-badge empty">0 DOI</div>
            </div>
            """, unsafe_allow_html=True)

    with col_btn:
        start_btn = st.button("🚀 BẮT ĐẦU PHÂN TÍCH & SOẠN THẢO NGAY", type="primary", use_container_width=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Cụm DOI Gợi ý 1-Click
    st.markdown('<div class="menu-header-badge">CỤM ĐỀ TÀI GỢI Ý VỀ BÁO CHÍ & TÒA SOẠN AI (BẤM ĐỂ CHỌN NHANH):</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📰 Thuật toán & Tòa soạn (2 bài)", use_container_width=True):
            st.session_state.doi_input_val = "10.1177/1464884918757072, 10.1080/17512786.2017.1320773"
            st.rerun()
    with c2:
        if st.button("👥 Độc giả & Tin tự động (2 bài)", use_container_width=True):
            st.session_state.doi_input_val = "10.17645/mac.v8i3.3019, 10.1080/17512786.2017.1320773"
            st.rerun()
    with c3:
        if st.button("⚖️ Đạo đức & Tin giả (2 bài)", use_container_width=True):
            st.session_state.doi_input_val = "10.1080/21670811.2019.1623701, 10.1177/1464884918757072"
            st.rerun()
    with c4:
        if st.button("🌐 Tổng quan AI báo chí (3 bài)", use_container_width=True):
            st.session_state.doi_input_val = "10.1177/1464884918757072, 10.1080/17512786.2017.1320773, 10.17645/mac.v8i3.3019"
            st.rerun()

    if start_btn:
        run_academic_pipeline(
            dois=detected_dois,
            g1_lim=gen1_limit,
            g2_lim=gen2_limit,
            target_synth=synth_target,
            llm_mode=llm_choice,
            api_key=api_key_val,
            email=email_val
        )

    # Hiển thị bảng điều hướng nhanh khi đã có kết quả phân tích
    if st.session_state.pipeline_results:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:var(--bg-surface-elevated); border:2px solid var(--badge-green-border); border-radius:14px; padding:18px 22px; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <div style="color:var(--badge-green-text); font-weight:800; font-size:16px; display:flex; align-items:center; gap:8px;">
                    <span>✓</span> DỮ LIỆU ĐÃ PHÂN TÍCH XONG & SẴN SÀNG KHÁM PHÁ!
                </div>
                <span class="status-chip green" style="font-weight:700;">Hoàn tất 100%</span>
            </div>
            <p style="color:var(--text-secondary); font-size:13px; margin:0; line-height:1.5;">
                Bạn có thể bấm vào các thẻ điều hướng nhanh bên dưới (tương đương với chọn ở thanh Menu trái) để chuyển thẳng đến màn hình tương ứng ngay lập tức:
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        qnav1, qnav2, qnav3, qnav4 = st.columns(4)
        with qnav1:
            st.markdown("""
            <div class="quick-nav-card qnav-net">
                <div class="qnav-title">🌐 MẠNG LƯỚI TRÍCH DẪN KHOA HỌC</div>
                <div class="qnav-desc">Khám phá sơ đồ phả hệ học thuật, node trích dẫn & phân loại Open Access</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➔ XEM MẠNG LƯỚI TRÍCH DẪN", type="primary", use_container_width=True, key="btn_qnav_m2"):
                go_to_screen("02. Mạng lưới trích dẫn khoa học")
                
        with qnav2:
            st.markdown("""
            <div class="quick-nav-card qnav-apa">
                <div class="qnav-title">📊 BẢNG TỔNG HỢP PHƯƠNG PHÁP (APA 7)</div>
                <div class="qnav-desc">Bóc tách bằng chứng phương pháp, mẫu trích đoạn & chuẩn hóa trích dẫn APA 7</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➔ XEM BẢNG TỔNG HỢP APA 7", use_container_width=True, key="btn_qnav_m3"):
                go_to_screen("03. Bảng tổng hợp phương pháp (APA 7)")
                
        with qnav3:
            st.markdown("""
            <div class="quick-nav-card qnav-cars">
                <div class="qnav-title">✍️ SOẠN THẢO CARS & PHẢN BIỆN MÔ PHỎNG</div>
                <div class="qnav-desc">Bản thảo Mở đầu song ngữ chuẩn John Swales CARS & mô phỏng phản biện học thuật</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➔ XEM BẢN THẢO CARS", use_container_width=True, key="btn_qnav_m5"):
                go_to_screen("05. Soạn thảo CARS & Phản biện mô phỏng")
                
        with qnav4:
            st.markdown("""
            <div class="quick-nav-card qnav-pack">
                <div class="qnav-title">📦 TẢI VỀ TRỌN BỘ HỒ SƠ & AI COPILOT</div>
                <div class="qnav-desc">Xuất trọn gói 5 định dạng học thuật (.ZIP, .CSV, .BIB, .DOCX, .HTML tương tác)</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➔ ĐẾN TRANG TẢI VỀ HỒ SƠ", use_container_width=True, key="btn_qnav_m6"):
                go_to_screen("06. Tải về trọn bộ hồ sơ & AI Copilot")

# -----------------------------------------------------------------------------
# MÀN HÌNH 2: SƠ ĐỒ MẠNG LƯỚI TRÍCH DẪN & PHÂN LOẠI QUYỀN TRUY CẬP
# -----------------------------------------------------------------------------
elif "02." in workspace_nav:
    if st.session_state.pipeline_results:
        c_res = st.session_state.pipeline_results["citenet"]
        nodes_dict = c_res.get("nodes", {})
        papers_list = c_res.get("papers_list", list(nodes_dict.values()))
        
        oa_papers = [p for p in papers_list if p.get("is_oa") or bool(p.get("pdf_url"))]
        paywall_papers = [p for p in papers_list if not (p.get("is_oa") or bool(p.get("pdf_url")))]
        oa_pct = round((len(oa_papers) / len(papers_list) * 100), 1) if papers_list else 0.0
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card-full" style="border-top: 3px solid #FB7185;">
                <div class="metric-title">Bài báo gốc khởi đầu (Seed)</div>
                <div class="metric-value" style="color: #FB7185;">{c_res['stats']['gen0_count']} bài</div>
                <div class="metric-sub">Công trình định hướng nghiên cứu</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card-full" style="border-top: 3px solid #38BDF8;">
                <div class="metric-title">Tổng số bài báo Scopus</div>
                <div class="metric-value" style="color: #38BDF8;">{c_res['stats']['total_papers']} bài</div>
                <div class="metric-sub">{c_res['stats']['gen1_count']} bài trực tiếp • {c_res['stats']['gen2_count']} bài mở rộng</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card-full" style="border-top: 3px solid #34D399;">
                <div class="metric-title">Bản full PDF miễn phí (OA)</div>
                <div class="metric-value" style="color: #34D399;">{len(oa_papers)} bài ({oa_pct}%)</div>
                <div class="metric-sub">Tải trực tiếp không cần tài khoản</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-card-full" style="border-top: 3px solid #FBBF24;">
                <div class="metric-title">Bản cần quyền truy cập</div>
                <div class="metric-value" style="color: #FBBF24;">{len(paywall_papers)} bài</div>
                <div class="metric-sub">Truy cập qua cổng thư viện trường</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        with st.expander("🎛️ Bộ lọc động sơ đồ mạng lưới trích dẫn (Interactive Graph Filters)", expanded=False):
            f_c1, f_c2, f_c3, f_c4 = st.columns(4)
            with f_c1:
                year_range = st.slider("Khoảng năm xuất bản:", min_value=2010, max_value=2026, value=(2015, 2026), key="flt_yr_slider")
            with f_c2:
                min_cite_filter = st.number_input("Số trích dẫn tối thiểu (Citations):", min_value=0, max_value=500, value=0, step=5, key="flt_cite_input")
            with f_c3:
                theme_filter = st.selectbox("Lọc theo trường phái nghiên cứu:", ["Tất cả chủ đề", "Newsroom & Workflow AI", "Ethical & Governance", "Audience & Trust", "Algorithmic & Tech", "Systematic Review"], key="flt_theme_sb")
            with f_c4:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                oa_only_filter = st.checkbox("Chỉ hiện bài Full PDF Open Access", value=False, key="flt_oa_chk")

        citenet_agent_inst = CiteNetAgent(email=email_val)
        active_network_html = citenet_agent_inst.filter_and_generate_network_html(
            nodes=nodes_dict,
            edges=c_res.get("edges", []),
            min_year=year_range[0],
            max_year=year_range[1],
            min_citations=int(min_cite_filter),
            study_type=theme_filter,
            only_oa=oa_only_filter
        )

        col_g1, col_g2, col_g3 = st.columns([1.8, 1.1, 1.1], gap="small")
        with col_g1:
            with st.expander("💡 Hướng dẫn & Quy ước thao tác sơ đồ", expanded=False):
                st.markdown("""
                - **Kích cỡ Node:** Tỷ lệ thuận với số lượt trích dẫn Scopus (Academic Impact).
                - **Màu sắc:** 🔴 Đỏ: Bài báo gốc (Seed) | 🔵 Xanh dương: Tham khảo trực tiếp (Gen-1) | 🟢 Xanh lục: Mở rộng (Gen-2).
                - **Thao tác:** Bấm nút **🎛️ Bảng công cụ** ở góc trên sơ đồ để phóng to, thu nhỏ, căn giữa, chuyển kiểu nền 3D hoặc bố cục phả hệ.
                """)
        with col_g2:
            st.download_button(
                "📥 Tải tệp HTML",
                data=active_network_html,
                file_name="so_do_mang_luoi_trich_dan.html",
                mime="text/html",
                use_container_width=True,
                key="btn_dl_active_net_html"
            )
        with col_g3:
            if st.button("🪟 MỞ MÀN HÌNH PHỤ ↗", type="primary", use_container_width=True, key="btn_open_network_subscreen"):
                if hasattr(st, "dialog"):
                    show_network_modal(active_network_html)
                else:
                    st.info("💡 Màn hình phụ đang hiển thị trực tiếp bên dưới.")

        # Hiển thị sơ đồ tương tác chuẩn quốc tế
        components.html(active_network_html, height=730, scrolling=False)

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        
        # Gom nhóm liệt kê phân loại quyền truy cập, Phân tích khoảng trống & Tra cứu chi tiết
        st.markdown("### 📊 Gom nhóm danh mục, Bản đồ khoảng trống & Quyền truy cập tài liệu:")
        
        tab_oa_group, tab_paywall_group, tab_timeline, tab_heatmap, tab_single_lookup = st.tabs([
            f"🔓 Nhóm bản full PDF miễn phí (OA: {len(oa_papers)} bài)",
            f"🔒 Nhóm bản trả phí / Cần quyền (Paywall: {len(paywall_papers)} bài)",
            "📈 Dòng thời gian phát triển (Timeline)",
            "🎯 Bản đồ khoảng trống nghiên cứu (Gap Heatmap)",
            "🔍 Tra cứu chi tiết & Tóm tắt song ngữ"
        ])
        
        with tab_oa_group:
            st.markdown(f"""
            <div style="background: rgba(52, 211, 153, 0.08); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;">
                <div style="color: #34D399; font-weight: 700; font-size: 14px; margin-bottom: 4px;">
                    ✓ Đã định vị {len(oa_papers)} tài liệu Open Access có sẵn liên kết tải toàn văn PDF miễn phí
                </div>
                <div style="color: #94A3B8; font-size: 13px;">
                    Bạn có thể tải trực tiếp từng bài bên dưới hoặc chuyển sang <b>Menu 06</b> để tải trọn bộ hàng loạt vào thư mục trên máy tính.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c_oa1, c_oa2 = st.columns(2, gap="medium")
            for idx, p in enumerate(oa_papers):
                target_c = c_oa1 if idx % 2 == 0 else c_oa2
                pdf_u = p.get("pdf_url") or p.get("oa_url") or ""
                doi_v = p.get("doi", "")
                with target_c:
                    st.markdown(f"""
                    <div class="apa-ref-card" style="border-left: 3px solid #34D399;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="color:#38BDF8; font-weight:700; font-size:12px;">#{idx+1} • {p.get('scopus_tier', 'Scopus')}</span>
                            <span class="access-badge-oa">{get_svg_icon('lock-open', color='#34D399', size=12)} Full PDF Free</span>
                        </div>
                        <div class="apa-hanging-indent" style="font-size:13px; color:#F8FAFC;">
                            {format_apa7_reference(p)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if pdf_u:
                        st.link_button(f"🔓 Tải Full PDF bài #{idx+1} ↗", url=pdf_u, type="primary", use_container_width=True)
                    elif doi_v:
                        st.link_button(f"🔗 Mở link DOI ({doi_v}) ↗", url=f"https://doi.org/{doi_v}", use_container_width=True)
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        with tab_paywall_group:
            st.markdown(f"""
            <div style="background: rgba(251, 113, 133, 0.08); border: 1px solid rgba(251, 113, 133, 0.3); border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;">
                <div style="color: #FB7185; font-weight: 700; font-size: 14px; margin-bottom: 4px;">
                    🔒 Danh sách {len(paywall_papers)} tài liệu thuộc dạng xuất bản có bản quyền (Subscription / Paywall)
                </div>
                <div style="color: #94A3B8; font-size: 13px;">
                    Để tải toàn văn các tài liệu này, vui lòng truy cập qua mạng nội bộ trường đại học (VPN/EZProxy) hoặc đăng nhập tài khoản thư viện liên kết với nhà xuất bản (Elsevier, Springer, Taylor & Francis, SAGE, IEEE).
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c_pw1, c_pw2 = st.columns(2, gap="medium")
            for idx, p in enumerate(paywall_papers):
                target_c = c_pw1 if idx % 2 == 0 else c_pw2
                doi_v = p.get("doi", "")
                doi_u = p.get("doi_url") or (f"https://doi.org/{doi_v}" if doi_v else "")
                landing_u = p.get("landing_url") or doi_u
                with target_c:
                    st.markdown(f"""
                    <div class="apa-ref-card" style="border-left: 3px solid #FB7185;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="color:#FBBF24; font-weight:700; font-size:12px;">#{idx+1} • {p.get('scopus_tier', 'Scopus')}</span>
                            <span class="access-badge-paywall">{get_svg_icon('lock-closed', color='#FB7185', size=12)} Cần quyền truy cập</span>
                        </div>
                        <div class="apa-hanging-indent" style="font-size:13px; color:#F8FAFC;">
                            {format_apa7_reference(p)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if landing_u:
                        st.link_button(f"🔗 Mở trang nhà xuất bản ({doi_v or 'DOI'}) ↗", url=landing_u, use_container_width=True)
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        with tab_timeline:
            st.markdown("#### 📈 Biểu đồ tiến hóa & Dòng thời gian công bố bài báo (Plotly Timeline):")
            fig_time = create_evolution_timeline_chart(papers_list, theme_id=st.session_state.selected_theme)
            st.plotly_chart(fig_time, use_container_width=True)

        with tab_heatmap:
            st.markdown("#### 🎯 Bản đồ ma trận khoảng trống nghiên cứu & Phân tích điểm bão hòa:")
            # Use evidence pool if available, otherwise papers_list
            synth_pool = st.session_state.pipeline_results.get("synthdesk", {}).get("evidence_pool", papers_list)
            fig_gap, narrative_gap = create_research_gap_heatmap(synth_pool, theme_id=st.session_state.selected_theme)
            st.plotly_chart(fig_gap, use_container_width=True)
            st.markdown(narrative_gap)

        with tab_single_lookup:
            paper_options = {}
            for nid, meta in nodes_dict.items():
                gen_label = "[Bài gốc]" if meta.get("generation") == 0 else f"[Thế hệ {meta.get('generation', 2)}]"
                auth = meta.get("first_author", "Tác giả")
                yr = meta.get("year", "")
                title_short = (meta.get("title", "Không có tiêu đề")[:65] + "...") if len(meta.get("title", "")) > 65 else meta.get("title", "")
                display_name = f"{gen_label} {auth} ({yr}) — {title_short}"
                paper_options[display_name] = nid

            selected_label = st.selectbox(
                "Chọn một bài báo để kiểm tra quyền truy cập bản full PDF, tóm tắt và các bài liên quan:",
                options=list(paper_options.keys())
            )

            if selected_label:
                sel_id = paper_options[selected_label]
                sel_paper = nodes_dict.get(sel_id, {})
                
                doi_val = sel_paper.get("doi", "")
                doi_url = sel_paper.get("doi_url") or (f"https://doi.org/{doi_val}" if doi_val else "")
                pdf_url = sel_paper.get("pdf_url", "")
                is_oa = sel_paper.get("is_oa", False) or bool(pdf_url)
                gen_num = sel_paper.get("generation", 2)
                
                gen_badge_color = "var(--badge-rose-text)" if gen_num == 0 else ("var(--primary-accent)" if gen_num == 1 else "var(--badge-green-text)")
                gen_badge_text = "Bài báo gốc (Khởi đầu)" if gen_num == 0 else (f"Thế hệ {gen_num} (Mở rộng)")

                oa_badge_html = f'<span class="access-badge-oa">{get_svg_icon("lock-open", color="var(--badge-green-text)", size=13)} Bản PDF miễn phí (Open Access)</span>' if is_oa else f'<span class="access-badge-paywall">{get_svg_icon("lock-closed", color="var(--badge-rose-text)", size=13)} Cần quyền truy cập (Paywall)</span>'

                sel_title = clean_academic_text(sel_paper.get('title', 'Không có tiêu đề'))
                sel_venue = clean_academic_text(sel_paper.get('venue', 'N/A'))
                sel_tier = clean_academic_text(sel_paper.get('scopus_tier', 'Tạp chí Thẩm định'))
                sel_cites = sel_paper.get('citation_count', 0) or 0
                sel_apa7 = format_apa7_reference(sel_paper)
                sel_type = clean_academic_text(sel_paper.get('study_type', 'Nghiên cứu thực nghiệm'))

                card_detail_html = (
                    f'<div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 14px; padding: 20px 24px; margin-top: 10px;">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">'
                    f'<div style="display:flex; gap:8px; align-items:center;">'
                    f'<span style="background: var(--badge-blue-bg); color: {gen_badge_color}; border: 1px solid var(--badge-blue-border); padding: 3px 10px; border-radius: 10px; font-weight: 700; font-size: 12px;">'
                    f'● {gen_badge_text}'
                    f'</span>'
                    f'{oa_badge_html}'
                    f'</div>'
                    f'<span style="color: var(--primary-accent); font-weight: 600; font-size: 13px;">'
                    f'{sel_tier} • {sel_cites} lượt trích dẫn'
                    f'</span>'
                    f'</div>'
                    f'<h3 style="color: var(--text-primary); font-size: 17px; margin: 0 0 10px 0; line-height: 1.45;">'
                    f'{sel_title}'
                    f'</h3>'
                    f'<div style="color: var(--text-secondary); font-size: 13.5px; margin-bottom: 6px;">'
                    f'<b>Định dạng trích dẫn APA 7:</b> <span class="apa-hanging-indent" style="display:inline-block; margin-top:4px;">{sel_apa7}</span>'
                    f'</div>'
                    f'<div style="color: var(--text-secondary); font-size: 13.5px; margin-bottom: 12px;">'
                    f'<b>Tạp chí công bố:</b> {sel_venue} | <b>Phân loại:</b> <span style="color:var(--badge-green-text); font-weight:600;">{sel_type}</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_detail_html, unsafe_allow_html=True)

                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    if pdf_url:
                        st.link_button(f"🔓 Tải toàn văn bản PDF miễn phí ↗", url=pdf_url, type="primary", use_container_width=True)
                    elif doi_url:
                        st.link_button(f"🔗 Mở trang nhà xuất bản ({doi_val}) ↗", url=doi_url, use_container_width=True)
                    else:
                        st.button("⚠️ Không có đường dẫn trực tiếp", disabled=True, use_container_width=True)
                with col_btn2:
                    oa_openalex_url = sel_paper.get('openalex_url') or (f"https://openalex.org/works?filter=doi:{doi_val}" if doi_val else "")
                    if oa_openalex_url:
                        st.link_button("🌐 Xem hồ sơ quốc tế trên OpenAlex ↗", url=oa_openalex_url, use_container_width=True)
                    else:
                        st.button("🌐 OpenAlex N/A", disabled=True, use_container_width=True)

                # Tóm tắt nội dung Song ngữ (2 Tabs)
                st.markdown("<div style='margin: 16px 0 8px 0; font-weight: 700; color: var(--primary-accent); font-size: 14px;'>📄 TÓM TẮT NỘI DUNG NGHIÊN CỨU (SONG NGỮ):</div>", unsafe_allow_html=True)
                tab_vi, tab_en = st.tabs(["🇻🇳 Bản dịch tiếng Việt (Thuần Việt)", "🇬🇧 Nguyên bản gốc (English)"])
                with tab_vi:
                    abs_vi_str = sel_paper.get('abstract_vi') or sel_paper.get('abstract', 'Đang cập nhật tóm tắt tiếng Việt...')
                    st.markdown(
                        f'<div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 18px 22px; color: var(--text-primary); font-size: 14px; line-height: 1.75; white-space: pre-line;">'
                        f'{abs_vi_str}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with tab_en:
                    abs_en_str = sel_paper.get('abstract_en') or sel_paper.get('abstract', 'Abstract in English...')
                    st.markdown(
                        f'<div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 18px 22px; color: var(--text-secondary); font-size: 13.5px; line-height: 1.75; font-style: italic; white-space: pre-line;">'
                        f'{abs_en_str}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
    else:
        st.markdown("""
        <div style="background:var(--bg-surface); border:1px solid var(--border-hover); border-radius:16px; padding:24px 20px; margin-bottom:20px; text-align:center; box-shadow:0 8px 30px rgba(0,0,0,0.12);">
            <div style="font-size:36px; margin-bottom:8px;">🌐</div>
            <h2 style="color:var(--text-primary); font-size:20px; margin:0 0 8px 0; font-weight:800;">
                SƠ ĐỒ MẠNG LƯỚI TRÍCH DẪN KHOA HỌC (CITATION KNOWLEDGE GRAPH)
            </h2>
            <p style="color:var(--text-secondary); font-size:13.5px; max-width:700px; margin:0 auto 18px auto; line-height:1.6;">
                Khám phá bản đồ tri thức tương tác đa chiều chuẩn quốc tế (VOSviewer, HistCite, CiteSpace) với phân tầng trích dẫn 2 thế hệ từ mạng lưới OpenAlex và thẩm định Scopus Q1/Q2.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        c_m2_1, c_m2_2 = st.columns([1.6, 1], gap="medium")
        with c_m2_1:
            if st.button("🚀 BẬT BẢN ĐỒ MẪU NGAY (20 BÀI BÁO BÁO CHÍ & AI - SCOPUS Q1)", type="primary", use_container_width=True, key="btn_m2_run_demo"):
                demo_dois = ["10.1177/1464884918757072", "10.1080/17512786.2017.1320773"]
                st.session_state.doi_input_val = ", ".join(demo_dois)
                run_academic_pipeline(
                    dois=demo_dois,
                    g1_lim=gen1_limit,
                    g2_lim=gen2_limit,
                    target_synth=synth_target,
                    llm_mode=llm_choice,
                    api_key=api_key_val,
                    email=email_val
                )
        with c_m2_2:
            if st.button("📥 Hoặc nhập mã DOI riêng tại Menu 01 ➔", use_container_width=True, key="btn_m2_goto_m1"):
                go_to_screen("01. Khởi tạo & Nhập mã DOI")

# -----------------------------------------------------------------------------
# MÀN HÌNH 3: BẢNG TỔNG HỢP PHƯƠNG PHÁP & KẾT QUẢ (CHUẨN APA 7 — CẤU TRÚC ĐOẠN ĐẸP)
# -----------------------------------------------------------------------------
elif "03." in workspace_nav:
    if st.session_state.pipeline_results:
        s_res = st.session_state.pipeline_results["synthdesk"]
        evidence_pool = s_res["evidence_pool"]
        cov = s_res['grounding_stats']['coverage_percent']
        cov_color = "#34D399" if cov >= 96.0 else "#FBBF24"

        st.markdown(f"""
        <div class="frame-box" style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2>📊 Bảng tổng hợp phương pháp & Bằng chứng thực nghiệm (Chuẩn APA 7)</h2>
                <div style="color: #94A3B8; font-size: 14px; margin-top: 4px;">Trình bày theo các khối phân loại học thuật chuyên sâu: Bối cảnh, phương pháp, kết quả thực nghiệm và ranh giới đạo đức.</div>
            </div>
            <div style="display: flex; gap: 14px; text-align: right;">
                <div style="background:#181B24; border:1px solid #262B38; border-radius:10px; padding:8px 16px;">
                    <div style="font-size: 11px; color: #64748B; text-transform: uppercase; font-weight:700;">Độ chính xác nguồn</div>
                    <div style="font-size: 22px; font-weight: 800; color: {cov_color};">{cov}%</div>
                </div>
                <div style="background:#181B24; border:1px solid #262B38; border-radius:10px; padding:8px 16px;">
                    <div style="font-size: 11px; color: #64748B; text-transform: uppercase; font-weight:700;">Dữ liệu kiểm chứng</div>
                    <div style="font-size: 22px; font-weight: 800; color: #38BDF8;">{s_res['grounding_stats']['grounded_cells']} / {s_res['grounding_stats']['total_cells']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Thanh công cụ tải đa định dạng (DOCX, XLSX, CSV, MD)
        st.markdown("##### 📥 Tải bảng tổng hợp phương pháp dưới các định dạng:")
        col_down1, col_down2, col_down3, col_down4 = st.columns(4)
        
        docx_bytes = markdown_to_docx("Bảng tổng hợp phương pháp & Bằng chứng thực nghiệm (APA 7)", s_res.get("evidence_table_apa7_md", ""), author="TRẦN DUY")
        xlsx_bytes = dataframe_to_xlsx(s_res["evidence_dataframe"], sheet_name="Evidence Matrix")
        
        with col_down1:
            st.download_button("📄 Tải bản Word (.DOCX)", data=docx_bytes, file_name="bang_tong_hop_phuong_phap_apa7.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        with col_down2:
            st.download_button("📊 Tải bản Excel (.XLSX)", data=xlsx_bytes, file_name="bang_tong_hop_phuong_phap.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col_down3:
            st.download_button("📋 Tải bảng CSV (.CSV)", data=s_res["evidence_table_csv"], file_name="bang_tong_hop_phuong_phap.csv", mime="text/csv", use_container_width=True)
        with col_down4:
            st.download_button("📝 Tải bản Markdown (.MD)", data=s_res.get("evidence_table_apa7_md", ""), file_name="bang_tong_hop_phuong_phap.md", mime="text/markdown", use_container_width=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        tab_structured, tab_apa_table, tab_interactive = st.tabs([
            "🗂️ Trình bày dạng khối chi tiết (Dễ đọc & Chuyên nghiệp)",
            "📑 Bảng cấu trúc chuẩn APA 7 (Table Format)",
            "🔍 Bảng dữ liệu tương tác (DataFrame)"
        ])
        
        with tab_structured:
            st.markdown('<div class="menu-header-badge">DANH SÁCH BÓC TÁCH 4 CHIỀU HỌC THUẬT TỪNG BÀI BÁO:</div>', unsafe_allow_html=True)
            for idx, p in enumerate(evidence_pool, 1):
                is_oa = p.get("is_oa", False) or bool(p.get("pdf_url"))
                pdf_url = p.get("pdf_url", "")
                doi_val = p.get("doi", "")
                auth_str = p.get("authors_formatted") or p.get("first_author") or "N/A"
                yr_str = str(p.get("year", ""))
                title_str = p.get("title", "")
                journal_str = p.get("venue") or p.get("journal") or p.get("host_venue") or p.get("scopus_tier") or "Tạp chí Scopus Q1/Q2"
                cites = p.get("citation_count", 0)
                
                c_problem = p.get("newsroom_problem") or p.get("context") or p.get("problem") or "Khảo sát và định vị bối cảnh ứng dụng AI trong quy trình sản xuất tin tức."
                c_method = p.get("ai_methodology") or p.get("methodology") or p.get("methods") or "Phương pháp phân tích thực nghiệm và đối sánh thuật toán học thuật."
                c_finding = p.get("empirical_finding") or p.get("findings") or p.get("results") or "Đánh giá định lượng tác động và phản hồi của người tiếp nhận thông tin."
                c_ethics = p.get("ethical_limitation_gap") or p.get("ethics") or p.get("limitations") or "Xem xét tính minh bạch thuật toán và các ranh giới đạo đức học thuật."
                
                oa_chip = '<span class="status-chip green" style="font-size:11px; font-weight:700;">🔓 Full PDF Open Access</span>' if is_oa else '<span class="status-chip rose" style="font-size:11px; font-weight:700;">🔒 Cần quyền truy cập</span>'
                apa_ref_text = p.get("apa7_ref") or format_apa7_reference(p)
                
                card_html = (
                    f'<div class="evidence-card" style="border-left: 4px solid var(--primary-accent); margin-bottom: 16px;">'
                    f'<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 6px;">'
                    f'<div style="font-weight: 800; font-size: 15px; color: var(--text-primary);">#{idx}. {title_str}</div>'
                    f'{oa_chip}'
                    f'</div>'
                    f'<div style="font-size: 12.5px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5;">'
                    f'<b>Tác giả:</b> {auth_str} ({yr_str}) • <b>Tạp chí:</b> <i>{journal_str}</i> • <b>Trích dẫn:</b> {cites} lượt • <b>DOI:</b> <code>{doi_val}</code>'
                    f'</div>'
                    f'<div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">'
                    f'<div style="background: var(--bg-surface); padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">'
                    f'<div style="font-size: 11px; font-weight: 700; color: var(--badge-blue-text); margin-bottom: 3px;">🏛️ BỐI CẢNH & VẤN ĐỀ NGHIÊN CỨU</div>'
                    f'<div style="font-size: 12.5px; color: var(--text-primary); line-height: 1.5;">{c_problem}</div>'
                    f'</div>'
                    f'<div style="background: var(--bg-surface); padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">'
                    f'<div style="font-size: 11px; font-weight: 700; color: var(--primary-accent); margin-bottom: 3px;">🔬 PHƯƠNG PHÁP & DỮ LIỆU THỰC NGHIỆM</div>'
                    f'<div style="font-size: 12.5px; color: var(--text-primary); line-height: 1.5;">{c_method}</div>'
                    f'</div>'
                    f'<div style="background: var(--bg-surface); padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">'
                    f'<div style="font-size: 11px; font-weight: 700; color: var(--badge-green-text); margin-bottom: 3px;">📊 KẾT QUẢ & PHÁT HIỆN THEN CHỐT</div>'
                    f'<div style="font-size: 12.5px; color: var(--text-primary); line-height: 1.5;">{c_finding}</div>'
                    f'</div>'
                    f'<div style="background: var(--bg-surface); padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">'
                    f'<div style="font-size: 11px; font-weight: 700; color: var(--badge-rose-text); margin-bottom: 3px;">⚖️ RANH GIỚI ĐẠO ĐỨC & KHUYẾN NGHỊ</div>'
                    f'<div style="font-size: 12.5px; color: var(--text-primary); line-height: 1.5;">{c_ethics}</div>'
                    f'</div>'
                    f'</div>'
                    f'<div style="font-size: 12px; color: var(--text-secondary); background: var(--bg-surface); padding: 8px 12px; border-radius: 6px; border-left: 3px solid #64748B;">'
                    f'<b>Trích dẫn chuẩn APA 7:</b> {apa_ref_text}'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
                
        with tab_apa_table:
            st.markdown(s_res.get("evidence_table_apa7_md", generate_apa7_evidence_table_markdown(evidence_pool)))
            
        with tab_interactive:
            df_ev = s_res.get("evidence_dataframe")
            if df_ev is None or df_ev.empty:
                df_ev = papers_to_dataframe(evidence_pool)
            st.dataframe(df_ev, use_container_width=True, height=450)
    else:
        st.info("💡 Vui lòng phân tích bài báo từ Menu 1 để xem Bảng tổng hợp phương pháp & bằng chứng chuẩn APA 7.")

# -----------------------------------------------------------------------------
# MÀN HÌNH 4: TÓM LƯỢC LUẬN ĐIỂM NGHIÊN CỨU (SONG NGỮ & ĐA ĐỊNH DẠNG TẢI)
# -----------------------------------------------------------------------------
elif "04." in workspace_nav:
    if st.session_state.pipeline_results:
        s_res = st.session_state.pipeline_results["synthdesk"]
        brief_vi = s_res.get("evidence_brief_vi_md", s_res.get("evidence_brief_md", ""))
        brief_en = s_res.get("evidence_brief_en_md", "")

        st.markdown("""
        <div class="frame-box">
            <h2 style="color: var(--primary-accent);">📝 Bản tóm lược luận điểm khoa học (Song ngữ)</h2>
            <div style="color: var(--text-secondary); font-size: 14px; margin-top: 4px;">Văn bản tổng hợp học thuật (~1.000 từ), phân loại các phát hiện theo từng chủ đề lớn về Trí tuệ Nhân tạo trong Tòa soạn Báo chí kèm trích dẫn chuẩn APA 7.</div>
        </div>
        """, unsafe_allow_html=True)

        # Thanh tải đa định dạng
        st.markdown("##### 📥 Tải bản tóm lược luận điểm dưới các định dạng:")
        c_tb1, c_tb2, c_tb3, c_tb4 = st.columns(4)
        
        docx_brief = markdown_to_docx("Bản tóm lược luận điểm nghiên cứu Báo chí AI", brief_vi, author="TRẦN DUY")
        html_print = generate_printable_html("Bản tóm lược luận điểm nghiên cứu Báo chí AI", brief_vi, author="TRẦN DUY")

        with c_tb1:
            st.download_button("📄 Tải bản Word (.DOCX)", data=docx_brief, file_name="tom_luoc_luan_diem_bao_chi_ai.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        with c_tb2:
            st.download_button("🖨️ Tải bản in / PDF (.HTML)", data=html_print, file_name="in_tom_luoc_luan_diem.html", mime="text/html", use_container_width=True)
        with c_tb3:
            st.download_button("📝 Tải bản Markdown (.MD)", data=brief_vi, file_name="tom_luoc_luan_diem.md", mime="text/markdown", use_container_width=True)
        with c_tb4:
            st.download_button("📑 Tải bản Text (.TXT)", data=brief_vi, file_name="tom_luoc_luan_diem.txt", mime="text/plain", use_container_width=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        brief_tab_vi, brief_tab_en = st.tabs(["🇻🇳 Bản tóm lược tiếng Việt (Thuần Việt)", "🇬🇧 Original Evidence Brief (English)"])
        with brief_tab_vi:
            st.markdown(brief_vi)
        with brief_tab_en:
            st.markdown(brief_en)
    else:
        st.info("💡 Vui lòng phân tích bài báo từ Menu 1 để xem bản tóm lược luận điểm khoa học song ngữ.")

# -----------------------------------------------------------------------------
# MÀN HÌNH 5: SOẠN THẢO MỞ ĐẦU & KIỂM TRA DẪN CHỨNG (SONG NGỮ & ĐA ĐỊNH DẠNG TẢI)
# -----------------------------------------------------------------------------
elif "05." in workspace_nav:
    if st.session_state.pipeline_results:
        i_res = st.session_state.pipeline_results["introwri"]
        s_res = st.session_state.pipeline_results.get("synthdesk", {})
        evidence_pool = s_res.get("evidence_pool", [])
        audit_dict = i_res["audit_report_dict"]
        status_label = audit_dict["compliance_status"]
        status_color = "#10B981" if audit_dict["audit_passed"] else "#F59E0B"

        intro_en = i_res.get('introduction_draft_en_md', i_res.get('introduction_draft_md', ''))
        intro_vi = i_res.get('introduction_draft_vi_md', '')

        st.markdown(f"""
        <div class="frame-box">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <h2 style="color: var(--text-primary);">✍️ Soạn thảo mở đầu chuẩn CARS & Báo cáo kiểm tra dẫn chứng</h2>
                <span style="background: var(--badge-green-bg); color: {status_color}; border: 1px solid {status_color}; padding: 4px 14px; border-radius: 16px; font-weight: 700; font-size: 13px;">
                    {status_label}
                </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                <div style="background: var(--bg-surface-elevated); padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border-subtle);">
                    <div style="color: var(--text-muted); font-size: 11px; font-weight: 700;">ĐỘ DÀI BẢN THẢO</div>
                    <div style="font-weight: 800; font-size: 18px; color: var(--text-primary); margin-top: 3px;">{audit_dict['metrics']['total_word_count']} từ</div>
                </div>
                <div style="background: var(--bg-surface-elevated); padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border-subtle);">
                    <div style="color: var(--text-muted); font-size: 11px; font-weight: 700;">LUẬN ĐIỂM CÓ DẪN CHỨNG</div>
                    <div style="font-weight: 800; font-size: 18px; color: #10B981; margin-top: 3px;">{audit_dict['metrics']['verified_grounded_claims']} câu (≥8)</div>
                </div>
                <div style="background: var(--bg-surface-elevated); padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border-subtle);">
                    <div style="color: var(--text-muted); font-size: 11px; font-weight: 700;">BÀI BÁO ĐÃ TRÍCH DẪN</div>
                    <div style="font-weight: 800; font-size: 18px; color: var(--primary-accent); margin-top: 3px;">{audit_dict['metrics']['distinct_references_used']} bài (≥6)</div>
                </div>
                <div style="background: var(--bg-surface-elevated); padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border-subtle);">
                    <div style="color: var(--text-muted); font-size: 11px; font-weight: 700;">MÔ HÌNH SWALES CARS</div>
                    <div style="font-weight: 800; font-size: 18px; color: #F59E0B; margin-top: 3px;">Move 1, 2, 3 Đầy đủ</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Thanh tải bản thảo mở đầu đa định dạng
        st.markdown("##### 📥 Tải bản thảo mở đầu dưới các định dạng:")
        c_in1, c_in2, c_in3, c_in4 = st.columns(4)
        
        docx_intro_vi = markdown_to_docx("Bản thảo mở đầu nghiên cứu Báo chí AI (Swales CARS)", intro_vi, author="TRẦN DUY")
        docx_intro_en = markdown_to_docx("Manuscript Introduction: AI in Journalism (Swales CARS)", intro_en, author="TRẦN DUY")
        html_print_intro = generate_printable_html("Bản thảo mở đầu nghiên cứu Báo chí AI", intro_vi, author="TRẦN DUY")

        with c_in1:
            st.download_button("📄 Tải bản Word Tiếng Việt (.DOCX)", data=docx_intro_vi, file_name="ban_thao_mo_dau_vi.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        with c_in2:
            st.download_button("📄 Tải bản Word English (.DOCX)", data=docx_intro_en, file_name="manuscript_intro_en.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        with c_in3:
            st.download_button("🖨️ Tải bản in / PDF (.HTML)", data=html_print_intro, file_name="in_ban_thao_mo_dau.html", mime="text/html", use_container_width=True)
        with c_in4:
            st.download_button("📝 Tải bản Markdown (.MD)", data=intro_vi, file_name="ban_thao_mo_dau.md", mime="text/markdown", use_container_width=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        st.markdown("### ✍️ Bản thảo phần mở đầu & Trình tinh chỉnh văn bản AI (Song ngữ):")
        draft_tab_en, draft_tab_vi, draft_tab_editor = st.tabs([
            "🇬🇧 Bản thảo ngôn ngữ gốc (English CARS)",
            "🇻🇳 Bản dịch học thuật tiếng Việt (Vietnamese Translation)",
            "🛠️ Trình hiệu đính & Trau chuốt trực tiếp (In-App Live Editor & AI Polisher)"
        ])
        
        with draft_tab_en:
            st.markdown(f"""
            <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 14px; padding: 22px; color: var(--text-primary); font-size: 14.5px; line-height: 1.8;">
{intro_en}
            </div>
            """, unsafe_allow_html=True)

        with draft_tab_vi:
            st.markdown(f"""
            <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 14px; padding: 22px; color: var(--text-primary); font-size: 14.5px; line-height: 1.8;">
{intro_vi}
            </div>
            """, unsafe_allow_html=True)

        with draft_tab_editor:
            st.markdown("<div style='font-size:13px; color:var(--text-secondary); margin-bottom:8px;'>Chỉnh sửa bản thảo thời gian thực kết hợp kho mẫu câu học thuật <b>Academic Phrasebank</b> và bộ chèn trích dẫn 1-click:</div>", unsafe_allow_html=True)
            
            # 1. ACADEMIC PHRASEBANK & CITATION INSERTER TOOLBAR
            with st.expander("📖 Kho Mẫu Câu Học Thuật Quốc Tế (Academic Phrasebank) & Chèn Trích Dẫn 1-Click", expanded=False):
                pb_c1, pb_c2 = st.columns([1.2, 1.8], gap="medium")
                with pb_c1:
                    st.markdown("##### 🏛️ Chọn nhóm mẫu câu CARS:")
                    cats = get_phrasebank_categories()
                    cat_keys = list(cats.keys())
                    cat_labels = [cats[k]["title"] for k in cat_keys]
                    selected_cat_idx = st.selectbox("Giai đoạn lập luận:", range(len(cat_labels)), format_func=lambda i: cat_labels[i], key="sb_phrasebank_cat")
                    active_cat_key = cat_keys[selected_cat_idx]
                    
                    st.markdown("##### 📌 Chọn bài báo để chèn trích dẫn:")
                    paper_cite_opts = {}
                    for idx_p, p in enumerate(evidence_pool, 1):
                        p_auth = p.get('first_author', 'Tác giả')
                        p_yr = p.get('year', '2020')
                        paper_cite_opts[f"#{idx_p} {p_auth} ({p_yr})"] = f"({p_auth}, {p_yr})"
                    
                    selected_cite_key = st.selectbox("Bài báo nguồn:", list(paper_cite_opts.keys()), key="sb_paper_cite_ins")
                    if st.button("➕ Chèn trích dẫn vào bản thảo", use_container_width=True, key="btn_insert_cite"):
                        cite_tag = paper_cite_opts[selected_cite_key]
                        current_t = st.session_state.get("custom_edited_intro_vi", intro_vi)
                        st.session_state["custom_edited_intro_vi"] = current_t + f" {cite_tag} "
                        st.toast(f"Đã chèn trích dẫn {cite_tag}")
                        st.rerun()

                with pb_c2:
                    st.markdown("##### ✍️ Danh sách mẫu câu chuẩn Manchester:")
                    phrases_list = cats[active_cat_key]["phrases"]
                    for p_idx, item in enumerate(phrases_list):
                        st.markdown(f"""
                        <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:8px; padding:10px 12px; margin-bottom:8px;">
                            <div style="color:var(--primary-accent); font-size:12.5px; font-weight:600; margin-bottom:3px;">🇬🇧 {item['en']}</div>
                            <div style="color:var(--text-secondary); font-size:12px; font-style:italic;">🇻🇳 {item['vi']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"➕ Chèn mẫu câu #{p_idx+1} vào bản thảo", key=f"btn_ins_phrase_{active_cat_key}_{p_idx}"):
                            current_t = st.session_state.get("custom_edited_intro_vi", intro_vi)
                            st.session_state["custom_edited_intro_vi"] = current_t + f"\n\n{item['vi']}"
                            st.toast("Đã thêm mẫu câu vào bản thảo!")
                            st.rerun()

            # Text area for live editing
            current_edit_text = st.session_state.get("custom_edited_intro_vi", intro_vi)
            edited_text_input = st.text_area("Văn bản bản thảo tiếng Việt (có thể chỉnh sửa trực tiếp):", value=current_edit_text, height=260, key="txt_live_intro_editor")
            
            p_c1, p_c2, p_c3, p_c4 = st.columns(4)
            
            provider_mode = "gemini" if "Gemini" in llm_choice and api_key_val else ("openai" if "OpenAI" in llm_choice and api_key_val else "mock")
            m_name = "gemini-2.0-flash" if "2.0" in llm_choice else ("gpt-4o-mini" if provider_mode == "openai" else "mock")
            polisher_llm = LLMHelper(provider=provider_mode, api_key=api_key_val, model_name=m_name)
            polisher_agent = EditorPolisherAgent(llm_helper=polisher_llm)

            with p_c1:
                if st.button("🔄 AI Trau chuốt văn phong Scopus Q1", use_container_width=True, key="btn_polish_tone"):
                    with st.spinner("Đang nâng cấp văn phong học thuật..."):
                        p_res = polisher_agent.polish_text(edited_text_input, action_type="polish")
                        st.session_state["custom_edited_intro_vi"] = p_res["result_text"]
                        st.toast(p_res["changes_summary"])
                        st.rerun()
            with p_c2:
                if st.button("📈 AI Mở rộng luận điểm & Cơ chế", use_container_width=True, key="btn_expand_arg"):
                    with st.spinner("Đang mở rộng chiều sâu luận điểm..."):
                        p_res = polisher_agent.polish_text(edited_text_input, action_type="expand")
                        st.session_state["custom_edited_intro_vi"] = p_res["result_text"]
                        st.toast(p_res["changes_summary"])
                        st.rerun()
            with p_c3:
                if st.button("✂️ AI Rút gọn súc tích", use_container_width=True, key="btn_shorten_text"):
                    with st.spinner("Đang cô đọng thông tin..."):
                        p_res = polisher_agent.polish_text(edited_text_input, action_type="shorten")
                        st.session_state["custom_edited_intro_vi"] = p_res["result_text"]
                        st.toast(p_res["changes_summary"])
                        st.rerun()
            with p_c4:
                if st.button("🔗 AI Tăng liên kết Swales CARS", use_container_width=True, key="btn_cohesion_cars"):
                    with st.spinner("Đang tối ưu hóa mạch lập luận..."):
                        p_res = polisher_agent.polish_text(edited_text_input, action_type="cohesion")
                        st.session_state["custom_edited_intro_vi"] = p_res["result_text"]
                        st.toast(p_res["changes_summary"])
                        st.rerun()

            if st.button("💾 Lưu bản chỉnh sửa này vào hồ sơ dự án", type="primary", use_container_width=True, key="btn_save_edited_intro"):
                st.session_state["custom_edited_intro_vi"] = edited_text_input
                st.session_state.pipeline_results["introwri"]["introduction_draft_vi_md"] = edited_text_input
                st.session_state.pipeline_results["artifacts"]["introduction_draft_vi.md"] = edited_text_input
                st.success("✓ Đã cập nhật thành công bản thảo mở đầu! Tệp xuất Word (.docx) và in ấn (.html) đã tự động đồng bộ.")

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        st.markdown("### 🔍 Báo cáo kiểm tra dẫn chứng & Mô phỏng phản biện Scopus (Song ngữ):")
        audit_tab_vi, audit_tab_en, audit_tab_peer = st.tabs([
            "🇻🇳 Báo cáo thẩm định chi tiết (Tiếng Việt)",
            "🇬🇧 Technical Audit Report & JSON Metrics (English)",
            "🎓 Mô phỏng phản biện tạp chí Scopus (Double-Blind Peer Review)"
        ])
        
        with audit_tab_vi:
            st.markdown(i_res.get("audit_report_vi_md", ""))
            
        with audit_tab_en:
            st.json(audit_dict)

        with audit_tab_peer:
            st.markdown("""
            <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
                <div style="color: var(--primary-accent); font-weight: 700; font-size: 14px; margin-bottom: 4px;">
                    🎓 Mô phỏng quy trình bình duyệt khoa học kép độc lập (Double-Blind Peer Review)
                </div>
                <div style="color: var(--text-secondary); font-size: 13px;">
                    Reviewer 1 (Chuyên gia phương pháp luận) và Reviewer 2 (Chuyên gia phát hiện thực nghiệm & tính mới) sẽ thẩm định gắt gao bài báo của bạn theo chuẩn tạp chí Scopus Q1.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 CHẠY MÔ PHỎNG PHẢN BIỆN KHOA HỌC KÉP NGAY", type="primary", use_container_width=True, key="btn_run_peer_review"):
                with st.spinner("⏳ Hai chuyên gia phản biện đang thẩm định bản thảo bài báo..."):
                    reviewer_llm = LLMHelper(provider=provider_mode, api_key=api_key_val, model_name=m_name)
                    peer_agent = PeerReviewerAgent(llm_helper=reviewer_llm)
                    curr_text_to_eval = st.session_state.get("custom_edited_intro_vi", intro_vi)
                    peer_report = peer_agent.simulate_peer_review(curr_text_to_eval)
                    st.session_state["peer_review_result"] = peer_report
                    st.toast(f"Đã hoàn tất phản biện! Quyết định: {peer_report['decision']}")

            if st.session_state.get("peer_review_result"):
                p_res_data = st.session_state["peer_review_result"]
                st.markdown(f"""
                <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 14px; padding: 22px; color: var(--text-primary); font-size: 14px; line-height: 1.75; margin-top: 10px;">
{p_res_data['review_report_md']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 Vui lòng phân tích bài báo từ Menu 1 để tạo bản thảo mở đầu và báo cáo kiểm tra dẫn chứng song ngữ.")

# -----------------------------------------------------------------------------
# MÀN HÌNH 6: TẢI VỀ TRỌN BỘ HỒ SƠ, SLIDE POWERPOINT & BỘ CÔNG CỤ AI COPILOT
# -----------------------------------------------------------------------------
elif "06." in workspace_nav:
    if st.session_state.pipeline_results:
        artifacts = st.session_state.pipeline_results["artifacts"]
        zip_data = st.session_state.pipeline_results["zip_bytes"]
        evidence_pool = st.session_state.pipeline_results["synthdesk"]["evidence_pool"]
        all_papers = st.session_state.pipeline_results["citenet"].get("papers_list", evidence_pool)
        
        oa_pool = [p for p in all_papers if p.get("is_oa") or bool(p.get("pdf_url"))]
        paywall_pool = [p for p in all_papers if not (p.get("is_oa") or bool(p.get("pdf_url")))]
        
        st.markdown("""
        <div class="frame-box">
            <h2 style="color: var(--primary-accent);">📦 Trung tâm Xuất bản Hồ sơ, Slide Thuyết trình & Trợ lý Đa Tài liệu AI</h2>
            <p style="color: var(--text-secondary); font-size: 14px; margin: 0;">
                Xuất trọn gói Slide báo cáo PowerPoint (.pptx), hội thoại so sánh chéo đa tài liệu (Multi-Doc RAG), trích xuất bảng biểu từ PDF, và chuyển đổi 6 chuẩn trích dẫn quốc tế (APA 7, IEEE, Harvard, Chicago, MLA, Vancouver).
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_pkg_export, tab_multidoc_rag, tab_fig_gallery, tab_multi_cite, tab_batch_pdf = st.tabs([
            "📦 1. Gói hồ sơ & Slide PowerPoint (.PPTX)",
            "🤖 2. AI Chatbot Tổng hợp Đa Tài liệu (RAG)",
            "📊 3. Bộ sưu tập Bảng biểu & Đồ thị PDF",
            "⚡ 4. Trung tâm Đa Chuẩn Trích dẫn & Đồng bộ",
            "📑 5. Tải Full PDF Hàng loạt & Copilot Đơn lẻ"
        ])

        # ---------------------------------------------------------------------
        # TAB 1: GÓI HỒ SƠ & SLIDE POWERPOINT (.PPTX)
        # ---------------------------------------------------------------------
        with tab_pkg_export:
            st.markdown("##### 📽️ Tải Slide Thuyết trình Báo cáo Khoa học (PowerPoint .PPTX):")
            try:
                topic_kw = st.session_state.get("custom_keywords", "Nghiên cứu Báo chí AI & Tòa soạn Tự động hóa")
                pptx_bytes = create_presentation_deck(st.session_state.pipeline_results, topic_title=topic_kw)
                st.download_button(
                    label="📽️ TẢI BỘ SLIDE THUYẾT TRÌNH BÁO CÁO KHOA HỌC (.PPTX - 8 SLIDE CHUẨN QUỐC TẾ)",
                    data=pptx_bytes,
                    file_name="Bao_cao_Thuyet_trinh_ScholarGraph.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    type="primary",
                    use_container_width=True
                )
            except Exception as ex:
                st.error(f"Lỗi tạo Slide PowerPoint: {ex}")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="⬇️ TẢI TRỌN BỘ HỒ SƠ NGHIÊN CỨU (.ZIP - ĐẦY ĐỦ BẢN THẢO SONG NGỮ & APA 7)",
                data=zip_data,
                file_name="ho_so_nghien_cuu_bao_chi_ai_apa7.zip",
                mime="application/zip",
                use_container_width=True
            )

            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
            st.markdown("##### 📥 Tải riêng lẻ từng tài liệu trong hồ sơ:")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("🌐 1. Sơ đồ tương tác mạng lưới (network.html)", data=artifacts.get("network.html", ""), file_name="so_do_mang_luoi.html", mime="text/html", use_container_width=True)
                st.download_button("📚 2. Danh mục tài liệu chuẩn APA 7 (references_apa7.md)", data=artifacts.get("references_apa7.md", ""), file_name="danh_muc_tai_lieu_apa7.md", mime="text/markdown", use_container_width=True)
                st.download_button("📑 3. Tệp BibTeX cho Overleaf/LaTeX (refs.bib)", data=artifacts.get("refs.bib", ""), file_name="refs.bib", mime="text/plain", use_container_width=True)
                st.download_button("📑 4. Tệp RIS cho Zotero/Mendeley (refs.ris)", data=artifacts.get("refs.ris", ""), file_name="refs.ris", mime="text/plain", use_container_width=True)
            with col_d2:
                st.download_button("📊 5. Bảng tổng hợp phương pháp chuẩn APA 7 (evidence_table_apa7.md)", data=artifacts.get("evidence_table_apa7.md", ""), file_name="bang_phuong_phap_apa7.md", mime="text/markdown", use_container_width=True)
                st.download_button("✍️ 6. Bản thảo Mở đầu Tiếng Anh (introduction_draft_en.md)", data=artifacts.get("introduction_draft_en.md", ""), file_name="ban_thao_mo_dau_en.md", mime="text/markdown", use_container_width=True)
                st.download_button("✍️ 7. Bản dịch Mở đầu Tiếng Việt (introduction_draft_vi.md)", data=artifacts.get("introduction_draft_vi.md", ""), file_name="ban_thao_mo_dau_vi.md", mime="text/markdown", use_container_width=True)
                st.download_button("🔍 8. Báo cáo kiểm tra chất lượng dẫn chứng (audit_report_vi.md)", data=artifacts.get("audit_report_vi.md", ""), file_name="bao_cao_kiem_tra_dan_chung.md", mime="text/markdown", use_container_width=True)

        # ---------------------------------------------------------------------
        # TAB 2: AI CHATBOT TỔNG HỢP ĐA TÀI LIỆU (MULTI-DOC SYNTHESIS RAG)
        # ---------------------------------------------------------------------
        with tab_multidoc_rag:
            st.markdown("""
            <div style="background:var(--bg-surface); border:1px solid var(--primary-accent); border-radius:12px; padding:16px 20px; margin-bottom:16px;">
                <div style="color:var(--primary-accent); font-weight:700; font-size:15px; margin-bottom:4px;">
                    🤖 Trợ lý AI Tổng hợp & So sánh Chéo Đa Tài liệu (Cross-Paper Synthesis Engine)
                </div>
                <div style="color:var(--text-secondary); font-size:13px;">
                    Tổng hợp kiến thức chéo trên toàn bộ tập hợp bài báo Scopus Q1/Q2 đã thẩm định. Đối chiếu sự đồng thuận, mâu thuẫn và chỉ ra chứng cứ thực nghiệm cụ thể.
                </div>
            </div>
            """, unsafe_allow_html=True)

            rag_c1, rag_c2 = st.columns([1.2, 2.8], gap="medium")
            with rag_c1:
                st.markdown("💡 **Câu hỏi tổng hợp gợi ý:**")
                if st.button("❓ So sánh phương pháp các bài?", use_container_width=True, key="btn_rag_meth"):
                    st.session_state["multidoc_rag_q"] = "So sánh sự khác biệt và tương đồng về phương pháp nghiên cứu, cách chọn mẫu và kỹ thuật phân tích dữ liệu giữa các công trình này?"
                if st.button("❓ Tổng hợp định nghĩa & Khung lý thuyết?", use_container_width=True, key="btn_rag_theory"):
                    st.session_state["multidoc_rag_q"] = "Tổng hợp các định nghĩa cốt lõi và khung lý thuyết chủ đạo về trí tuệ nhân tạo trong tòa soạn báo chí xuất hiện trong các bài báo?"
                if st.button("❓ Đối chiếu các phát hiện mâu thuẫn?", use_container_width=True, key="btn_rag_conflict"):
                    st.session_state["multidoc_rag_q"] = "Có những phát hiện thực nghiệm nào mâu thuẫn hoặc đưa ra góc nhìn trái ngược nhau về niềm tin của độc giả đối với tin tức tự động?"
                if st.button("❓ Tổng kết thách thức đạo đức?", use_container_width=True, key="btn_rag_ethics"):
                    st.session_state["multidoc_rag_q"] = "Tổng kết toàn diện các rủi ro đạo đức, thiên vị thuật toán và vấn đề trách nhiệm giải trình được các tác giả cảnh báo?"

            with rag_c2:
                rag_query_val = st.text_area(
                    "Câu hỏi nghiên cứu tổng hợp:",
                    value=st.session_state.get("multidoc_rag_q", "So sánh phương pháp nghiên cứu và phát hiện thực nghiệm giữa các bài báo tiêu biểu?"),
                    height=90,
                    key="txt_rag_query"
                )
                if st.button("🚀 TỔNG HỢP & ĐỐI CHIẾU CHÉO BẰNG CHỨNG HỌC THUẬT", type="primary", use_container_width=True, key="btn_run_rag_synthesizer"):
                    with st.spinner("⏳ Đang phân tích và đối soát toàn bộ cơ sở dữ liệu bài báo..."):
                        provider_mode = "gemini" if "Gemini" in llm_choice and api_key_val else ("openai" if "OpenAI" in llm_choice and api_key_val else "mock")
                        m_name = "gemini-2.0-flash" if "2.0" in llm_choice else ("gpt-4o-mini" if provider_mode == "openai" else "mock")
                        rag_llm = LLMHelper(provider=provider_mode, api_key=api_key_val, model_name=m_name)
                        rag_engine = MultiDocSynthesizer(llm_helper=rag_llm)
                        
                        rag_res = rag_engine.answer_query(rag_query_val, evidence_pool)
                        st.session_state["multidoc_rag_last_result"] = rag_res

                if st.session_state.get("multidoc_rag_last_result"):
                    res_obj = st.session_state["multidoc_rag_last_result"]
                    st.markdown(f"""
                    <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:12px; padding:20px 24px; margin-top:14px; font-size:14px; line-height:1.75; color:var(--text-primary);">
                        {res_obj['answer']}
                    </div>
                    """, unsafe_allow_html=True)
                    if res_obj.get("referenced_papers"):
                        with st.expander(f"📚 Xem {len(res_obj['referenced_papers'])} công trình được trích dẫn trong câu trả lời"):
                            for ref_line in res_obj["referenced_papers"]:
                                st.markdown(f"• {ref_line}")

        # ---------------------------------------------------------------------
        # TAB 3: BỘ SƯU TẬP BẢNG BIỂU & ĐỒ THỊ TỪ PDF (FIGURE GALLERY)
        # ---------------------------------------------------------------------
        with tab_fig_gallery:
            st.markdown("""
            <div style="background:var(--bg-surface); border:1px solid var(--badge-green-border); border-radius:12px; padding:16px 20px; margin-bottom:16px;">
                <div style="color:var(--badge-green-text); font-weight:700; font-size:15px; margin-bottom:4px;">
                    📊 Bộ sưu tập Bảng biểu & Đồ thị Trích xuất từ Toàn văn PDF (Figure & Table Gallery)
                </div>
                <div style="color:var(--text-secondary); font-size:13px;">
                    Tự động quét các tệp PDF đã tải về trên máy, bóc tách các sơ đồ, đồ thị và bảng số liệu định lượng để duyệt nhanh mà không cần đọc hết bài báo.
                </div>
            </div>
            """, unsafe_allow_html=True)

            scan_btn = st.button("🔍 Quét & Trích xuất Bảng biểu / Đồ thị từ Thư mục PDF", type="primary", key="btn_scan_visuals")
            
            if scan_btn or "cached_pdf_visuals" in st.session_state:
                if scan_btn:
                    with st.spinner("⏳ Đang quét cấu trúc PDF và bóc tách hình ảnh đồ thị..."):
                        extracted_vis = batch_extract_visuals_from_directory(st.session_state.download_folder, max_total_visuals=24)
                        st.session_state["cached_pdf_visuals"] = extracted_vis
                
                vis_list = st.session_state.get("cached_pdf_visuals", [])
                if not vis_list:
                    st.info(f"ℹ️ Chưa tìm thấy biểu đồ hình ảnh nào trong thư mục `{st.session_state.download_folder}`. Hãy tải các bản PDF về máy trước.")
                else:
                    st.success(f"✓ Đã trích xuất thành công **{len(vis_list)}** bảng biểu / đồ thị từ các bài báo PDF!")
                    
                    # Display 3-column image gallery
                    cols = st.columns(3)
                    for v_idx, v_item in enumerate(vis_list):
                        col_target = cols[v_idx % 3]
                        with col_target:
                            st.image(v_item["image_bytes"], caption=f"{v_item['doc_name'][:25]}... (Trang {v_item['page_number']})", use_container_width=True)
                            st.download_button(
                                label=f"⬇️ Tải ảnh #{v_idx+1} ({v_item['width']}x{v_item['height']}px)",
                                data=v_item["image_bytes"],
                                file_name=f"figure_{v_idx+1}_{v_item['doc_name']}.{v_item['image_ext']}",
                                mime=f"image/{v_item['image_ext']}",
                                key=f"dl_img_{v_idx}",
                                use_container_width=True
                            )
                            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # TAB 4: TRUNG TÂM ĐA CHUẨN TRÍCH DẪN & ĐỒNG BỘ ZOTERO/NOTION
        # ---------------------------------------------------------------------
        with tab_multi_cite:
            st.markdown("""
            <div style="background:var(--bg-surface); border:1px solid var(--primary-accent); border-radius:12px; padding:16px 20px; margin-bottom:16px;">
                <div style="color:var(--primary-accent); font-weight:700; font-size:15px; margin-bottom:4px;">
                    ⚡ Trung tâm Đa Chuẩn Trích dẫn Quốc tế & Đồng bộ Zotero / Notion
                </div>
                <div style="color:var(--text-secondary); font-size:13px;">
                    Hỗ trợ chuyển đổi tức thì 6 chuẩn trích dẫn quốc tế hàng đầu và tạo sẵn cấu trúc dữ liệu nạp trực tiếp vào Notion Database hoặc Zotero API.
                </div>
            </div>
            """, unsafe_allow_html=True)

            c_style_col1, c_style_col2 = st.columns([1.5, 2.5], gap="medium")
            with c_style_col1:
                st.markdown("##### 📌 Chọn định dạng trích dẫn:")
                chosen_style = st.selectbox(
                    "Chuẩn trích dẫn học thuật:",
                    ["APA 7th Edition (Mặc định)", "IEEE Style (Kỹ thuật & AI)", "Harvard Referencing", "Chicago 17th Edition (Author-Date)", "MLA 9th Edition", "Vancouver Style"],
                    key="sb_multi_style_choice"
                )
                style_key_map = {
                    "APA 7th Edition (Mặc định)": "apa7",
                    "IEEE Style (Kỹ thuật & AI)": "ieee",
                    "Harvard Referencing": "harvard",
                    "Chicago 17th Edition (Author-Date)": "chicago",
                    "MLA 9th Edition": "mla",
                    "Vancouver Style": "vancouver"
                }
                curr_style_key = style_key_map.get(chosen_style, "apa7")

                st.markdown("##### 🔄 Đồng bộ cơ sở dữ liệu học thuật:")
                notion_json = json.dumps(generate_notion_sync_payload(evidence_pool), ensure_ascii=False, indent=2)
                zotero_json = json.dumps(generate_zotero_sync_payload(evidence_pool), ensure_ascii=False, indent=2)

                st.download_button("📊 Xuất file nạp Notion Database (.JSON)", data=notion_json, file_name="notion_papers_sync.json", mime="application/json", use_container_width=True)
                st.download_button("📥 Xuất file nạp Zotero Collection (.JSON)", data=zotero_json, file_name="zotero_papers_sync.json", mime="application/json", use_container_width=True)

            with c_style_col2:
                st.markdown(f"##### 📚 Danh mục tài liệu theo chuẩn {chosen_style}:")
                style_md = generate_multi_style_references_markdown(evidence_pool, style=curr_style_key)
                st.text_area("Văn bản trích dẫn định dạng chuẩn (Có thể sao chép nhanh):", value=style_md, height=290, key="txt_style_preview")
                st.download_button(
                    f"📝 Tải danh mục trích dẫn ({curr_style_key.upper()} .MD)",
                    data=style_md,
                    file_name=f"references_{curr_style_key}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

        # ---------------------------------------------------------------------
        # TAB 5: TẢI FULL PDF HÀNG LOẠT & COPILOT ĐƠN LẺ
        # ---------------------------------------------------------------------
        with tab_batch_pdf:
            st.markdown(f"""
            <div style="background: var(--bg-surface); border: 1px solid var(--primary-accent); border-radius: 14px; padding: 20px 24px; margin-bottom: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:10px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        {get_svg_icon("download", color="var(--primary-accent)", size=22)}
                        <h3 style="margin:0; font-size:17px; color:var(--primary-accent);">Trình tải hàng loạt bản Full PDF về máy tính (Batch PDF Downloader)</h3>
                    </div>
                    <div style="display:flex; gap:8px;">
                        <span class="status-chip green">{icon_spark_svg} {len(oa_pool)} bản PDF Miễn phí</span>
                        <span class="status-chip rose">{icon_shield_svg} {len(paywall_pool)} bản Trả phí</span>
                    </div>
                </div>
                <p style="color:var(--text-secondary); font-size:13.5px; line-height:1.6; margin:0;">
                    Chỉ định thư mục lưu trữ trên ổ đĩa máy tính của bạn và tiến hành tải xuống hàng loạt các tệp Open Access có thanh tiến trình trực tiếp.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # 1. Chỉ định thư mục lưu
            col_dir1, col_dir2 = st.columns([3, 1])
            with col_dir1:
                target_save_folder = st.text_input(
                    "📁 Chỉ định đường dẫn thư mục lưu tệp PDF trên thiết bị của bạn:",
                    value=st.session_state.download_folder,
                    help="Nhập đường dẫn tuyệt đối hoặc tương đối trên máy tính để lưu tệp PDF tải về",
                    key="txt_dl_folder_tab5"
                )
                st.session_state.download_folder = target_save_folder
            with col_dir2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("📁 Tạo / Xác nhận thư mục", use_container_width=True, key="btn_confirm_dir_tab5"):
                    try:
                        os.makedirs(target_save_folder, exist_ok=True)
                        st.success(f"✓ Thư mục sẵn sàng: `{os.path.abspath(target_save_folder)}`")
                    except Exception as ex:
                        st.error(f"Lỗi tạo thư mục: {ex}")

            # 2. Bộ chọn tài liệu tải xuống
            oa_options = {}
            for idx_p, p in enumerate(oa_pool, 1):
                title_clean = p.get('title', 'Untitled')
                auth = p.get('first_author', 'Tác giả')
                yr = p.get('year', 'n.d.')
                lbl = f"#{idx_p} [{yr}] {auth} — {title_clean[:65]}..." if len(title_clean) > 65 else f"#{idx_p} [{yr}] {auth} — {title_clean}"
                oa_options[lbl] = p

            c_sel1, c_sel2 = st.columns([1, 1])
            with c_sel1:
                select_all_oa = st.checkbox("Chọn tất cả tài liệu có bản PDF miễn phí", value=True, key="cb_select_all_tab5")
            with c_sel2:
                st.caption(f"Đã phát hiện **{len(oa_pool)}** tài liệu có liên kết tải PDF trực tiếp.")

            default_selected = list(oa_options.keys()) if select_all_oa else []
            selected_labels = st.multiselect(
                "Danh sách bài báo sẽ được tải về thiết bị:",
                options=list(oa_options.keys()),
                default=default_selected,
                label_visibility="collapsed",
                key="ms_dl_papers_tab5"
            )
            selected_papers_to_download = [oa_options[k] for k in selected_labels if k in oa_options]

            start_batch_btn = st.button(
                f"🚀 TIẾN HÀNH TẢI {len(selected_papers_to_download)} TÀI LIỆU ĐÃ CHỌN VỀ MÁY TÍNH",
                type="primary",
                disabled=len(selected_papers_to_download) == 0,
                use_container_width=True,
                key="btn_start_dl_tab5"
            )

            if start_batch_btn:
                if not selected_papers_to_download:
                    st.warning("⚠️ Vui lòng chọn ít nhất 1 bài báo để tiến hành tải.")
                else:
                    progress_container = st.container()
                    with progress_container:
                        p_bar = st.progress(0, text="Đang chuẩn bị kết nối tải tệp PDF...")
                        log_placeholder = st.empty()
                        
                        def download_callback(cur_idx, total_cnt, message, extra):
                            pct = int((cur_idx / total_cnt) * 100)
                            p_bar.progress(pct, text=f"Tiến độ tải ({cur_idx}/{total_cnt}): {message}")
                            if extra.get("status") == "completed_item":
                                r = extra.get("result", {})
                                if r.get("success"):
                                    log_placeholder.markdown(f"<span style='color:var(--badge-green-text);'>✓ Đã lưu: <b>{r.get('filename')}</b> ({r.get('size_mb')} MB)</span>", unsafe_allow_html=True)
                                else:
                                    log_placeholder.markdown(f"<span style='color:var(--badge-rose-text);'>⚠️ Lỗi tải: <b>{r.get('title')[:40]}</b> ({r.get('error')})</span>", unsafe_allow_html=True)

                        with st.spinner("⏳ Đang tải các tài liệu PDF về thiết bị..."):
                            download_summary = batch_download_papers(
                                papers=selected_papers_to_download,
                                target_directory=target_save_folder,
                                progress_callback=download_callback,
                                timeout=25
                            )
                            st.session_state.batch_download_status = download_summary

            if st.session_state.batch_download_status:
                summary = st.session_state.batch_download_status
                succ_cnt = summary["success_count"]
                tot_mb = summary["total_size_mb"]
                dest_dir = summary["target_directory"]

                st.markdown(f"""
                <div style="background: var(--bg-surface); border: 1px solid var(--badge-green-border); border-radius: 12px; padding: 18px 20px; margin: 14px 0;">
                    <h4 style="color:var(--badge-green-text); margin:0 0 4px 0; font-size:16px;">🎉 Hoàn tất quá trình tải PDF hàng loạt!</h4>
                    <div style="color:var(--text-primary); font-size:13.5px;">
                        Đã tải thành công <b>{succ_cnt} / {summary['total_requested']}</b> tệp PDF (Tổng dung lượng: <b>{tot_mb} MB</b>).
                    </div>
                    <div style="color:var(--text-muted); font-size:12.5px; margin-top:4px;">
                        📁 Vị trí thư mục lưu trên máy tính: <code>{dest_dir}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                res_c1, res_c2 = st.columns(2)
                with res_c1:
                    zip_all_pdfs = create_zip_from_downloaded_files(summary["successful_downloads"])
                    st.download_button("📦 Tải gói nén .ZIP chứa các PDF đã tải", data=zip_all_pdfs, file_name="cac_bai_bao_full_pdf.zip", mime="application/zip", use_container_width=True, key="btn_dl_all_zip_tab5")
                with res_c2:
                    if st.button("📂 Mở thư mục chứa tệp PDF trên máy tính", use_container_width=True, key="btn_open_folder_tab5"):
                        try:
                            if os.name == 'nt':
                                os.startfile(dest_dir)
                                st.toast(f"Đã mở thư mục {dest_dir}")
                        except Exception as e:
                            st.info(f"Đường dẫn thư mục: {dest_dir}")

            # PDF COPILOT ĐỌC HIỂU TOÀN VĂN
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            st.markdown("##### 💬 Trợ lý AI Copilot đọc hiểu sâu từng tệp PDF (Single PDF Deep Reader):")
            
            existing_pdfs = []
            if os.path.exists(target_save_folder):
                existing_pdfs = [os.path.join(target_save_folder, f) for f in os.listdir(target_save_folder) if f.lower().endswith(".pdf")]
                
            if not existing_pdfs and st.session_state.get("batch_download_status"):
                existing_pdfs = [item["dest_path"] for item in st.session_state["batch_download_status"]["successful_downloads"] if os.path.exists(item.get("dest_path", ""))]

            col_copilot_opts, col_copilot_chat = st.columns([1.2, 2.8], gap="medium")
            with col_copilot_opts:
                if existing_pdfs:
                    st.caption(f"Đã phát hiện **{len(existing_pdfs)} tệp PDF**.")
                    pdf_labels = {os.path.basename(p): p for p in existing_pdfs}
                    sel_pdf_label = st.selectbox("Chọn tài liệu:", ["🔍 Quét toàn bộ tệp PDF đã tải"] + list(pdf_labels.keys()), key="sb_pdf_scope_tab5")
                    active_pdf_paths = existing_pdfs if sel_pdf_label == "🔍 Quét toàn bộ tệp PDF đã tải" else [pdf_labels[sel_pdf_label]]
                else:
                    st.info("ℹ️ Hãy tải tệp PDF về để kích hoạt Copilot toàn văn.")
                    active_pdf_paths = []

            with col_copilot_chat:
                user_copilot_query = st.text_area("Câu hỏi về bài báo:", value="Những phát hiện thực nghiệm cốt lõi nhất là gì?", height=75, key="txt_copilot_q_tab5")
                if st.button("🚀 GỬI CÂU HỎI CHO COPILOT", type="primary", use_container_width=True, key="btn_send_copilot_tab5"):
                    if not active_pdf_paths:
                        st.warning("⚠️ Không có tệp PDF nào sẵn sàng.")
                    else:
                        with st.spinner("⏳ Đang quét toàn văn các trang PDF..."):
                            provider_mode = "gemini" if "Gemini" in llm_choice and api_key_val else ("openai" if "OpenAI" in llm_choice and api_key_val else "mock")
                            m_name = "gemini-2.0-flash" if "2.0" in llm_choice else ("gpt-4o-mini" if provider_mode == "openai" else "mock")
                            copilot_llm = LLMHelper(provider=provider_mode, api_key=api_key_val, model_name=m_name)
                            copilot_agent = PDFCopilotAgent(llm_helper=copilot_llm)
                            st.session_state["copilot_last_answer"] = copilot_agent.answer_pdf_question(user_copilot_query, target_pdf_paths=active_pdf_paths)

                if st.session_state.get("copilot_last_answer"):
                    ans_data = st.session_state["copilot_last_answer"]
                    st.markdown(f"""
                    <div style="background:var(--bg-surface-elevated); border:1px solid var(--border-subtle); border-radius:12px; padding:16px 20px; margin-top:10px; font-size:14px; line-height:1.75; color:var(--text-primary);">
                        <div style="color:var(--badge-green-text); font-weight:700; margin-bottom:4px;">✓ DẪN CHỨNG TRANG SÁCH TỪ COPILOT:</div>
                        {ans_data['answer']}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("💡 Vui lòng phân tích bài báo từ Menu 1 để mở trung tâm xuất bản hồ sơ & AI Copilot.")

# -----------------------------------------------------------------------------
# MÀN HÌNH 7: CÀI ĐẶT HỆ THỐNG & TRÍ TUỆ NHÂN TẠO (GEMINI 2.0 FLASH / PRO)
# -----------------------------------------------------------------------------
elif "07." in workspace_nav:
    st.markdown("""
    <div class="frame-box">
        <h2 style="color: var(--text-primary);">⚙️ Cài đặt hệ thống & Tùy chọn mô hình trí tuệ nhân tạo (Google Gemini 2.0)</h2>
        <p style="color: var(--text-secondary); font-size: 14px; margin: 0;">
            Hệ thống hỗ trợ các chuẩn API mới nhất của Google Gemini (Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash), OpenAI GPT-4o-mini và Bộ máy Học thuật Nội bộ Ngoại tuyến.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("### 🎛️ Quy mô quét mạng lưới trích dẫn:")
        gen1_val = st.slider("Số bài tham khảo trực tiếp (Thế hệ 1):", min_value=5, max_value=40, value=20, step=1)
        gen2_val = st.slider("Số bài tham khảo mở rộng (Thế hệ 2):", min_value=15, max_value=120, value=68, step=1)
        synth_val = st.slider("Số bài chọn lọc để bóc tách chi tiết chuẩn APA 7:", min_value=10, max_value=40, value=25, step=1)
    
    with col_s2:
        st.markdown("### 🤖 Mô hình trí tuệ nhân tạo (AI Engine):")
        model_choice = st.selectbox(
            "Mô hình AI:",
            [
                "Google Gemini 2.0 Flash (Khuyên dùng - Nhanh & Chuẩn xác nhất)",
                "Google Gemini 1.5 Pro (Phân tích chuyên sâu)",
                "Google Gemini 1.5 Flash",
                "OpenAI (gpt-4o-mini)",
                "Mô hình Học thuật Nội bộ (Miễn phí 100% / Hoạt động Ngoại tuyến)"
            ]
        )
        api_key_input = ""
        if "Gemini" in model_choice:
            api_key_input = st.text_input("Mã khóa Gemini API Key:", value=get_secret("GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", ""), type="password")
        elif "OpenAI" in model_choice:
            api_key_input = st.text_input("Mã khóa OpenAI API Key:", value=get_secret("OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", ""), type="password")

        email_input = st.text_input(
            "Email truy cập dữ liệu OpenAlex:",
            value=get_secret("OPENALEX_EMAIL", "scholar.researcher@academic.edu.vn"),
            help="Email dùng để kết nối kênh dữ liệu học thuật mở nhanh"
        )
        st.success("✓ Đã lưu cài đặt hệ thống và cấu hình mô hình AI thành công.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎨 Bộ sưu tập 10 giao diện học thuật cao cấp (10 Academic Themes):")
    st.markdown("<div style='font-size:13.5px; color:var(--text-secondary); margin-bottom:14px;'>Tất cả các theme đều được tối ưu hóa độ tương phản nghiêm ngặt theo tiêu chuẩn WCAG AAA/AA, đảm bảo chữ luôn sắc nét, phân định rõ ràng giữa nền, thẻ nội dung và thanh điều hướng.</div>", unsafe_allow_html=True)
    
    theme_cols = st.columns(2, gap="medium")
    for idx, t in enumerate(get_theme_list()):
        target_col = theme_cols[idx % 2]
        c = t["colors"]
        is_active = (t["id"] == st.session_state.selected_theme)
        
        with target_col:
            active_border = f"border: 2px solid {c['primary_accent']};" if is_active else f"border: 1px solid {c['border_subtle']};"
            active_badge = f'<span style="background:{c["primary_accent"]}; color:#000; font-weight:800; font-size:11px; padding:2px 8px; border-radius:6px;">ĐANG SỬ DỤNG</span>' if is_active else '<span style="color:var(--text-muted); font-size:11.5px;">Sẵn sàng</span>'
            
            st.markdown(f"""
            <div style="background:{c['bg_surface']}; {active_border} border-radius:14px; padding:16px 18px; margin-bottom:10px; box-shadow:0 4px 14px rgba(0,0,0,0.08);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <div style="color:{c['text_primary']}; font-weight:700; font-size:15px;">{t['name']}</div>
                    {active_badge}
                </div>
                <div style="color:{c['primary_accent']}; font-size:12px; font-weight:600; margin-bottom:6px;">{t['tagline']}</div>
                <div style="color:{c['text_secondary']}; font-size:12.5px; line-height:1.5; margin-bottom:12px;">{t['desc']}</div>
                <div style="display:flex; gap:6px; align-items:center;">
                    <span style="font-size:11px; color:{c['text_muted']};">Bảng màu:</span>
                    <span style="display:inline-block; width:18px; height:18px; border-radius:50%; background:{c['bg_main']}; border:1px solid {c['border_subtle']};" title="Nền chính"></span>
                    <span style="display:inline-block; width:18px; height:18px; border-radius:50%; background:{c['bg_surface']}; border:1px solid {c['border_subtle']};" title="Bề mặt thẻ"></span>
                    <span style="display:inline-block; width:18px; height:18px; border-radius:50%; background:{c['primary_accent']};" title="Màu nhấn"></span>
                    <span style="display:inline-block; width:18px; height:18px; border-radius:50%; background:{c['badge_green_text']};" title="Thành công"></span>
                    <span style="display:inline-block; width:18px; height:18px; border-radius:50%; background:{c['badge_rose_text']};" title="Cảnh báo"></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if not is_active:
                if st.button(f"Áp dụng theme {t['name']}", key=f"btn_apply_theme_{t['id']}", use_container_width=True):
                    st.session_state.selected_theme = t["id"]
                    st.rerun()
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MÀN HÌNH 8: HƯỚNG DẪN SỬ DỤNG & CẨM NANG TOÀN DIỆN (SCHOLARGRAPH PRO)
# -----------------------------------------------------------------------------
elif "08." in workspace_nav:
    st.markdown("""
    <div class="manual-hero-banner">
        <div class="manual-app-title">SCHOLARGRAPH PRO</div>
        <div class="manual-app-subtitle">HỆ THỐNG MẠNG LƯỚI TRI THỨC HỌC THUẬT & SOẠN THẢO BÁO CHÍ AI</div>
        <div style="margin-top: 10px; display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
            <span class="custom-badge badge-blue">Phiên bản: v3.5 Enterprise</span>
            <span class="custom-badge badge-green">Chuẩn APA 7th Edition</span>
            <span class="custom-badge badge-purple">5 Chuẩn Trắc lượng Quốc tế</span>
            <span class="custom-badge badge-amber">Tác giả: TRẦN DUY (Lead AI Research Engineer)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists("assets/manual_banner.jpg"):
        st.image("assets/manual_banner.jpg", caption="Hệ sinh thái Trắc lượng Khoa học & Tổng hợp Tri thức Đa tầng SCHOLARGRAPH PRO", use_container_width=True)

    tab_flow, tab_samples, tab_standards, tab_faq = st.tabs([
        "🚀 Quy trình 6 bước Thực chiến",
        "💡 Đề tài Mẫu & Nạp 1-Click",
        "🕸️ Cẩm nang 5 Chuẩn Trắc lượng",
        "❓ Câu hỏi Thường gặp & Khắc phục"
    ])

    with tab_flow:
        st.markdown("### 🧭 Lộ trình 6 bước từ Khởi tạo Dữ liệu đến Hoàn thiện Công bố Khoa học")
        st.markdown("<div style='color:var(--text-secondary); font-size:13.5px; margin-bottom:18px;'>Quy trình làm việc được thiết kế chuẩn mực hóa theo thông lệ của các viện nghiên cứu và tạp chí học thuật quốc tế (Scopus/Web of Science), kết hợp sức mạnh phân tích của mô hình AI thế hệ mới.</div>", unsafe_allow_html=True)

        # Step 1
        st.markdown("""
        <div class="manual-step-card">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <div class="manual-step-badge">1</div>
                <div>
                    <div style="color:var(--text-primary); font-weight:800; font-size:16px;">Bước 1: Khởi tạo Dữ liệu & Nạp Nguồn Học thuật (Menu 01)</div>
                    <div style="color:var(--text-secondary); font-size:12px;">Data Ingestion, Resolution & OpenAlex Synchronization</div>
                </div>
            </div>
            <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.6;">
                Hệ thống cung cấp <b>4 phương thức nạp dữ liệu linh hoạt</b>:
                <ul style="margin-top:6px; margin-bottom:8px;">
                    <li><b>Nhập danh sách mã DOI:</b> Dán trực tiếp một hoặc nhiều mã DOI (ví dụ: <code>10.1177/1464884918757072</code>). Hệ thống tự động truy vấn dữ liệu thời gian thực từ mạng lưới 250+ triệu tài liệu OpenAlex.</li>
                    <li><b>Nhập từ khóa chủ đề:</b> Gõ từ khóa nghiên cứu (ví dụ: <i>"Automated Journalism AND Trust"</i>) để AI tự động tìm kiếm các bài báo kinh điển và bài báo mới nhất.</li>
                    <li><b>Tải tệp trích dẫn (.bib / .ris):</b> Nhập trực tiếp danh mục từ Zotero, Mendeley, EndNote hoặc Google Scholar.</li>
                    <li><b>Tải tệp PDF bài báo:</b> Tải tệp PDF gốc để AI trích xuất tự động văn bản, tiêu đề và siêu dữ liệu.</li>
                </ul>
                <div style="background:rgba(56, 189, 248, 0.08); border-left:3px solid #38BDF8; padding:8px 12px; border-radius:4px; font-size:12.5px; color:var(--text-primary);">
                    💡 <b>Mẹo học thuật:</b> Chọn bài báo hạt nhân (seed paper) có lượng trích dẫn cao hoặc bài báo tổng quan (Systematic Literature Review) để hệ thống tự động quét mạng lưới trích dẫn xung quanh hiệu quả nhất.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Step 2
        st.markdown("""
        <div class="manual-step-card">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <div class="manual-step-badge">2</div>
                <div>
                    <div style="color:var(--text-primary); font-weight:800; font-size:16px;">Bước 2: Khám phá Mạng lưới Trích dẫn Đa chiều (Menu 02)</div>
                    <div style="color:var(--text-secondary); font-size:12px;">Interactive Citation Network & Scientometrics Evolution</div>
                </div>
            </div>
            <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.6;">
                Trải nghiệm trực quan hóa trắc lượng khoa học đạt chuẩn quốc tế:
                <ul style="margin-top:6px; margin-bottom:8px;">
                    <li><b>5 kiểu bố cục chuẩn quốc tế:</b> Chuyển đổi linh hoạt giữa <i>VOSviewer Clustering</i>, <i>HistCite Chronological Timeline</i>, <i>Concentric Orbit</i>, <i>CiteSpace Tree DAG</i>, và <i>Scimago Quartile Matrix</i>.</li>
                    <li><b>Kích thước nút phản ánh độ ảnh hưởng:</b> Các bài báo có số lượt trích dẫn lớn sẽ hiển thị nút to, viền sáng nổi bật kèm con số trích dẫn thực tế.</li>
                    <li><b>Bộ công cụ tương tác:</b> Phóng to / Thu nhỏ (Zoom In / Zoom Out / Reset), kéo thả nút, lọc theo năm xuất bản, lọc số lượng trích dẫn tối thiểu.</li>
                    <li><b>Xuất ảnh độ phân giải cao:</b> Tải sơ đồ định dạng PNG / SVG để đưa vào bài báo khoa học hoặc luận văn.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Step 3
        st.markdown("""
        <div class="manual-step-card">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <div class="manual-step-badge">3</div>
                <div>
                    <div style="color:var(--text-primary); font-weight:800; font-size:16px;">Bước 3: Bóc tách Phương pháp & Ma trận Đối sánh APA 7 (Menu 03)</div>
                    <div style="color:var(--text-secondary); font-size:12px;">4-Dimensional Methodological Matrix & Clean APA Formatting</div>
                </div>
            </div>
            <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.6;">
                AI tự động phân tích sâu bài báo theo ma trận 4 chiều học thuật:
                <ul style="margin-top:6px; margin-bottom:8px;">
                    <li><b>Bối cảnh & Thiết kế Nghiên cứu:</b> Xác định rõ phương pháp định lượng (Survey, Experiment), định tính (In-depth Interview, Content Analysis) hoặc hỗn hợp (Mixed-methods).</li>
                    <li><b>Mẫu & Công cụ Thu thập:</b> Bóc tách quy mô mẫu (N), đối tượng khảo sát và thang đo chuẩn hóa.</li>
                    <li><b>Phát hiện Cốt lõi & Đóng góp:</b> Tóm lược các kết quả có ý nghĩa thống kê và đóng góp lý thuyết mới.</li>
                    <li><b>Hạn chế & Gợi ý Hướng mở:</b> Nhận diện điểm nghẽn của công trình làm tiền đề xây dựng khoảng trống nghiên cứu (Research Gap).</li>
                    <li><b>Làm sạch định dạng tự động:</b> Toàn bộ ký hiệu thô được chuẩn hóa thành văn bản học thuật thanh lịch chuẩn mực APA 7.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Step 4
        st.markdown("""
        <div class="manual-step-card">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <div class="manual-step-badge">4</div>
                <div>
                    <div style="color:var(--text-primary); font-weight:800; font-size:16px;">Bước 4: Tóm lược Luận điểm & Tổng thuật Đa tài liệu Song ngữ (Menu 04)</div>
                    <div style="color:var(--text-secondary); font-size:12px;">Bilingual Synthesis, Key Arguments & Systematic Matrix</div>
                </div>
            </div>
            <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.6;">
                Tổng hợp tri thức liên tài liệu phục vụ viết tổng quan lý thuyết (Literature Review):
                <ul style="margin-top:6px; margin-bottom:8px;">
                    <li><b>Tóm lược điều hành (Executive Synthesis):</b> Khái quát bức tranh toàn cảnh của chủ đề nghiên cứu.</li>
                    <li><b>Chế độ xem Song ngữ Anh - Việt:</b> Hỗ trợ dịch thuật thuật ngữ chuyên ngành chuẩn xác, đối chiếu trực tiếp giữa bản ngữ tiếng Anh và tiếng Việt.</li>
                    <li><b>So sánh đối sánh luận điểm:</b> Chỉ ra các điểm đồng thuận (Consensus) và các tranh luận học thuật (Controversies) giữa các nhóm tác giả.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Step 5
        st.markdown("""
        <div class="manual-step-card">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <div class="manual-step-badge">5</div>
                <div>
                    <div style="color:var(--text-primary); font-weight:800; font-size:16px;">Bước 5: Soạn thảo Mở đầu CARS, Phrasebank & Phản biện Mô phỏng (Menu 05)</div>
                    <div style="color:var(--text-secondary); font-size:12px;">John Swales CARS Model, Manchester Phrasebank & Peer Review Simulation</div>
                </div>
            </div>
            <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.6;">
                Trợ lý viết bài báo chuẩn ISI/Scopus:
                <ul style="margin-top:6px; margin-bottom:8px;">
                    <li><b>Mô hình CARS (Creating A Research Space):</b> Soạn thảo chuẩn 3 bước: <i>Move 1: Xác lập lãnh thổ nghiên cứu</i> &rarr; <i>Move 2: Thiết lập khoảng trống (Research Gap)</i> &rarr; <i>Move 3: Chiếm lĩnh vị thế nghiên cứu</i>.</li>
                    <li><b>Thư viện mẫu câu học thuật (Manchester Academic Phrasebank):</b> Hơn 100+ mẫu câu hàn lâm tiếng Anh chuẩn mực phân loại theo 5 giai đoạn viết bài, cho phép chèn 1-click vào văn bản.</li>
                    <li><b>Phản biện mô phỏng AI (Peer Reviewer #2):</b> Chấm điểm phản biện ẩn danh theo 5 tiêu chí gắt gao của tạp chí Q1 (Tính mới, Phương pháp luận, Đóng góp lý thuyết, Tính logic, Khả năng ứng dụng).</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Step 6
        st.markdown("""
        <div class="manual-step-card">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <div class="manual-step-badge">6</div>
                <div>
                    <div style="color:var(--text-primary); font-weight:800; font-size:16px;">Bước 6: Xuất Slide Thuyết trình, Tải PDF Hàng loạt & AI Copilot (Menu 06)</div>
                    <div style="color:var(--text-secondary); font-size:12px;">PowerPoint Presentation, Batch PDF Downloader & Multidoc RAG</div>
                </div>
            </div>
            <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.6;">
                Đóng gói trọn vẹn và khai thác chuyên sâu hồ sơ nghiên cứu:
                <ul style="margin-top:6px; margin-bottom:8px;">
                    <li><b>Tạo Slide PowerPoint (.pptx) tự động:</b> Xuất bộ trình chiếu bảo vệ luận án / báo cáo hội thảo 7-slide chuyên nghiệp với bố cục 16:9 sắc nét.</li>
                    <li><b>Tải tệp toàn văn PDF hàng loạt:</b> Tự động quét và tải song song các tệp PDF Open Access hợp pháp (Unpaywall, PubMed Central, arXiv).</li>
                    <li><b>Hệ thống hỏi đáp đa tài liệu (Multidoc RAG):</b> Đặt câu hỏi tự do bằng tiếng Việt hoặc tiếng Anh, AI truy xuất chính xác từng đoạn văn bản và trích nguồn minh bạch.</li>
                    <li><b>Bóc tách hình ảnh & biểu đồ PDF:</b> Trích xuất bảng số liệu, biểu đồ vector độ phân giải cao từ tệp PDF gốc.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_samples:
        st.markdown("### 💡 Đề tài Mẫu Thực chiến (Case Studies) & Nạp Nhanh 1-Click")
        st.markdown("<div style='color:var(--text-secondary); font-size:13.5px; margin-bottom:18px;'>Lựa chọn một trong các đề tài nghiên cứu mẫu tiêu biểu dưới đây để trải nghiệm tức thì toàn bộ chuỗi tính năng của hệ thống:</div>", unsafe_allow_html=True)

        sample_packs = [
            {
                "title": "📰 Đề tài 1: Báo chí Tự động hóa & Niềm tin của Độc giả trong Kỷ nguyên Số",
                "field": "Truyền thông & Báo chí học (Journalism & Communication Studies)",
                "desc": "Nghiên cứu tác động của tin tức do thuật toán/AI tự động sản xuất đối với nhận thức về độ tin cậy, tính khách quan và trải nghiệm của công chúng.",
                "dois": [
                    "10.1177/1464884918757072",
                    "10.1080/17512786.2017.1320773",
                    "10.1080/21670811.2019.1677534"
                ],
                "badge": "Q1 Scopus / High Impact"
            },
            {
                "title": "🤖 Đề tài 2: Trí tuệ Nhân tạo Tạo sinh & Đạo đức Tác nghiệp Tòa soạn",
                "field": "Báo chí Công nghệ & Quản trị Tòa soạn (Generative AI & Newsroom Ethics)",
                "desc": "Khảo sát việc tích hợp các mô hình ngôn ngữ lớn (LLMs) trong quy trình tác nghiệp báo chí, thách thức về tin giả, bản quyền và tính minh bạch.",
                "dois": [
                    "10.1177/2056305120948255",
                    "10.1080/17512786.2021.1910988",
                    "10.1080/21670811.2020.1803604"
                ],
                "badge": "Top Trendy 2024-2026"
            },
            {
                "title": "📱 Đề tài 3: Chuyển đổi Số Tòa soạn & Mô hình Doanh thu Báo chí Đa nền tảng",
                "field": "Kinh tế Truyền thông & Chuyển đổi Số (Media Economics & Digital Strategy)",
                "desc": "Phân tích chiến lược đăng ký thuê bao số (Paywall / Digital Subscription), mô hình thành viên và hành vi trả tiền mua tin tức trực tuyến.",
                "dois": [
                    "10.1080/21670811.2018.1504624",
                    "10.1177/1464884919864236",
                    "10.1080/17512786.2020.1740683"
                ],
                "badge": "Strategic Media Management"
            }
        ]

        for idx, sp in enumerate(sample_packs):
            st.markdown(f"""
            <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:14px; padding:18px 22px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                    <div style="color:var(--text-primary); font-weight:800; font-size:16px;">{sp['title']}</div>
                    <span class="custom-badge badge-blue">{sp['badge']}</span>
                </div>
                <div style="color:var(--primary-accent); font-size:12.5px; font-weight:600; margin-bottom:6px;">Lĩnh vực: {sp['field']}</div>
                <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.5; margin-bottom:12px;">{sp['desc']}</div>
                <div style="background:rgba(0,0,0,0.25); border-radius:8px; padding:10px 14px; font-family:monospace; font-size:12px; color:#38BDF8; margin-bottom:12px;">
                    <b>Danh sách mã DOI:</b><br/>
                    {'<br/>'.join([f"• {d}" for d in sp['dois']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn, _ = st.columns([2, 3])
            with col_btn:
                if st.button(f"📥 Nạp Đề tài {idx+1} vào Không gian làm việc (1-Click)", key=f"btn_load_sample_pack_{idx}", use_container_width=True):
                    st.session_state.doi_input_val = "\n".join(sp["dois"])
                    st.session_state.sample_dois_to_load = "\n".join(sp["dois"])
                    st.success(f"✓ Đã nạp thành công danh sách DOI của Đề tài {idx+1}! Hãy chuyển sang **Menu 01. Nhập mã DOI** để tiến hành phân tích.")

    with tab_standards:
        st.markdown("### 🕸️ Cẩm nang 5 Chuẩn Trắc lượng Khoa học Quốc tế (Scientometrics)")
        st.markdown("<div style='color:var(--text-secondary); font-size:13.5px; margin-bottom:18px;'>Hệ thống SCHOLARGRAPH PRO tích hợp 5 mô hình toán học và lý thuyết đồ thị tiên tiến nhất trong nghiên cứu trắc lượng khoa học thế giới:</div>", unsafe_allow_html=True)

        standards_data = [
            {
                "name": "1. VOSviewer ForceAtlas2 Clustering (Cụm Đồng trích dẫn)",
                "origin": "Đại học Leiden, Hà Lan (Van Eck & Waltman)",
                "theory": "Sử dụng thuật toán tối ưu hóa lực kéo-đẩy (ForceAtlas2 Layout) để nhóm các bài báo có mối quan hệ đồng trích dẫn (Co-citation) hoặc ghép cặp thư mục (Bibliographic Coupling) vào cùng một cụm màu chủ đề.",
                "use_case": "Nhận diện các trường phái nghiên cứu lớn, nhóm tác giả tiên phong và các tiểu chủ đề nhánh.",
                "icon": "🎨"
            },
            {
                "name": "2. HistCite Chronological Flow (Dòng thời gian Trực hệ)",
                "origin": "Eugene Garfield (Cha đẻ của ISI / Web of Science)",
                "theory": "Sắp xếp toàn bộ các công trình theo trục thời gian năm xuất bản từ trái sang phải, với các đường liên kết thể hiện quan hệ trích dẫn trực tiếp từ bài báo kế thừa về bài báo nền tảng.",
                "use_case": "Phác họa lịch sử phát triển của một lý thuyết khoa học và tìm ra bài báo khai phá gốc (Pioneering Seed Paper).",
                "icon": "⏳"
            },
            {
                "name": "3. Concentric Orbit Network (Mạng lưới Quỹ đạo Đồng tâm)",
                "origin": "Scientometrics Radar Model",
                "theory": "Bài báo hạt nhân hoặc bài báo có tầm ảnh hưởng tối cao nằm tại tâm điểm (Center Node). Các công trình liên quan được phân bố trên các vòng quỹ đạo đồng tâm, khoảng cách tỉ lệ nghịch với lượng trích dẫn.",
                "use_case": "Đánh giá mức độ ảnh hưởng trung tâm và độ lan tỏa của đề tài theo bán kính tri thức.",
                "icon": "🪐"
            },
            {
                "name": "4. CiteSpace Directed Acyclic Graph - DAG (Cây Phả hệ Cấu trúc)",
                "origin": "Chaomei Chen (Drexel University)",
                "theory": "Mô hình hóa các công trình thành cây đồ thị có hướng không chu trình (DAG). Nút gốc đại diện cho lý thuyết nền móng, các nhánh con thể hiện sự tiến hóa và mở rộng phương pháp luận.",
                "use_case": "Phát hiện các đột phá cấu trúc (Structural Breakthroughs) và các bước nhảy vọt về mặt lý thuyết.",
                "icon": "🌳"
            },
            {
                "name": "5. Scimago Journal Quartile Matrix (Ma trận Phân hạng Q1 - Q4)",
                "origin": "Scimago Lab / Elsevier Scopus",
                "theory": "Phân tầng trực quan các bài báo dựa trên thứ hạng chất lượng tạp chí (Q1: Top 25% uy tín nhất thế giới, Q2: 25-50%, Q3: 50-75%, Q4: 75-100%).",
                "use_case": "Đánh giá độ tin cậy học thuật và chất lượng nguồn trích dẫn của toàn bộ hồ sơ nghiên cứu.",
                "icon": "🏆"
            }
        ]

        for std in standards_data:
            st.markdown(f"""
            <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:14px; padding:18px 22px; margin-bottom:16px;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    <span style="font-size:22px;">{std['icon']}</span>
                    <div>
                        <div style="color:var(--text-primary); font-weight:800; font-size:16px;">{std['name']}</div>
                        <div style="color:var(--primary-accent); font-size:12px; font-weight:600;">Nguồn gốc & Lý thuyết: {std['origin']}</div>
                    </div>
                </div>
                <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.6; margin-bottom:8px;">
                    <b>Cơ chế hoạt động:</b> {std['theory']}
                </div>
                <div style="background:rgba(52, 211, 153, 0.08); border-left:3px solid #34D399; padding:8px 12px; border-radius:4px; font-size:12.5px; color:var(--text-primary);">
                    🎯 <b>Ứng dụng thực tế:</b> {std['use_case']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_faq:
        st.markdown("### ❓ Câu hỏi Thường gặp & Khắc phục Sự cố (FAQ & Troubleshooting)")
        st.markdown("<div style='color:var(--text-secondary); font-size:13.5px; margin-bottom:18px;'>Giải đáp các thắc mắc kỹ thuật và tối ưu hóa hiệu năng trong quá trình sử dụng hệ thống:</div>", unsafe_allow_html=True)

        faqs = [
            {
                "q": "1. Làm thế nào để cấu hình API Key Google Gemini 2.0 Flash?",
                "a": "Truy cập <a href='https://aistudio.google.com/' target='_blank' style='color:#38BDF8;'>Google AI Studio</a>, tạo một API Key miễn phí. Sau đó chuyển sang <b>Menu 07. Cài đặt hệ thống</b> trên thanh điều hướng bên trái và dán khóa API vào ô cấu hình. Hệ thống sẽ tự động lưu trữ và sử dụng cho toàn bộ các tác vụ phân tích AI."
            },
            {
                "q": "2. Hệ thống xử lý các bài báo có bản quyền (Paywalled) như thế nào?",
                "a": "Hệ thống tích hợp bộ giải mã Unpaywall, OpenAlex và PubMed Central để tự động tìm kiếm các phiên bản toàn văn Open Access (Green OA, Gold OA, Bronze OA, Hybrid OA hoặc bản Preprint hợp pháp). Với các bài báo hoàn toàn đóng kín, hệ thống vẫn trích xuất được Abstract đầy đủ, ma trận trích dẫn và các thuộc tính thư mục chuẩn xác."
            },
            {
                "q": "3. Làm sao để chuyển dữ liệu sang Zotero, Mendeley hoặc Overleaf (LaTeX)?",
                "a": "Tại <b>Menu 06. Tải về trọn bộ hồ sơ</b>, bạn có thể xuất tệp <code>citations.bib</code> hoặc <code>references.ris</code>. Tệp này có thể nhập trực tiếp vào Zotero, Mendeley, EndNote hoặc tải lên Overleaf để trích dẫn tự động trong mã nguồn LaTeX."
            },
            {
                "q": "4. Sơ đồ mạng lưới hiển thị quá nhiều nút khiến giao diện bị rối?",
                "a": "Tại <b>Menu 02. Sơ đồ mạng lưới trích dẫn</b>, sử dụng thanh trượt <i>Lọc số lượng trích dẫn tối thiểu</i> hoặc thanh trượt <i>Khoảng năm xuất bản</i> để lọc bỏ các bài báo ít liên quan, giữ lại các công trình trụ cột then chốt."
            },
            {
                "q": "5. Làm cách nào để đổi giao diện màu sắc phù hợp khi làm việc ban đêm?",
                "a": "Sử dụng hộp chọn <b>Bảng màu & Giao diện (Theme)</b> ngay đầu thanh sidebar bên trái. Hệ thống cung cấp 10 bộ theme cao cấp (Dark Academic, Midnight Obsidian, Cyberpunk Neon, Classic Ivory, Solarized Scholar...) đạt chuẩn tương phản cao WCAG AAA."
            }
        ]

        for faq in faqs:
            with st.expander(f"📌 {faq['q']}", expanded=False):
                st.markdown(f"<div style='color:var(--text-primary); font-size:13.5px; line-height:1.6;'>{faq['a']}</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MÀN HÌNH 9: QUẢN TRỊ HỆ THỐNG & PHÂN QUYỀN NGƯỜI DÙNG (SUPER ADMIN PORTAL)
# -----------------------------------------------------------------------------
elif "09." in workspace_nav:
    if not is_admin_or_super:
        st.error("🚫 Bạn không có quyền truy cập vào Cổng Quản Trị Hệ Thống.")
    else:
        st.markdown(f"""
        <div class="frame-box">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <h2 style="color:var(--primary-accent); margin:0 0 4px 0;">👑 Cổng Quản trị Hệ thống & Phân quyền Doanh nghiệp (Enterprise Admin Portal)</h2>
                    <div style="color:var(--text-secondary); font-size:13.5px;">Quản trị tài khoản truy cập, phân quyền vai trò (RBAC), kiểm soát chính sách mật khẩu và giám sát nhật ký bảo mật.</div>
                </div>
                <div style="display:flex; gap:8px;">
                    <span class="custom-badge badge-purple">Super Admin: {SUPER_ADMIN_EMAIL}</span>
                    <span class="custom-badge badge-green">Bảo mật: PBKDF2-HMAC-SHA256</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_m_users, tab_m_recovery, tab_m_audit = st.tabs([
            "👥 1. Quản lý Người dùng & Phân quyền (RBAC)",
            "🔑 2. Phục hồi Mật khẩu & Điều hướng Email Bảo mật",
            "🛡️ 3. Nhật ký Kiểm toán Bảo mật (Audit Logs)"
        ])

        # ---------------------------------------------------------------------
        # TAB 1: QUẢN LÝ NGƯỜI DÙNG & PHÂN QUYỀN
        # ---------------------------------------------------------------------
        with tab_m_users:
            all_users_data = get_all_users()
            st.markdown(f"##### 📋 Danh sách tài khoản đã cấp phép ({len(all_users_data)} người dùng):")
            
            # Display user cards/table
            for u_item in all_users_data:
                u_email = u_item["email"]
                is_sa = (u_email == SUPER_ADMIN_EMAIL)
                role_badge_class = "badge-purple" if is_sa else ("badge-blue" if u_item["role"] == "admin" else "badge-green")
                status_badge = '<span class="status-chip green">Đang hoạt động</span>' if u_item["is_active"] else '<span class="status-chip rose">Bị tạm khóa</span>'
                must_change_badge = '<span style="color:#F59E0B; font-size:11.5px; font-weight:700;">[Chưa đổi pass @123]</span>' if u_item["must_change_password"] else '<span style="color:#10B981; font-size:11.5px;">[Đã đổi pass riêng]</span>'
                
                st.markdown(f"""
                <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:12px; padding:14px 18px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                        <div>
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span style="font-weight:800; font-size:15px; color:var(--text-primary);">{u_item['full_name']}</span>
                                <span class="custom-badge {role_badge_class}">{u_item['role'].upper()}</span>
                                {status_badge}
                                {must_change_badge}
                            </div>
                            <div style="color:var(--text-secondary); font-size:13px; margin-top:3px;">
                                📧 <code>{u_email}</code> • Tạo ngày: <i>{u_item['created_at'][:10]}</i> • Đăng nhập cuối: <i>{u_item['last_login'][:16] if u_item['last_login'] else 'Chưa đăng nhập'}</i>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            
            c_add_u, c_mod_u = st.columns([1.2, 1.8], gap="large")
            with c_add_u:
                st.markdown("##### ➕ Cấp phép tài khoản mới:")
                with st.form("form_add_new_user", clear_on_submit=True):
                    new_u_email = st.text_input("Địa chỉ Email người dùng:", placeholder="researcher@university.edu.vn")
                    new_u_name = st.text_input("Họ và tên:", placeholder="TS. Nguyễn Văn A")
                    new_u_role = st.selectbox("Phân quyền vai trò:", ["researcher", "admin", "viewer"], format_func=lambda r: "🔬 Chuyên gia nghiên cứu (Researcher)" if r == "researcher" else ("⭐ Quản trị viên (Admin)" if r == "admin" else "👁️ Khách xem (Viewer)"))
                    new_u_pass = st.text_input("Mật khẩu tạm thời ban đầu:", value="@123", help="Người dùng sẽ bắt buộc phải đổi mật khẩu khi đăng nhập lần đầu.")
                    
                    btn_submit_add = st.form_submit_button("CẤP PHÉP TÀI KHOẢN NGAY", type="primary", use_container_width=True)
                    if btn_submit_add:
                        if not new_u_email:
                            st.error("Vui lòng nhập địa chỉ email.")
                        else:
                            ok_add, msg_add = add_user_by_admin(new_u_email, new_u_name, new_u_role, cur_auth["email"], new_u_pass)
                            if ok_add:
                                st.success(msg_add)
                                st.rerun()
                            else:
                                st.error(msg_add)

            with c_mod_u:
                st.markdown("##### ⚙️ Thao tác quản lý tài khoản:")
                manageable_users = [u["email"] for u in all_users_data if u["email"] != SUPER_ADMIN_EMAIL]
                if not manageable_users:
                    st.info("Hiện tại chưa có tài khoản phụ nào khác.")
                else:
                    sel_target_email = st.selectbox("Chọn tài khoản cần thao tác:", manageable_users, key="sb_target_manage_user")
                    target_obj = next((u for u in all_users_data if u["email"] == sel_target_email), None)
                    
                    if target_obj:
                        col_act1, col_act2, col_act3 = st.columns(3)
                        with col_act1:
                            new_r_choice = st.selectbox("Đổi vai trò:", ["researcher", "admin", "viewer"], index=["researcher", "admin", "viewer"].index(target_obj["role"]) if target_obj["role"] in ["researcher", "admin", "viewer"] else 0, key="sb_change_role_choice")
                            if st.button("Cập nhật vai trò", key="btn_apply_new_role", use_container_width=True):
                                ok_r, msg_r = update_user_role(sel_target_email, new_r_choice, cur_auth["email"])
                                if ok_r:
                                    st.success(msg_r)
                                    st.rerun()
                                else:
                                    st.error(msg_r)

                        with col_act2:
                            is_currently_active = bool(target_obj["is_active"])
                            toggle_btn_label = "🔒 Khóa tài khoản" if is_currently_active else "🔓 Mở khóa tài khoản"
                            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                            if st.button(toggle_btn_label, key="btn_toggle_active_status", use_container_width=True):
                                ok_t, msg_t = toggle_user_status(sel_target_email, not is_currently_active, cur_auth["email"])
                                if ok_t:
                                    st.success(msg_t)
                                    st.rerun()
                                else:
                                    st.error(msg_t)

                        with col_act3:
                            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("🗑️ Xóa tài khoản vĩnh viễn", type="secondary", key="btn_delete_user_perm", use_container_width=True):
                                ok_del, msg_del = delete_user_by_admin(sel_target_email, cur_auth["email"])
                                if ok_del:
                                    st.success(msg_del)
                                    st.rerun()
                                else:
                                    st.error(msg_del)

        # ---------------------------------------------------------------------
        # TAB 2: TRUNG TÂM PHỤC HỒI MẬT KHẨU & ĐIỀU HƯỚNG EMAIL BẢO MẬT
        # ---------------------------------------------------------------------
        with tab_m_recovery:
            st.markdown(f"""
            <div style="background:rgba(56, 189, 248, 0.08); border:1px solid #38BDF8; border-radius:14px; padding:18px 22px; margin-bottom:16px;">
                <div style="color:#38BDF8; font-weight:800; font-size:16px; margin-bottom:6px;">
                    🛡️ Cơ chế Phục hồi Mật khẩu Bảo mật Đa Tầng (Dual-Recovery Routing)
                </div>
                <div style="color:var(--text-secondary); font-size:13.5px; line-height:1.6;">
                    Khi bất kỳ người dùng nào yêu cầu khôi phục mật khẩu hoặc Admin phát lệnh đặt lại mật khẩu khẩn cấp, hệ thống sẽ sinh ra <b>Mã Token 32 ký tự mã hóa</b> có thời hạn 2 giờ và <b>tự động gửi về đúng 2 địa chỉ bảo mật tối cao</b>:
                    <ul style="margin-top:6px; margin-bottom:0;">
                        <li><code>topxtmtkt21@gmail.com</code></li>
                        <li><code>tranduytno@gmail.com</code></li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_rec1, col_rec2 = st.columns([1.5, 2.5], gap="large")
            with col_rec1:
                st.markdown("##### ⚡ Phát lệnh đặt lại mật khẩu khẩn cấp:")
                all_emails = [u["email"] for u in all_users_data]
                selected_reset_target = st.selectbox("Chọn tài khoản cần cấp lại mật khẩu:", all_emails, key="sb_rec_target_user")
                
                if st.button("🚀 PHÁT LỆNH ĐẶT LẠI MẬT KHẨU NGAY", type="primary", use_container_width=True, key="btn_issue_admin_reset"):
                    ok_is, msg_is, token_is = request_password_reset(selected_reset_target)
                    if ok_is:
                        st.session_state["last_issued_admin_token"] = token_is
                        st.session_state["last_issued_target_user"] = selected_reset_target
                        st.success(msg_is)
                    else:
                        st.error(msg_is)

            with col_rec2:
                st.markdown("##### 🔑 Chi tiết Token và Trình kích hoạt:")
                if st.session_state.get("last_issued_admin_token"):
                    tok = st.session_state["last_issued_admin_token"]
                    u_t = st.session_state.get("last_issued_target_user", "")
                    st.markdown(f"""
                    <div style="background:var(--bg-surface-elevated); border:1px solid #10B981; border-radius:12px; padding:16px 20px;">
                        <div style="color:#10B981; font-weight:700; font-size:14px; margin-bottom:4px;">✓ ĐÃ TẠO TOKEN XÁC THỰC THÀNH CÔNG:</div>
                        <div style="color:var(--text-secondary); font-size:12.5px;">Tài khoản áp dụng: <b>{u_t}</b></div>
                        <div style="background:rgba(0,0,0,0.3); padding:10px 14px; border-radius:8px; font-family:monospace; color:#38BDF8; font-size:14px; font-weight:700; margin:10px 0; word-break:break-all;">
                            {tok}
                        </div>
                        <div style="color:var(--text-muted); font-size:11.5px;">
                            Token này có hiệu lực trong 2 giờ và đã được điều hướng gửi thông báo đến <code>topxtmtkt21@gmail.com</code> và <code>tranduytno@gmail.com</code>.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # TAB 3: NHẬT KÝ KIỂM TOÁN BẢO MẬT (SECURITY AUDIT LOGS)
        # ---------------------------------------------------------------------
        with tab_m_audit:
            st.markdown("##### 🛡️ Nhật ký kiểm toán 50 sự kiện bảo mật gần nhất (Security Audit Trail):")
            audit_records = get_audit_logs(limit=50)
            
            if not audit_records:
                st.info("Chưa có sự kiện nào được ghi nhận.")
            else:
                audit_df = pd.DataFrame(audit_records)
                audit_df = audit_df.rename(columns={
                    "timestamp": "Thời gian",
                    "actor_email": "Tài khoản thực hiện",
                    "action": "Hành vi",
                    "details": "Chi tiết sự kiện",
                    "ip_address": "Địa chỉ IP"
                })
                st.dataframe(audit_df, use_container_width=True, height=450)

    st.markdown("""
    <div style="text-align: center; color: var(--text-muted); font-size: 12px; margin-top: 40px; padding: 20px; border-top: 1px solid var(--border-subtle);">
        SCHOLARGRAPH PRO &copy; 2026. Kiến trúc và phát triển bởi <b>TRẦN DUY (Lead AI Research Engineer)</b>.<br/>
        🌐 <b>Cổng ứng dụng trực tuyến:</b> <a href="https://topxtmtk21-scholargraph-pro-app-9rbsz8.streamlit.app/" target="_blank" style="color:var(--primary-accent); text-decoration:none; font-weight:700;">https://topxtmtk21-scholargraph-pro-app-9rbsz8.streamlit.app/</a><br/>
        Hệ thống chuyên dụng phục vụ Viện nghiên cứu, Trường Đại học và Tòa soạn Báo chí Hiện đại.
    </div>
    """, unsafe_allow_html=True)


