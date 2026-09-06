import os
import re
import io
import zipfile
import requests
from typing import List, Dict, Any, Optional, Callable

def sanitize_filename(title: str, author: str = "", year: str = "", max_length: int = 90) -> str:
    """Generate a clean, safe, standard academic filename."""
    # Clean author
    auth_clean = re.sub(r"[^\w\s-]", "", author.split()[0] if author else "Paper").strip()
    year_clean = str(year).strip() if year else "n.d."
    
    # Clean title
    title_clean = re.sub(r"[^\w\s-]", "", title).strip()
    title_clean = re.sub(r"[-\s]+", "_", title_clean)
    
    if len(title_clean) > max_length:
        title_clean = title_clean[:max_length].rstrip("_")
        
    base_name = f"{auth_clean}_{year_clean}_{title_clean}" if auth_clean else f"{year_clean}_{title_clean}"
    base_name = re.sub(r"_+", "_", base_name).strip("_")
    return f"{base_name}.pdf"

def download_single_pdf(
    url: str,
    dest_path: str,
    timeout: int = 30,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Download a single PDF file with stream chunks, academic user-agent, and PDF content validation.
    """
    if not url:
        return {"success": False, "error": "Đường dẫn tải tệp PDF trống (Empty URL)", "size_bytes": 0}
        
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (ScholarGraph Pro Academic Research Client)",
        "Accept": "application/pdf,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8"
    }
    if headers:
        req_headers.update(headers)

    try:
        response = requests.get(url, stream=True, headers=req_headers, timeout=timeout, allow_redirects=True)
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Mã phản hồi HTTP {response.status_code} ({response.reason})",
                "size_bytes": 0
            }

        # Check content type or initial magic bytes
        content_type = response.headers.get("Content-Type", "").lower()
        
        # Stream into temporary byte chunks
        total_bytes = 0
        first_chunk = True
        is_pdf_content = True
        
        # Ensure destination folder exists
        os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
        
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    if first_chunk:
                        first_chunk = False
                        # If Content-Type was HTML and not starting with %PDF, it might be a landing/redirect page
                        if b"%PDF" not in chunk[:1024] and "text/html" in content_type:
                            is_pdf_content = False
                    f.write(chunk)
                    total_bytes += len(chunk)

        # If file is too small or clearly HTML error page
        if total_bytes < 1024 and not is_pdf_content:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return {
                "success": False,
                "error": "Tài liệu trả về trang web HTML thay vì tệp nhị phân PDF (yêu cầu xác thực qua cổng trường)",
                "size_bytes": total_bytes
            }

        size_mb = round(total_bytes / (1024 * 1024), 2)
        return {
            "success": True,
            "dest_path": dest_path,
            "filename": os.path.basename(dest_path),
            "size_bytes": total_bytes,
            "size_mb": size_mb,
            "error": None
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"Hết thời gian kết nối (Timeout sau {timeout}s)", "size_bytes": 0}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Lỗi kết nối mạng: {str(e)}", "size_bytes": 0}
    except Exception as e:
        return {"success": False, "error": f"Lỗi lưu trữ tệp: {str(e)}", "size_bytes": 0}

def batch_download_papers(
    papers: List[Dict[str, Any]],
    target_directory: str,
    progress_callback: Optional[Callable[[int, int, str, Dict[str, Any]], None]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Batch download multiple open-access research papers to a user-specified local folder.
    """
    os.makedirs(target_directory, exist_ok=True)
    
    total = len(papers)
    successful_downloads = []
    failed_downloads = []
    total_downloaded_bytes = 0

    for idx, p in enumerate(papers, 1):
        title = p.get("title", "Untitled")
        author = p.get("first_author", "Author")
        year = p.get("year", "")
        pdf_url = p.get("pdf_url") or p.get("oa_url") or ""
        
        filename = sanitize_filename(title, author, year)
        dest_file_path = os.path.join(target_directory, filename)
        
        if progress_callback:
            progress_callback(idx, total, f"Đang tải ({idx}/{total}): {title[:50]}...", {
                "status": "downloading",
                "index": idx,
                "title": title
            })

        if not pdf_url:
            res = {"success": False, "error": "Không tìm thấy URL tải PDF trực tiếp", "size_bytes": 0}
        else:
            res = download_single_pdf(pdf_url, dest_file_path, timeout=timeout)
            
        paper_result = {
            "paper_id": p.get("id", ""),
            "doi": p.get("doi", ""),
            "title": title,
            "author": author,
            "year": year,
            "pdf_url": pdf_url,
            "filename": filename,
            "dest_path": dest_file_path,
            "success": res["success"],
            "size_mb": res.get("size_mb", 0),
            "size_bytes": res.get("size_bytes", 0),
            "error": res.get("error")
        }

        if res["success"]:
            successful_downloads.append(paper_result)
            total_downloaded_bytes += res.get("size_bytes", 0)
        else:
            failed_downloads.append(paper_result)

        if progress_callback:
            progress_callback(idx, total, f"Đã xử lý ({idx}/{total}): {'✓ Thành công' if res['success'] else '⚠️ Lỗi'}", {
                "status": "completed_item",
                "result": paper_result
            })

    total_size_mb = round(total_downloaded_bytes / (1024 * 1024), 2)

    return {
        "total_requested": total,
        "success_count": len(successful_downloads),
        "fail_count": len(failed_downloads),
        "total_size_mb": total_size_mb,
        "target_directory": os.path.abspath(target_directory),
        "successful_downloads": successful_downloads,
        "failed_downloads": failed_downloads
    }

def create_zip_from_downloaded_files(download_results: List[Dict[str, Any]]) -> bytes:
    """Package all successfully downloaded PDFs into a single in-memory ZIP archive."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for item in download_results:
            if item.get("success") and os.path.exists(item.get("dest_path", "")):
                arcname = item.get("filename", os.path.basename(item["dest_path"]))
                zip_file.write(item["dest_path"], arcname=arcname)
    buffer.seek(0)
    return buffer.getvalue()
