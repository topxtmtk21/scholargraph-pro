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
