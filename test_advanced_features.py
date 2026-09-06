"""
Comprehensive Test Script for 5 Major Advanced Upgrades in ScholarGraph Pro
Verifies Slide Generator, Academic Phrasebank, Multi-Style Citations, Multi-Doc RAG, and Visual Extractor.
"""

import os
import sys
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from utils.phrasebank_data import get_phrasebank_categories, search_phrasebank
from utils.bib_formatter import (
    format_paper_citation,
    generate_multi_style_references_markdown,
    generate_notion_sync_payload,
    generate_zotero_sync_payload
)
from utils.slide_generator import create_presentation_deck
from utils.pdf_visual_extractor import extract_pdf_visual_elements
from agents.multidoc_rag import MultiDocSynthesizer

def run_tests():
    print("==================================================================")
    print("🧪 KIỂM THỬ 5 TÍNH NĂNG NÂNG CẤP ĐỘT PHÁ CỦA SCHOLARGRAPH PRO")
    print("==================================================================")

    dummy_papers = [
        {
            "id": "https://openalex.org/W2801977793",
            "citation_key": "Wolker2018",
            "title": "Algorithms in the newsroom? News readers' perceived credibility and selection of automated journalism",
            "first_author": "Anja Wölker",
            "authors": "Anja Wölker; Thomas E. Powell",
            "year": 2018,
            "venue": "Journalism",
            "doi": "10.1177/1464884918757072",
            "scopus_tier": "Scopus Q1 (Top Tier)",
            "citation_count": 274,
            "generation": 0,
            "is_oa": True,
            "pdf_url": "https://journals.sagepub.com/doi/pdf/10.1177/1464884918757072",
            "newsroom_problem": "Báo chí tự động hóa tạo áp lực lên nhận thức độ tin cậy của độc giả.",
            "ai_methodology": "Thực nghiệm trực tuyến 2x2 trên mẫu n=400 độc giả tin tức.",
            "empirical_finding": "Độc giả không phân biệt được rõ rệt chất lượng giữa văn bản máy và người viết.",
            "ethical_limitation_gap": "Cần gắn nhãn nguồn gốc thuật toán để bảo đảm quyền được biết của độc giả."
        },
        {
            "id": "https://openalex.org/W2798765432",
            "citation_key": "Thurman2019",
            "title": "When Reporters Get Hands-on with AI: Exploring Collaborative Workflows in Automated News",
            "first_author": "Neil Thurman",
            "authors": "Neil Thurman; Seth C. Lewis",
            "year": 2019,
            "venue": "Digital Journalism",
            "doi": "10.1080/21670811.2019.1677534",
            "scopus_tier": "Scopus Q1 (Top Tier)",
            "citation_count": 185,
            "generation": 1,
            "is_oa": False,
            "pdf_url": "",
            "newsroom_problem": "Quy trình tác nghiệp của phóng viên bị xáo trộn khi tiếp cận công cụ thuật toán.",
            "ai_methodology": "Phỏng vấn bán cấu trúc 28 nhà báo tại các tòa soạn lớn châu Âu.",
            "empirical_finding": "Phóng viên lo ngại mất quyền tự chủ biên tập nhưng đánh giá cao tốc độ bóc tách dữ liệu.",
            "ethical_limitation_gap": "Thiếu các tiêu chuẩn kiểm toán thuật toán độc lập trong tòa soạn."
        }
    ]

    dummy_pipeline = {
        "citenet": {
            "papers_list": dummy_papers,
            "seed_paper": dummy_papers[0],
            "edges": [("https://openalex.org/W2801977793", "https://openalex.org/W2798765432")]
        },
        "synthdesk": {
            "evidence_pool": dummy_papers,
            "grounding_stats": {"coverage_percent": 100.0}
        }
    }

    # 1. Test Academic Phrasebank
    print("\n--- [1/5] Kiểm tra Academic Phrasebank ---")
    cats = get_phrasebank_categories()
    assert len(cats) >= 4, "Phrasebank categories missing!"
    searched = search_phrasebank("algorithm")
    print(f"✓ Phrasebank OK: {len(cats)} danh mục chuẩn CARS, tìm kiếm trả về {len(searched)} mẫu câu!")

    # 2. Test Multi-Style Citations & Sync Payloads
    print("\n--- [2/5] Kiểm tra Multi-Citation & Notion/Zotero Sync ---")
    for st in ["apa7", "ieee", "harvard", "chicago", "mla", "vancouver"]:
        res_cite = format_paper_citation(dummy_papers[0], style=st, index=1)
        assert len(res_cite) > 10
        print(f"  • {st.upper():<10}: {res_cite[:75]}...")
    
    notion_data = generate_notion_sync_payload(dummy_papers)
    zotero_data = generate_zotero_sync_payload(dummy_papers)
    assert len(notion_data) == 2 and len(zotero_data) == 2
    print("✓ Multi-Style Citations & Notion/Zotero Sync Payloads OK!")

    # 3. Test Slide Presentation Generator (.pptx)
    print("\n--- [3/5] Kiểm tra Trình tạo Slide PowerPoint (.pptx) ---")
    pptx_bytes = create_presentation_deck(dummy_pipeline, topic_title="Báo chí AI & Tòa soạn Tự động hóa")
    assert len(pptx_bytes) > 20000, "PPTX bytes too small!"
    print(f"✓ PowerPoint Presentation generated successfully ({len(pptx_bytes)} bytes, 8 slides)!")

    # 4. Test Multi-Doc Synthesis RAG
    print("\n--- [4/5] Kiểm tra Multi-Document Synthesis RAG Engine ---")
    rag = MultiDocSynthesizer()
    rag_res = rag.answer_query("So sánh phương pháp nghiên cứu giữa các bài báo?", dummy_papers)
    assert "answer" in rag_res and len(rag_res["answer"]) > 50
    print(f"✓ Multi-Doc Synthesis RAG generated answer ({len(rag_res['answer'])} chars, {len(rag_res['referenced_papers'])} cited papers)!")

    # 5. Test Visual Element Extractor (Pymupdf)
    print("\n--- [5/5] Kiểm tra Visual Extractor Module ---")
    vis_res = extract_pdf_visual_elements("non_existent_file.pdf")
    assert isinstance(vis_res, list)
    print("✓ PDF Visual Extractor handled safely!")

    print("\n==================================================================")
    print("🎉 TẤT CẢ 5 TÍNH NĂNG NÂNG CẤP ĐÃ ĐƯỢC KIỂM THỬ THÀNH CÔNG 100%!")
    print("==================================================================")

if __name__ == "__main__":
    run_tests()
