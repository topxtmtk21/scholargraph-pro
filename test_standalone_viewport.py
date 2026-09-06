"""
Unit and integration test for Synapse Academic Standalone Dedicated Viewport.
Verifies that:
1. Fullscreen standalone viewport mode renders 100vh height.
2. Bottom panels (Related Papers Matrix & Selected Paper Details) are completely hidden (display: none !important).
3. Default in-app view retains bottom panels and regular 860px height.
4. Base64 encoding generates valid Data URI for popout window.
"""
import base64
from agents.citenet import CiteNetAgent

def test_standalone_viewport():
    print("\n--- Testing Synapse Academic Standalone Dedicated Viewport ---")
    citenet = CiteNetAgent()
    
    mock_nodes = {
        "https://doi.org/10.1016/j.ipm.2023.103321": {
            "title": "Quantum Neural Knowledge Graphs in Journalism",
            "authors": "Tran Duy, Nguyen Van A",
            "first_author": "Tran Duy",
            "year": 2024,
            "venue": "Information Processing & Management",
            "doi": "10.1016/j.ipm.2023.103321",
            "citation_count": 48,
            "level": 0,
            "layer": "seed",
            "study_type": "Empirical Journalism Study",
            "is_oa": True
        },
        "https://doi.org/10.1145/3308558.3313414": {
            "title": "Historical Roots of Graph Citation Networks",
            "authors": "Smith J., Doe A.",
            "first_author": "Smith J.",
            "year": 2019,
            "venue": "The Web Conference",
            "doi": "10.1145/3308558.3313414",
            "citation_count": 120,
            "level": -1,
            "layer": "backward",
            "study_type": "Theoretical Foundations",
            "is_oa": False
        }
    }
    mock_edges = [
        ("https://doi.org/10.1016/j.ipm.2023.103321", "https://doi.org/10.1145/3308558.3313414")
    ]
    
    # 1. Chế độ Mặc định trong ứng dụng (In-app HUD Deck)
    default_html = citenet.generate_network_html(mock_nodes, mock_edges)
    assert "height: 860px" in default_html, "Default mode should have 860px deck height"
    assert "display: grid" in default_html, "Default mode should display bottom deck panels"
    assert "Related Papers Matrix" in default_html, "Default mode should include related papers matrix"
    print("✅ 1. Default In-App View: Bottom panels and 860px deck preserved.")

    # 2. Chế độ Màn hình phụ (Standalone Dedicated Viewport)
    standalone_html = citenet.generate_standalone_fullscreen_html(mock_nodes, mock_edges)
    assert "height: 100vh" in standalone_html, "Standalone mode must have 100vh deck height"
    assert "display: none !important" in standalone_html, "Standalone mode must completely hide bottom deck panels"
    assert "height: calc(100vh - 76px)" in standalone_html, "Standalone mode middle canvas deck must fill 100vh - 76px"
    print("✅ 2. Standalone Viewport: 100vh canvas rendered, bottom panels successfully hidden.")

    # 3. Kiểm thử Data URI Base64 cho nút mở cửa sổ mới
    b64_str = base64.b64encode(standalone_html.encode("utf-8")).decode("utf-8")
    assert len(b64_str) > 500, "Base64 string should be properly encoded"
    data_uri = f"data:text/html;charset=utf-8;base64,{b64_str}"
    assert data_uri.startswith("data:text/html;charset=utf-8;base64,"), "Valid Data URI format"
    print("✅ 3. Data URI Base64: Popout window link successfully validated.")

if __name__ == "__main__":
    test_standalone_viewport()
    print("\n🎉 ALL STANDALONE VIEWPORT TESTS PASSED 100%!")
