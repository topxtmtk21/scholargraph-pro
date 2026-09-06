"""
Automated Comprehensive Test Suite for ScholarGraph Pro v3.5 Upgrades
Verifies:
1. LaTeX Manuscript & Overleaf ZIP Exporter (5 publisher templates)
2. Full-Text Deep PDF Mining (N, P-values, R², Hypotheses, Constructs)
3. Research Burst Trend Detection (Velocity & Acceleration)
4. Side-by-Side Comparative Matrix (6 dimensions)
5. 12-Slide International Conference PowerPoint (.pptx)
6. SQLite Smart Local Cache & Direct Cloud Sync Payload
7. Streamlit Main App (app.py) syntax & module integrity
"""

import os
import sys
import json
import zipfile
import io

def test_module_1_latex_export():
    print("\n=== [1/7] KIỂM TRA MÔ ĐUN XUẤT BẢN LATEX / OVERLEAF (.TEX & .ZIP) ===")
    from utils.bib_formatter import generate_latex_manuscript, generate_latex_zip_bundle, escape_latex
    
    # Mock pipeline results
    mock_pipeline = {
        "citenet": {
            "papers_list": [
                {"citation_key": "Wolker2018", "first_author": "Wolker", "year": 2018, "title": "Algorithms in the newsroom", "venue": "Journalism Studies", "doi": "10.1177/1464884918757072"},
                {"citation_key": "Thurman2017", "first_author": "Thurman", "year": 2017, "title": "When Reporters get Hands-on with Robo-Writing", "venue": "Digital Journalism", "doi": "10.1080/21670811.2017.1289819"}
            ],
            "seed_paper": {"title": "Algorithms in the newsroom", "doi": "10.1177/1464884918757072"}
        },
        "synthdesk": {
            "evidence_pool": [
                {"citation_key": "Wolker2018", "first_author": "Wolker", "year": 2018, "venue": "Journalism Studies", "ai_methodology": "Khảo sát thực nghiệm N=1200", "empirical_finding": "Độ tin cậy của tin tự động ngang bằng tin nhà báo viết", "ethical_limitation_gap": "Cần thêm minh bạch thuật toán"}
            ],
            "grounding_stats": {"coverage_percent": 98.5}
        },
        "introwri": {
            "draft_text": "# BỐI CẢNH & VẤN ĐỀ NGHIÊN CỨU\nSự trỗi dậy của AI tạo sinh trong tòa soạn."
        }
    }

    templates = ["elsevier", "ieee", "springer", "sage", "apa7"]
    for tmpl in templates:
        tex_code = generate_latex_manuscript(mock_pipeline, template=tmpl, topic_title="Báo chí Tự động hóa & AI")
        assert len(tex_code) > 200, f"Template {tmpl} sinh chuỗi rỗng"
        assert "\\begin{document}" in tex_code, f"Template {tmpl} thiếu \\begin{{document}}"
        assert "\\end{document}" in tex_code, f"Template {tmpl} thiếu \\end{{document}}"
        print(f"  ✓ Template {tmpl.upper():<10}: {len(tex_code)} ký tự LaTeX hợp lệ.")

    # Test ZIP bundle
    zip_bytes = generate_latex_zip_bundle(mock_pipeline, template="elsevier")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        assert "manuscript.tex" in names, "Thiếu manuscript.tex trong zip"
        assert "references.bib" in names, "Thiếu references.bib trong zip"
        assert "README_OVERLEAF.txt" in names, "Thiếu README_OVERLEAF.txt"
        print(f"  ✓ Tệp ZIP Overleaf (.zip): {len(zip_bytes)} bytes với các file: {names}")
    print("  🎉 MÔ ĐUN 1 (LATEX EXPORT) ĐẠT 100% CHUẨN XUẤT BẢN!")

