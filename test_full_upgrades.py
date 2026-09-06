import os
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_upgrades():
    print("=== [1/5] KIỂM TRA MODULE PDF PARSER & COPILOT ===")
    from utils.pdf_parser import extract_pdf_pages, chunk_pdf_document, search_relevant_chunks
    from agents.pdf_copilot import PDFCopilotAgent
    print("✓ utils.pdf_parser & agents.pdf_copilot import thành công!")

    print("\n=== [2/5] KIỂM TRA FILE IMPORTER (.BIB, .RIS, SEARCH) ===")
    from utils.file_importer import parse_bibtex_string, parse_ris_string, search_works_by_keyword
    sample_bib = """
    @article{Beckett2023,
      author = {Charlie Beckett},
      title = {Generating Change: A Global Survey of AI in Journalism},
      journal = {LSE Journalism AI Report},
      year = {2023},
      doi = {10.1177/1464884918757072}
    }
    """
    bib_res = parse_bibtex_string(sample_bib)
    assert len(bib_res) == 1, "BibTeX parsing failed"
    assert bib_res[0]["doi"] == "10.1177/1464884918757072", "DOI extraction failed"
    print(f"✓ BibTeX parsed successfully: {bib_res[0]['title']} (DOI: {bib_res[0]['doi']})")

    sample_ris = """
    TY  - JOUR
    TI  - Automated Journalism in Newsrooms
    AU  - Diakopoulos, Nicholas
    PY  - 2019
    DO  - 10.1080/17512786.2017.1320773
    ER  - 
    """
    ris_res = parse_ris_string(sample_ris)
    assert len(ris_res) == 1, "RIS parsing failed"
    assert ris_res[0]["doi"] == "10.1080/17512786.2017.1320773", "RIS DOI extraction failed"
    print(f"✓ RIS parsed successfully: {ris_res[0]['title']} (DOI: {ris_res[0]['doi']})")

    print("\n=== [3/5] KIỂM TRA ANALYTICS VIZ (TIMELINE & HEATMAP) ===")
    from utils.analytics_viz import create_evolution_timeline_chart, create_research_gap_heatmap
    dummy_papers = [
        {"title": "AI in News", "first_author": "Beckett", "year": 2023, "citation_count": 45, "study_type": "Newsroom & Workflow AI", "scopus_tier": "Scopus Q1", "ai_methodology": "survey n=100"},
        {"title": "Ethics of LLM", "first_author": "Diakopoulos", "year": 2020, "citation_count": 120, "study_type": "Ethical & Governance", "scopus_tier": "Scopus Q1", "ai_methodology": "experiment"}
    ]
    fig_time = create_evolution_timeline_chart(dummy_papers)
    fig_gap, rep = create_research_gap_heatmap(dummy_papers)
    assert fig_time is not None, "Timeline figure creation failed"
    assert fig_gap is not None, "Heatmap figure creation failed"
    print("✓ Plotly Timeline & Gap Heatmap generated successfully!")

    print("\n=== [4/5] KIỂM TRA SQLITE WORKSPACE DATABASE ===")
    from utils.workspace_db import save_project, list_projects, load_project, delete_project
    pid = save_project("Test Auto Project", "10.1177/1464884918757072", {"citenet": {"stats": {"total_papers": 20}}})
    assert pid > 0, "Save project failed"
    projs = list_projects()
    assert len(projs) > 0, "List projects failed"
    loaded = load_project(pid)
    assert loaded["name"] == "Test Auto Project", "Load project failed"
    delete_project(pid)
    print(f"✓ SQLite database CRUD passed (Project #{pid} created, loaded, and cleaned)!")

    print("\n=== [5/5] KIỂM TRA MAIN APP IMPORTS ===")
    import app
    print("✓ app.py imports and initializes with code 0!")

    print("\n🎉 TOÀN BỘ 4 NHÓM NÂNG CẤP ĐÃ ĐƯỢC KIỂM THỬ THÀNH CÔNG RỰC RỠ 100%!")

if __name__ == "__main__":
    test_upgrades()
