import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import time
import json
import zipfile
import io
from utils.openalex_client import normalize_doi, parse_doi_list, OpenAlexClient
from utils.llm_helper import LLMHelper
from utils.packager import create_research_bundle_zip
from agents.citenet import CiteNetAgent
from agents.synthdesk import SynthDeskAgent
from agents.introwri import IntroWriAgent

def test_journalism_pipeline():
    print("==================================================")
    print("📰 KIỂM THỬ PIPELINE NGHIÊN CỨU BÁO CHÍ & TÒA SOẠN AI")
    print("==================================================")

    # Verified Scopus Q1 DOIs in Journalism / Automated Newsrooms
    # 1. Thurman / Dörr / Caswell (Algorithms in Newsrooms - Journalism Scopus Q1)
    # 2. Caswell & Dörr (Automated Journalism 2.0 - Journalism Practice Scopus Q1)
    journalism_dois = "10.1177/1464884918757072, 10.1080/17512786.2017.1320773"
    doi_list = parse_doi_list(journalism_dois)
    print(f"📌 Parsed {len(doi_list)} Journalism Seed DOIs: {doi_list}")
    assert len(doi_list) == 2, "Should parse exactly 2 DOIs"

    t0 = time.time()

    # 1. Test CiteNet Agent with Journalism & Scopus
    print("\n--- 1. Testing CiteNet Agent (Scopus Q1 Journalism Graph) ---")
    citenet = CiteNetAgent(email="journalism_researcher@university.edu.vn")
    citenet_out = citenet.run(seed_dois=doi_list, gen1_limit=6, gen2_limit=12)
    
    assert citenet_out["nodes"], "Nodes dict should not be empty"
    assert len(citenet_out["seed_papers"]) == 2, "Should have 2 seed papers"
    print(f"✅ CiteNet Journalism OK: {citenet_out['stats']['total_papers']} papers ({citenet_out['stats']['gen0_count']} seeds in {citenet_out['seed_papers'][0]['venue']}), {citenet_out['stats']['total_links']} citation links.")

    # 2. Test SynthDesk Agent with Journalism Dimensions
    print("\n--- 2. Testing SynthDesk Agent (Newsroom & Ethical Dimensions) ---")
    llm = LLMHelper(provider="mock")
    synthdesk = SynthDeskAgent(llm_helper=llm)
    synthdesk_out = synthdesk.run(
        papers_list=citenet_out["papers_list"],
        seed_paper=citenet_out["seed_papers"],
        target_count=10
    )

    assert len(synthdesk_out["evidence_pool"]) > 0, "Evidence pool should have papers"
    assert "newsroom_problem" in synthdesk_out["evidence_pool"][0]
    assert "ethical_limitation_gap" in synthdesk_out["evidence_pool"][0]
    assert synthdesk_out["grounding_stats"]["coverage_percent"] >= 90.0, "Coverage should be high"
    print(f"✅ SynthDesk Journalism OK: {len(synthdesk_out['evidence_pool'])} Scopus curated papers, Coverage: {synthdesk_out['grounding_stats']['coverage_percent']}%.")

    # 3. Test IntroWri Agent with Media Studies CARS
    print("\n--- 3. Testing IntroWri Agent (Digital Journalism CARS Introduction) ---")
    introwri = IntroWriAgent(llm_helper=llm)
    introwri_out = introwri.run(
        evidence_pool=synthdesk_out["evidence_pool"],
        seed_paper=citenet_out["seed_papers"]
    )

    audit_dict = introwri_out["audit_report_dict"]
    print(f"   Audit status: {audit_dict['compliance_status']}")
    print(f"   Verified grounded claims: {audit_dict['metrics']['verified_grounded_claims']}")
    print(f"   Used references: {audit_dict['metrics']['distinct_references_used']}")
    assert "journalism" in introwri_out["introduction_draft_md"].lower() or "newsroom" in introwri_out["introduction_draft_md"].lower()
    assert audit_dict["metrics"]["verified_grounded_claims"] >= 8, "Must meet >=8 claims threshold"
    print(f"✅ IntroWri Journalism OK: Passed automated audit!")

    # 4. Test Packager
    print("\n--- 4. Testing ZIP Packager ---")
    all_artifacts = {
        "network.html": citenet_out["network_html"],
        "refs.csv": citenet_out["refs_csv"],
        "refs.bib": citenet_out["refs_bib"],
        "refs.ris": citenet_out["refs_ris"],
        "evidence_table.csv": synthdesk_out["evidence_table_csv"],
        "evidence_brief.md": synthdesk_out["evidence_brief_md"],
        "introduction_draft.md": introwri_out["introduction_draft_md"],
        "audit_report.json": introwri_out["audit_report_json"]
    }
    zip_data = create_research_bundle_zip(all_artifacts)
    assert len(zip_data) > 500, "Zip bytes should be valid"
    
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        namelist = zf.namelist()
        assert len(namelist) == 8, f"Expected 8 files in ZIP, got {len(namelist)}"
    print(f"✅ Packager OK: 8 artifacts verified in in-memory ZIP ({len(zip_data)} bytes)!")

    elapsed = time.time() - t0
    print(f"\n🎉 KIỂM THỬ BÁO CHÍ & AI TÒA SOẠN VƯỢT QUA THÀNH CÔNG TRONG {elapsed:.2f}s!")

if __name__ == "__main__":
    test_journalism_pipeline()