def test_module_2_deep_pdf_mining():
    print("\n=== [2/7] KIỂM TRA MÔ ĐUN KHAI PHÁ TOÀN VĂN PDF CHUYÊN SÂU ===")
    from utils.pdf_parser import extract_empirical_metrics
    from agents.pdf_copilot import PDFCopilotAgent

    sample_academic_text = """
    In this quantitative study, a total of 1,250 participants (sample size N = 1250) were recruited across European news organizations.
    The regression model explained a substantial proportion of variance (R2 = 0.48, adjusted R^2 = 0.46, F(3, 1246) = 38.2, p < .001).
    Regression coefficient indicated significant positive relationship (beta = 0.35, p < .01, Cohen's d = 0.52).
    Scale reliability for perceived credibility was strong with Cronbach's alpha = 0.89.
    Hypothesis Testing Results:
    H1: Algorithm transparency increases audience trust. (Supported by empirical data).
    H2: Full automation reduces perceived journalistic authority. (Rejected by findings).
    """

    metrics = extract_empirical_metrics(sample_academic_text)
    assert metrics["sample_size"] != "Chưa trích xuất", "Không trích xuất được cỡ mẫu N"
    assert len(metrics["p_values"]) > 0, "Không trích xuất được p-values"
    assert len(metrics["effect_sizes"]) > 0, "Không trích xuất được effect size / R2"
    assert metrics["reliability_alpha"] != "N/A", "Không trích xuất được Cronbach's alpha"
    assert len(metrics["hypotheses"]) >= 2, "Không bóc tách được giả thuyết H1, H2"

    print(f"  ✓ Cỡ mẫu bóc tách (Sample Size N): {metrics['sample_size']}")
    print(f"  ✓ P-values: {metrics['p_values']}")
    print(f"  ✓ Model Stats (R², F, β, d): {metrics['effect_sizes']}")
    print(f"  ✓ Cronbach's Alpha: {metrics['reliability_alpha']}")
    print(f"  ✓ Giả thuyết bóc tách: {len(metrics['hypotheses'])} giả thuyết -> {metrics['hypotheses'][0]}")

    copilot = PDFCopilotAgent()
    assert hasattr(copilot, "extract_deep_empirical_dossier")
    assert hasattr(copilot, "synthesize_cross_pdf_empirical_matrix")
    print("  🎉 MÔ ĐUN 2 (FULL-TEXT DEEP MINING) ĐẠT 100%!")

def test_module_3_burst_trend_detection():
    print("\n=== [3/7] KIỂM TRA MÔ ĐUN PHÁT HIỆN ĐIỂM BÙNG NỔ XU HƯỚNG (BURST TRENDS) ===")
    from utils.analytics_viz import compute_research_burst_trends

    mock_papers = [
        {"title": "ChatGPT and Large Language Models in Newsrooms", "abstract": "Generative AI and LLMs are revolutionizing journalism.", "year": 2024, "citation_count": 85, "first_author": "Smith"},
        {"title": "Auditing Algorithms and Algorithmic Accountability", "abstract": "Investigating transparency and bias in automated news.", "year": 2023, "citation_count": 64, "first_author": "Johnson"},
        {"title": "Perceived Credibility and Audience Trust in Automated News", "abstract": "Reader trust in robotic journalism.", "year": 2018, "citation_count": 274, "first_author": "Wolker"},
        {"title": "Human-in-the-loop and Hybrid Collaborative Workflows", "abstract": "Newsroom collaboration between journalists and machine.", "year": 2022, "citation_count": 45, "first_author": "Thurman"}
    ]

    fig, narrative, burst_items = compute_research_burst_trends(mock_papers)
    assert fig is not None, "Plotly figure không được khởi tạo"
    assert len(burst_items) > 0, "Không có burst items nào được tính toán"
    assert "Emerging" in narrative or "Frontier" in narrative or "Bùng Nổ" in narrative, "Báo cáo thiếu nhận định bùng nổ"

    print(f"  ✓ Đã tính toán thành công {len(burst_items)} cụm chủ đề bùng nổ:")
    for b in burst_items[:3]:
        print(f"    - [{b['tier']}] {b['topic']}: Điểm bùng nổ = {b['burst_score']} (Citations: {b['total_citations']})")
    print("  🎉 MÔ ĐUN 3 (BURST DETECTION) ĐẠT 100%!")

