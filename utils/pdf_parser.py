import os
import re
from typing import List, Dict, Any, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def is_mupdf_available() -> bool:
    return fitz is not None

def extract_pdf_pages(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from PDF page-by-page with page metadata using PyMuPDF.
    """
    if not os.path.exists(pdf_path):
        return []
    
    if not fitz:
        return []

    pages_data = []
    try:
        doc = fitz.open(pdf_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text") or ""
            # Basic cleanup
            clean_text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
            pages_data.append({
                "page_number": page_idx + 1,
                "text": clean_text,
                "char_count": len(clean_text),
                "word_count": len(clean_text.split())
            })
        doc.close()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        
    return pages_data

def extract_pdf_full_text(pdf_path: str) -> str:
    """Extract full text from PDF."""
    pages = extract_pdf_pages(pdf_path)
    return "\n\n".join([f"--- [Trang {p['page_number']}] ---\n{p['text']}" for p in pages if p['text']])

def extract_pdf_sections(pdf_path: str) -> Dict[str, str]:
    """
    Identify academic sections (Abstract, Introduction, Method, Findings, Discussion, Conclusion).
    """
    full_text = extract_pdf_full_text(pdf_path)
    if not full_text:
        return {}

    section_patterns = {
        "abstract": r"(?i)\b(abstract|tóm tắt)\b([\s\S]*?)(?=\b(1\.?\s*introduction|introduction|giới thiệu|bối cảnh)\b)",
        "introduction": r"(?i)\b(introduction|giới thiệu|1\.?\s*introduction)\b([\s\S]*?)(?=\b(literature review|related work|background|methodology|methods|phương pháp)\b)",
        "methodology": r"(?i)\b(methodology|methods|data and methods|phương pháp nghiên cứu)\b([\s\S]*?)(?=\b(results|findings|kết quả|analysis)\b)",
        "findings": r"(?i)\b(results|findings|empirical analysis|kết quả thực nghiệm)\b([\s\S]*?)(?=\b(discussion|thảo luận|implications|limitations|hạn chế)\b)",
        "discussion": r"(?i)\b(discussion|limitations|thảo luận|ranh giới đạo đức|ethical considerations)\b([\s\S]*?)(?=\b(conclusion|kết luận|references|tài liệu tham khảo)\b)",
        "conclusion": r"(?i)\b(conclusion|concluding remarks|kết luận)\b([\s\S]*?)(?=\b(references|bibliography|tài liệu tham khảo)\b)"
    }

    extracted = {}
    for sec_name, pattern in section_patterns.items():
        match = re.search(pattern, full_text)
        if match:
            # Take captured content
            content = match.group(2).strip() if len(match.groups()) >= 2 else match.group(0).strip()
            # Trim excessive length
            if len(content) > 6000:
                content = content[:6000] + "... [Đã rút gọn]"
            extracted[sec_name] = content

    return extracted

def chunk_pdf_document(pdf_path: str, chunk_size: int = 1200, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Split PDF into overlapping text chunks with page tracking for grounded AI retrieval.
    """
    pages = extract_pdf_pages(pdf_path)
    chunks = []
    filename = os.path.basename(pdf_path)

    for p in pages:
        p_num = p["page_number"]
        p_text = p["text"]
        if not p_text:
            continue

        words = p_text.split()
        if len(words) <= 180:
            chunks.append({
                "filename": filename,
                "pdf_path": pdf_path,
                "page": p_num,
                "chunk_text": p_text
            })
            continue

        # Split into multi-word chunks
        cur_idx = 0
        step = max(50, 180 - 40)
        while cur_idx < len(words):
            chunk_words = words[cur_idx:cur_idx + 180]
            chunk_str = " ".join(chunk_words)
            chunks.append({
                "filename": filename,
                "pdf_path": pdf_path,
                "page": p_num,
                "chunk_text": chunk_str
            })
            cur_idx += step

    return chunks

def search_relevant_chunks(chunks: List[Dict[str, Any]], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve top-k relevant chunks matching the query using lexical and token-overlap scoring.
    """
    if not chunks or not query:
        return []

    q_tokens = set(re.findall(r"\w+", query.lower()))
    scored_chunks = []

    for c in chunks:
        text = c.get("chunk_text", "").lower()
        score = 0
        for token in q_tokens:
            if len(token) > 2:
                # Count occurrences
                count = text.count(token)
                score += count * (len(token) ** 0.5)

        if score > 0:
            scored_chunks.append((score, c))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_chunks[:top_k]]
