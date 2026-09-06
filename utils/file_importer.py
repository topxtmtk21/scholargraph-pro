import re
import os
import requests
from typing import List, Dict, Any, Optional, Union

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def parse_bibtex_string(bib_str: str) -> List[Dict[str, Any]]:
    """
    Parse BibTeX text and extract entries with title, authors, year, journal, doi.
    """
    entries = []
    # Match each @entry_type{key, ...}
    raw_entries = re.split(r"@\w+\s*\{", bib_str)
    
    for raw in raw_entries:
        if not raw.strip():
            continue
        
        entry_lines = raw.split("\n")
        citation_key = entry_lines[0].split(",")[0].strip() if entry_lines else ""
        
        # Regex to extract fields like title = {...} or doi = "..."
        field_matches = re.findall(r'(\w+)\s*=\s*[\{\"]([\s\S]*?)[\}\"]\s*[,|\n]', raw)
        fields = {k.lower(): v.strip() for k, v in field_matches}
        
        title = fields.get("title", "")
        author = fields.get("author", "")
        year = fields.get("year", "")
        journal = fields.get("journal", "") or fields.get("booktitle", "")
        doi = fields.get("doi", "")
        
        # Normalize DOI
        if doi:
            doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", doi)
            doi = doi_match.group(0).rstrip(".,;") if doi_match else doi
            
        if title or doi:
            entries.append({
                "citation_key": citation_key,
                "title": title,
                "author": author,
                "year": year,
                "venue": journal,
                "doi": doi
            })
            
    return entries

def parse_ris_string(ris_str: str) -> List[Dict[str, Any]]:
    """
    Parse RIS text (Research Information Systems) standard format.
    """
    entries = []
    current_entry = {}
    current_authors = []
    
    for line in ris_str.split("\n"):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("TY  -"):
            current_entry = {}
            current_authors = []
        elif line.startswith("TI  -") or line.startswith("T1  -"):
            current_entry["title"] = line[5:].strip()
        elif line.startswith("AU  -") or line.startswith("A1  -"):
            current_authors.append(line[5:].strip())
        elif line.startswith("PY  -") or line.startswith("Y1  -"):
            year_match = re.search(r"\b(19\d\d|20\d\d)\b", line[5:])
            current_entry["year"] = year_match.group(1) if year_match else line[5:].strip()[:4]
        elif line.startswith("JO  -") or line.startswith("JF  -") or line.startswith("T2  -"):
            current_entry["venue"] = line[5:].strip()
        elif line.startswith("DO  -"):
            doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", line[5:])
            current_entry["doi"] = doi_match.group(0).rstrip(".,;") if doi_match else line[5:].strip()
        elif line.startswith("ER  -"):
            if current_authors:
                current_entry["author"] = "; ".join(current_authors)
            if current_entry.get("title") or current_entry.get("doi"):
                entries.append(current_entry)
            current_entry = {}
            current_authors = []
            
    return entries

def extract_doi_from_pdf(pdf_path_or_bytes: Union[str, bytes]) -> Optional[str]:
    """
    Extract DOI from the first 2 pages of a PDF using PyMuPDF and regular expressions.
    """
    if not fitz:
        return None

    try:
        if isinstance(pdf_path_or_bytes, bytes):
            doc = fitz.open(stream=pdf_path_or_bytes, filetype="pdf")
        else:
            if not os.path.exists(pdf_path_or_bytes):
                return None
            doc = fitz.open(pdf_path_or_bytes)

        # Inspect first 2 pages
        num_pages = min(2, len(doc))
        combined_text = ""
        for i in range(num_pages):
            combined_text += doc[i].get_text("text") + "\n"
        doc.close()

        # Regular expression for DOI
        doi_match = re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b", combined_text)
        if doi_match:
            doi = doi_match.group(1).rstrip(".,;)")
            return doi
    except Exception as e:
        print(f"Error extracting DOI from PDF: {e}")

    return None

def search_works_by_keyword(query: str, limit: int = 10, email: str = "scholar.researcher@academic.edu.vn") -> List[Dict[str, Any]]:
    """
    Search OpenAlex works API by keywords/title string.
    """
    if not query.strip():
        return []

    url = "https://api.openalex.org/works"
    params = {
        "search": query.strip(),
        "per_page": limit,
        "mailto": email
    }
    headers = {"User-Agent": f"ScholarGraphPro/2.0 (mailto:{email})"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for item in data.get("results", []):
                doi = item.get("doi", "")
                doi_clean = doi.replace("https://doi.org/", "").strip() if doi else ""
                
                title = item.get("title") or "Untitled"
                year = item.get("publication_year") or ""
                authorships = item.get("authorships", [])
                author_names = [a.get("author", {}).get("display_name", "") for a in authorships if a.get("author")]
                first_author = author_names[0] if author_names else "Author"
                
                loc = item.get("primary_location") or {}
                source = loc.get("source") or {}
                venue = source.get("display_name") or "Peer-Reviewed Journal"
                
                results.append({
                    "id": item.get("id", ""),
                    "doi": doi_clean,
                    "title": title,
                    "first_author": first_author,
                    "author_str": "; ".join(author_names[:4]),
                    "year": year,
                    "venue": venue,
                    "cited_by_count": item.get("cited_by_count", 0),
                    "is_oa": item.get("open_access", {}).get("is_oa", False)
                })
            return results
    except Exception as e:
        print(f"Error searching OpenAlex works: {e}")

    return []