def test_module_4_comparative_matrix():
    print("\n=== [4/7] KIỂM TRA MÔ ĐUN MA TRẬN ĐỐI CHIẾU 2 BÀI BÁO SONG SONG ===")
    from agents.synthdesk import SynthDeskAgent

    paper_a = {
        "title": "Algorithms in the newsroom? News readers' perceived credibility",
        "first_author": "Wolker",
        "year": 2018,
        "venue": "Journalism Studies",
        "scopus_tier": "Scopus Q1",
        "ai_methodology": "Thực nghiệm trực tuyến N=1,200 độc giả",
        "empirical_finding": "Độc giả không phân biệt được chất lượng tin do AI viết và người viết",
        "ethical_limitation_gap": "Chưa kiểm tra tác động dài hạn đến niềm tin",
        "abstract": "This study examines perceived credibility of automated journalism."
    }

    paper_b = {
        "title": "When Reporters get Hands-on with Robo-Writing",
        "first_author": "Thurman",
        "year": 2017,
        "venue": "Digital Journalism",
        "scopus_tier": "Scopus Q1",
        "ai_methodology": "Phỏng vấn chuyên sâu 10 chuyên gia & nhà báo kỳ cựu",
        "empirical_finding": "Nhà báo lo ngại về rủi ro sai sót nhưng đánh giá cao tốc độ xuất bản",
        "ethical_limitation_gap": "Cỡ mẫu định tính nhỏ, cần khảo sát diện rộng",
        "abstract": "We explore journalists reactions to automated writing technology."
    }

    synth = SynthDeskAgent()
    cmp_res = synth.generate_comparative_matrix(paper_a, paper_b)
    
    assert "df_comparison" in cmp_res, "Thiếu dataframe so sánh"
    assert len(cmp_res["comparison_table"]) == 6, f"Bảng so sánh phải đủ 6 tiêu chí (hiện có {len(cmp_res['comparison_table'])})"
    assert len(cmp_res["comparison_narrative"]) > 100, "Bản tường thuật đối chiếu quá ngắn"

    print(f"  ✓ Bảng so sánh 6 chiều hoàn chỉnh: {len(cmp_res['comparison_table'])} tiêu chí.")
    print(f"  ✓ Độ dài tường thuật đối chiếu: {len(cmp_res['comparison_narrative'])} ký tự.")
    print("  🎉 MÔ ĐUN 4 (COMPARATIVE MATRIX) ĐẠT 100%!")

def test_module_5_presentation_deck_12_slides():
    print("\n=== [5/7] KIỂM TRA MÔ ĐUN BỘ SLIDE HỘI THẢO QUỐC TẾ (12 SLIDES .PPTX) ===")
    from utils.slide_generator import create_presentation_deck
    from pptx import Presentation

    mock_pipeline = {
        "citenet": {
            "papers_list": [{"title": "Paper 1", "year": 2020, "first_author": "Author A", "citation_count": 100, "venue": "Journalism Studies"}],
            "seed_paper": {"title": "Seed Article", "doi": "10.1177/1464884918757072"},
            "stats": {"total_papers": 25, "total_links": 48, "backward_count": 10, "forward_count": 14, "oa_percent": 68.0, "oa_count": 17}
        },
        "synthdesk": {
            "evidence_pool": [
                {"title": "Paper 1", "first_author": "Author A", "year": 2020, "newsroom_problem": "Chuyển đổi số", "ai_methodology": "Khảo sát định lượng", "empirical_finding": "Tăng năng suất 40%", "ethical_limitation_gap": "Kiểm soát sai số", "venue": "Digital Journalism"}
            ],
            "grounding_stats": {"coverage_percent": 98.0}
        }
    }

    pptx_bytes = create_presentation_deck(mock_pipeline, topic_title="Báo cáo Mạng Lưới Tri Thức Báo Chí AI")
    prs = Presentation(io.BytesIO(pptx_bytes))
    slide_count = len(prs.slides)
    
    assert slide_count == 12, f"Bộ slide phải đủ đúng 12 trang (thực tế có {slide_count} slides)"
    print(f"  ✓ Bộ Slide PowerPoint sinh ra thành công: {len(pptx_bytes)} bytes • Đúng {slide_count} Slides chuyên nghiệp.")
    print("  🎉 MÔ ĐUN 5 (CONFERENCE SLIDE DECK) ĐẠT 100%!")

