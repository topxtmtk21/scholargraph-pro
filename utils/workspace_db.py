import os
import sqlite3
import json
import time
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "scholar_workspaces.db")

def get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            dois_str TEXT NOT NULL,
            total_papers INTEGER DEFAULT 0,
            summary_stats TEXT,
            pipeline_data TEXT
        );
        """)
    conn.close()

def save_project(name: str, dois_str: str, pipeline_results: Dict[str, Any]) -> int:
    """Save or update a research project workspace into SQLite."""
    init_db()
    conn = get_db_connection()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract brief stats
    c_stats = pipeline_results.get("citenet", {}).get("stats", {})
    total_papers = c_stats.get("total_papers", 0)
    summary_stats = json.dumps(c_stats, ensure_ascii=False)
    
    # Store clean serializable pipeline results (omit raw byte zip)
    clean_results = {
        "citenet": pipeline_results.get("citenet"),
        "synthdesk": pipeline_results.get("synthdesk"),
        "introwri": pipeline_results.get("introwri"),
        "artifacts": pipeline_results.get("artifacts"),
        "apa7_refs_md": pipeline_results.get("apa7_refs_md")
    }
    pipeline_data_str = json.dumps(clean_results, ensure_ascii=False, default=str)

    with conn:
        cursor = conn.execute("""
        INSERT INTO projects (name, created_at, updated_at, dois_str, total_papers, summary_stats, pipeline_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, now_str, now_str, dois_str, total_papers, summary_stats, pipeline_data_str))
        proj_id = cursor.lastrowid

    conn.close()
    return proj_id

def list_projects() -> List[Dict[str, Any]]:
    """List all saved research project workspaces."""
    init_db()
    conn = get_db_connection()
    cursor = conn.execute("SELECT id, name, created_at, updated_at, dois_str, total_papers FROM projects ORDER BY id DESC")
    rows = cursor.fetchall()
    projects = [dict(r) for r in rows]
    conn.close()
    return projects

def load_project(project_id: int) -> Optional[Dict[str, Any]]:
    """Load full workspace state from project ID."""
    init_db()
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None

    data = dict(row)
    try:
        data["pipeline_results"] = json.loads(data.get("pipeline_data") or "{}")
        data["summary_stats"] = json.loads(data.get("summary_stats") or "{}")
    except Exception:
        data["pipeline_results"] = None
        data["summary_stats"] = {}

    return data

def delete_project(project_id: int) -> bool:
    """Delete a research project workspace."""
    init_db()
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.close()
    return True

