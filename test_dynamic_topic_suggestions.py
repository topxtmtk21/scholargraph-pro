import pytest
from utils.openalex_client import (
    JOURNALISM_TOPIC_SUGGESTIONS,
    fetch_dynamic_journalism_dois,
    normalize_doi,
    parse_doi_list
)

def test_topic_structure_and_counts():
    """Verify exactly 2 groups, 10 topics each (total 20 topics)."""
    assert "group_a" in JOURNALISM_TOPIC_SUGGESTIONS
    assert "group_b" in JOURNALISM_TOPIC_SUGGESTIONS
    
    group_a = JOURNALISM_TOPIC_SUGGESTIONS["group_a"]["topics"]
    group_b = JOURNALISM_TOPIC_SUGGESTIONS["group_b"]["topics"]
    
    assert len(group_a) == 10, f"Group A must have 10 topics, got {len(group_a)}"
    assert len(group_b) == 10, f"Group B must have 10 topics, got {len(group_b)}"
    
    all_ids = set()
    for grp in [group_a, group_b]:
        for t in grp:
            assert "id" in t
            assert "title" in t
            assert "field" in t
            assert "desc" in t
            assert "search_query" in t
            assert "default_dois" in t
            assert "venue" in t
            assert "year_range" in t
            
            assert t["id"] not in all_ids, f"Duplicate topic ID: {t['id']}"
            all_ids.add(t["id"])
            
            # Check DOIs
            assert len(t["default_dois"]) >= 2
            for d in t["default_dois"]:
                assert d.startswith("10.") or "/" in d
                clean = normalize_doi(d)
                assert clean.startswith("10.")

def test_dynamic_openalex_fetch():
    """Verify live OpenAlex dynamic query and structured return."""
    res = fetch_dynamic_journalism_dois(
        search_query="generative ai newsroom journalism workflow",
        limit=3,
        min_year=2023
    )
    assert res["success"] is True
    assert len(res["dois"]) >= 1
    assert "10." in res["dois"][0]
    print(f"Dynamic DOIs fetched: {res['dois']}")

def test_dynamic_openalex_fallback():
    """Verify fallback mechanism when query is empty or network fails."""
    fb = ["10.1080/21670811.2023.2255771", "10.1177/14648849231201945"]
    res = fetch_dynamic_journalism_dois(
        search_query="!@#$%^&*()nonexistentqueryxyz999999",
        limit=2,
        min_year=2024,
        fallback_dois=fb
    )
    assert res["success"] is True
    assert len(res["dois"]) >= 2
    assert res["dois"][0] == fb[0]

if __name__ == "__main__":
    test_topic_structure_and_counts()
    test_dynamic_openalex_fetch()
    test_dynamic_openalex_fallback()
    print("ALL 3 TOPIC SUGGESTION TESTS PASSED 100%!")