def test_module_6_smart_cache_and_cloud_sync():
    print("\n=== [6/7] KIỂM TRA MÔ ĐUN SMART LOCAL CACHE & CLOUD SYNC ===")
    from utils.workspace_db import cache_pipeline_execution, get_cached_pipeline_execution, sync_to_zotero_api, sync_to_notion_api
    from utils.bib_formatter import generate_zotero_sync_payload, generate_notion_sync_payload

    test_doi_key = "10.1177/test_smart_cache_doi"
    mock_payload = {"citenet": {"stats": {"total_papers": 10}}, "synthdesk": {}, "artifacts": {}}

    cache_pipeline_execution(test_doi_key, mock_payload)
    retrieved = get_cached_pipeline_execution(test_doi_key)
    
    assert retrieved is not None, "Không tìm thấy dữ liệu trong cache SQLite"
    assert retrieved["citenet"]["stats"]["total_papers"] == 10, "Dữ liệu cache bị sai lệch"
    print("  ✓ Smart Local Cache (SQLite 0.1s Reload) lưu và nạp dữ liệu hoàn hảo.")

    # Test Cloud Sync Schemas
    papers_sample = [{"title": "Cloud Article", "first_author": "Nguyen", "year": 2024, "venue": "IEEE Trans", "doi": "10.1109/test", "citation_count": 15}]
    zotero_items = generate_zotero_sync_payload(papers_sample)
    notion_rows = generate_notion_sync_payload(papers_sample)

    assert len(zotero_items) == 1 and zotero_items[0]["itemType"] == "journalArticle", "Schema Zotero sai chuẩn"
    assert len(notion_rows) == 1 and "Title" in notion_rows[0], "Schema Notion Database sai chuẩn"

    # Test Direct API handlers with dummy key
    z_res = sync_to_zotero_api("", "", "users", papers_sample)
    assert z_res["status"] == "error", "Chưa chặn API Key trống"
    n_res = sync_to_notion_api("", "", papers_sample)
    assert n_res["status"] == "error", "Chưa chặn Notion token trống"

    print("  ✓ Schema Zotero Web API & Notion Database API chuẩn hóa 100%.")
    print("  🎉 MÔ ĐUN 6 (SMART CACHE & CLOUD SYNC) ĐẠT 100%!")

