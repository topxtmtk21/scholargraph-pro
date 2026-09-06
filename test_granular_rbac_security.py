#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST SUITE: BẢO MẬT ĐĂNG NHẬP & PHÂN QUYỀN ĐA TẦNG CHI TIẾT (GRANULAR RBAC)
SCHOLARGRAPH PRO v3.5 Enterprise Commercial Edition
==============================================================================
"""

import sys
import re
from utils.auth_manager import (
    ROLE_PERMISSIONS,
    has_feature_access,
    get_user_permissions
)

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

def test_granular_rbac():
    print("=" * 75)
    print("🧪 KIỂM THỬ BẢO MẬT & MA TRẬN PHÂN QUYỀN ĐA TẦNG CHI TIẾT (GRANULAR RBAC)")
    print("=" * 75)

    # 1. Test Local Mode (Zero Restrictions)
    print("\n[1/4] Kiểm tra Bản LOCAL (is_cloud=False): Toàn quyền 100% không bị hạn chế...")
    for f_key in ROLE_PERMISSIONS:
        assert has_feature_access("viewer", f_key, is_cloud=False) is True, f"Local mode phải cho phép viewer truy cập {f_key}"
        assert has_feature_access(None, f_key, is_cloud=False) is True, f"Local mode phải cho phép anonymous truy cập {f_key}"
    print("✓ Bản Local: 100% tính năng hoạt động thông suốt, không yêu cầu đăng nhập phiền phức.")

    # 2. Test Cloud Super Admin Role (All Access)
    print("\n[2/4] Kiểm tra Bản CLOUD với vai trò Super Admin...")
    sa_user = {"role": "super_admin", "email": "admin@scholargraph.pro"}
    for f_key in ROLE_PERMISSIONS:
        assert has_feature_access(sa_user, f_key, is_cloud=True) is True, f"Super admin phải có quyền {f_key}"
    print(f"✓ Super Admin: Toàn quyền truy cập {len(ROLE_PERMISSIONS)} module và tính năng con.")

    # 3. Test Cloud Researcher vs Viewer on Synapse Academic Sub-features
    print("\n[3/4] Kiểm tra Ma trận phân quyền chi tiết cho Mạng lưới trích dẫn (Synapse Academic)...")
    researcher_user = {"role": "researcher", "email": "researcher@university.edu.vn"}
    viewer_user = {"role": "viewer", "email": "viewer@guest.edu.vn"}

    # Researcher should have full graph exploration & export
    assert has_feature_access(researcher_user, "synapse_view_graph", is_cloud=True) is True
    assert has_feature_access(researcher_user, "synapse_lineage_trace", is_cloud=True) is True
    assert has_feature_access(researcher_user, "synapse_laser_beam", is_cloud=True) is True
    assert has_feature_access(researcher_user, "synapse_photon_speed", is_cloud=True) is True
    assert has_feature_access(researcher_user, "synapse_standalone_popout", is_cloud=True) is True
    assert has_feature_access(researcher_user, "synapse_export_html", is_cloud=True) is True
    assert has_feature_access(researcher_user, "pipeline_execute", is_cloud=True) is True
    assert has_feature_access(researcher_user, "mod_09_user_admin", is_cloud=True) is False, "Researcher không được quản trị user"

    # Viewer should have view/search only, blocked from popout, export, pipeline run, user admin
    assert has_feature_access(viewer_user, "synapse_view_graph", is_cloud=True) is True, "Viewer được xem đồ thị"
    assert has_feature_access(viewer_user, "synapse_search_focus", is_cloud=True) is True, "Viewer được tìm kiếm node"
    assert has_feature_access(viewer_user, "synapse_view_node_details", is_cloud=True) is True, "Viewer được xem chi tiết node"
    assert has_feature_access(viewer_user, "synapse_standalone_popout", is_cloud=True) is False, "Viewer bị khóa màn hình phụ"
    assert has_feature_access(viewer_user, "synapse_export_html", is_cloud=True) is False, "Viewer bị khóa tải HTML"
    assert has_feature_access(viewer_user, "synapse_lineage_trace", is_cloud=True) is False, "Viewer bị khóa chỉnh phả hệ"
    assert has_feature_access(viewer_user, "pipeline_execute", is_cloud=True) is False, "Viewer bị khóa chạy quét DOI mới"
    assert has_feature_access(viewer_user, "mod_07_settings", is_cloud=True) is False, "Viewer bị khóa cài đặt hệ thống"
    assert has_feature_access(viewer_user, "mod_09_user_admin", is_cloud=True) is False, "Viewer bị khóa quản trị admin"
    print("✓ Phân định chuẩn xác quyền hạn giữa Researcher và Viewer trên bản Cloud.")

    # 4. Static Code Inspection of app.py for Security Compliance
    print("\n[4/4] Kiểm tra mã nguồn app.py: Đảm bảo không còn nút Đăng nhập nhanh 1-Click hoặc lộ email dev trên Cloud...")
    with open("app.py", "r", encoding="utf-8") as f:
        app_content = f.read()

    # Ensure quick admin bypass button is removed
    assert "btn_quick_admin_login" not in app_content, "Phát hiện nút bypass btn_quick_admin_login trong app.py!"
    assert "btn_fill_topxt" not in app_content, "Phát hiện nút autofill btn_fill_topxt trong app.py!"
    assert "btn_fill_tranduy" not in app_content, "Phát hiện nút autofill btn_fill_tranduy trong app.py!"
    
    # Check that cloud login form does not expose developer email in login placeholder/default
    cloud_login_match = re.search(r"if IS_CLOUD_ENV and not st\.session_state\.auth_user:(.*?)(?=# -{10,}|cur_auth =)", app_content, re.DOTALL)
    if cloud_login_match:
        login_block = cloud_login_match.group(1)
        assert "tranduytno@gmail.com" not in login_block, "Email cá nhân tranduytno bị lộ trong khối Login Cloud!"
        assert "topxtmtk21@gmail.com" not in login_block, "Email cá nhân topxtmtk21 bị lộ trong khối Login Cloud!"
        assert "topxtmtkt21@gmail.com" not in login_block, "Email cá nhân topxtmtkt21 bị lộ trong khối Login Cloud!"
    print("✓ Cổng đăng nhập Cloud hoàn toàn sạch sẽ, không có cửa hậu (Backdoor) hay lộ thông tin nhạy cảm.")

    print("\n" + "=" * 75)
    print("🎉 TẤT CẢ 4/4 BÀI TEST BẢO MẬT & PHÂN QUYỀN ĐÃ ĐẠT 100% PASSED!")
    print("=" * 75)

if __name__ == "__main__":
    test_granular_rbac()