# -------------------------------------------------------------
# SMART LOCAL QUERY CACHE (0.1s Instant Reload)
# -------------------------------------------------------------
def init_cache_table():
    conn = get_db_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS query_cache (
            query_key TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            pipeline_data TEXT NOT NULL
        );
        """)
    conn.close()

def get_cached_pipeline_execution(dois_str: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached pipeline run from SQLite in 0.1s."""
    init_cache_table()
    q_key = re_normalize_key(dois_str)
    conn = get_db_connection()
    cursor = conn.execute("SELECT pipeline_data FROM query_cache WHERE query_key = ?", (q_key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row["pipeline_data"])
        except Exception:
            return None
    return None

def cache_pipeline_execution(dois_str: str, pipeline_results: Dict[str, Any]) -> None:
    """Save pipeline run to query cache."""
    init_cache_table()
    q_key = re_normalize_key(dois_str)
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    clean_results = {
        "citenet": pipeline_results.get("citenet"),
        "synthdesk": pipeline_results.get("synthdesk"),
        "introwri": pipeline_results.get("introwri"),
        "artifacts": pipeline_results.get("artifacts"),
        "apa7_refs_md": pipeline_results.get("apa7_refs_md")
    }
    data_str = json.dumps(clean_results, ensure_ascii=False, default=str)
    conn = get_db_connection()
    with conn:
        conn.execute("""
        INSERT OR REPLACE INTO query_cache (query_key, created_at, pipeline_data)
        VALUES (?, ?, ?)
        """, (q_key, now_str, data_str))
    conn.close()

def re_normalize_key(s: str) -> str:
    import re
    return "".join(re.findall(r"[a-zA-Z0-9]", s.lower()))

# -------------------------------------------------------------
# DIRECT CLOUD SYNC: ZOTERO & NOTION APIS
# -------------------------------------------------------------
def sync_to_zotero_api(api_key: str, library_id: str, library_type: str = "users", papers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Directly push paper items to Zotero Web API.
    Endpoint: https://api.zotero.org/{users|groups}/{library_id}/items
    """
    import urllib.request
    import urllib.error
    from utils.bib_formatter import generate_zotero_sync_payload

    if not api_key or not library_id:
        return {"status": "error", "message": "Vui lòng nhập đầy đủ Zotero API Key và Library ID."}

    payload = generate_zotero_sync_payload(papers or [])
    if not payload:
        return {"status": "error", "message": "Không có bài báo nào để đồng bộ."}

    # Zotero allows up to 50 items per batch
    batch = payload[:50]
    url = f"https://api.zotero.org/{library_type}/{library_id}/items"
    
    headers = {
        "Zotero-API-Key": api_key.strip(),
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(batch).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            status_code = resp.getcode()
            resp_body = resp.read().decode("utf-8")
            return {
                "status": "success",
                "code": status_code,
                "synced_count": len(batch),
                "message": f"Đã đồng bộ thành công {len(batch)} bài báo vào thư viện Zotero!",
                "response": resp_body[:200]
            }
    except urllib.error.HTTPError as he:
        return {
            "status": "error",
            "code": he.code,
            "message": f"Lỗi Zotero API (Mã {he.code}): {he.reason}. Vui lòng kiểm tra quyền ghi của API Key."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi kết nối Zotero: {str(e)}"
        }

def sync_to_notion_api(api_token: str, database_id: str, papers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Directly push paper items to Notion Database API.
    Endpoint: https://api.notion.com/v1/pages
    """
    import urllib.request
    import urllib.error

    if not api_token or not database_id:
        return {"status": "error", "message": "Vui lòng nhập đầy đủ Notion API Token và Database ID."}

    if not papers:
        return {"status": "error", "message": "Không có danh sách bài báo để đồng bộ."}

    clean_db_id = database_id.replace("-", "").strip()
    headers = {
        "Authorization": f"Bearer {api_token.strip()}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    synced = 0
    errors = []

    for p in papers[:20]: # Sync top 20 papers per run to stay well within rate limits
        title = p.get("title", "Untitled")[:90]
        authors = p.get("authors", "")[:80]
        doi = p.get("doi", "")
        year = int(p.get("year", 2020)) if str(p.get("year", "")).isdigit() else 2020
        cites = p.get("citation_count", 0) or 0
        venue = p.get("venue", "Scopus Journal")[:60]

        page_body = {
            "parent": {"database_id": clean_db_id},
            "properties": {
                "Title": {"title": [{"text": {"content": title}}]},
                "Authors": {"rich_text": [{"text": {"content": authors}}]},
                "Journal": {"rich_text": [{"text": {"content": venue}}]},
                "Year": {"number": year},
                "Citations": {"number": cites}
            }
        }
        if doi:
            page_body["properties"]["DOI"] = {"url": f"https://doi.org/{doi}"}

        try:
            req = urllib.request.Request(
                "https://api.notion.com/v1/pages",
                data=json.dumps(page_body).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.getcode() in [200, 201]:
                    synced += 1
        except urllib.error.HTTPError as he:
            errors.append(f"HTTP {he.code}: {he.reason}")
            break
        except Exception as e:
            errors.append(str(e))
            break

    if synced > 0:
        return {
            "status": "success",
            "synced_count": synced,
            "message": f"Đã đồng bộ thành công {synced} bài báo vào Notion Database!"
        }
    return {
        "status": "error",
        "message": f"Lỗi đồng bộ Notion: {', '.join(errors) if errors else 'Kiểm tra lại quyền truy cập của Integration Token với Database ID.'}"
    }