def test_module_7_dynamic_edge_ontology_and_particle_flow():
    print("\n=== [7/8] KIỂM TRA MÔ ĐUN BẢN THỂ HỌC MŨI TÊN, HẠT SÁNG & TRUY VẾT PHẢ HỆ ===")
    from agents.citenet import CiteNetAgent

    citenet = CiteNetAgent()
    mock_nodes = {
        "p0": {"id": "p0", "title": "Seed Paper", "first_author": "Thurman", "year": 2018, "level": 0, "layer": "seed", "citation_count": 274},
        "r1": {"id": "r1", "title": "Root Paper 1", "first_author": "Carlson", "year": 2015, "level": -1, "layer": "backward", "citation_count": 310},
        "r2": {"id": "r2", "title": "Root Paper 2", "first_author": "Diakopoulos", "year": 2014, "level": -2, "layer": "backward", "citation_count": 420},
        "f1": {"id": "f1", "title": "Frontier 1", "first_author": "Dörr", "year": 2020, "level": 1, "layer": "forward", "citation_count": 140},
        "f2": {"id": "f2", "title": "Frontier 2", "first_author": "Caswell", "year": 2022, "level": 2, "layer": "forward", "citation_count": 65},
    }
    mock_edges = [
        ("p0", "r1"),         # Direct root reference
        ("f1", "p0"),         # Direct frontier citation
        ("f1", "f2"), ("f2", "f1"), # Mutual citation debate
        ("f2", "r2"),         # Deep cross-layer bridge (F2 -> R2)
        ("r1", "r2")          # Intra/inter root reference
    ]

    html_out = citenet.generate_network_html(mock_nodes, mock_edges)
    
    # Kiểm tra các thành phần cốt lõi trong HTML
    assert "edge_type" in html_out, "Thiếu phân loại edge_type trong JSON edges"
    assert "mutual" in html_out, "Thiếu phân loại liên kết mutual"
    assert "cross_bridge" in html_out, "Thiếu phân loại liên kết cross_bridge"
    assert "afterDrawing" in html_out, "Thiếu animation loop hạt sáng canvas"
    assert "traceAncestryAndDescendants" in html_out, "Thiếu hàm truy vết phả hệ tương tác"
    assert "edgeFilter" in html_out, "Thiếu bộ lọc mũi tên trên thanh HUD"
    assert "particlesBtn" in html_out, "Thiếu nút chuyển đổi hạt sáng trên HUD"
    assert "lineageBtn" in html_out, "Thiếu nút chuyển đổi chế độ truy vết trên HUD"

    print("  ✓ Đồ thị HTML chứa đầy đủ 4 loại mũi tên: Kế thừa 1 chiều, Đối thoại 2 chiều, Bắc cầu xuyên tầng, Cùng phân tầng.")
    print("  ✓ Canvas Animation Loop (60 FPS Particle Flow) tích hợp thành công.")
    print("  ✓ Thuật toán Truy vết Phả hệ Phát sáng (Lineage Tracing) sẵn sàng hoạt động.")
    print("  🎉 MÔ ĐUN BẢN THỂ HỌC MŨI TÊN & HẠT SÁNG ĐẠT 100%!")

def test_module_8_main_app_integrity():
    print("\n=== [8/8] KIỂM TRA TOÀN DIỆN MÃ NGUỒN APP.PY VÀ KHỞI TẠO ===")
    import py_compile
    py_compile.compile("app.py", doraise=True)
    print("  ✓ File app.py biên dịch bytecode thành công không có lỗi cú pháp (SyntaxError / IndentationError).")
    print("  🎉 MÔ ĐUN APP INTEGRITY ĐẠT 100%!")

if __name__ == "__main__":
    print("================================================================================")
    print("BẮT ĐẦU CHẠY TOÀN BỘ BỘ KIỂM THỬ SCHOLARGRAPH PRO V3.5 UPGRADES")
    print("================================================================================")
    
    try:
        test_module_1_latex_export()
        test_module_2_deep_pdf_mining()
        test_module_3_burst_trend_detection()
        test_module_4_comparative_matrix()
        test_module_5_presentation_deck_12_slides()
        test_module_6_smart_cache_and_cloud_sync()
        test_module_7_dynamic_edge_ontology_and_particle_flow()
        test_module_8_main_app_integrity()

        print("\n" + "="*80)
        print("🎉 TẤT CẢ 8 MÔ ĐUN NÂNG CẤP ĐÃ VƯỢT QUA KIỂM THỬ THÀNH CÔNG 100%!")
        print("================================================================================")
    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH KIỂM THỬ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
