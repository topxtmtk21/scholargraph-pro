"""
PDF Visual Element Extractor for ScholarGraph Pro
Extracts embedded figures, charts, diagrams, and table images from academic PDF papers.
"""

import os
import io
import fitz # PyMuPDF
from typing import List, Dict, Any, Optional
from PIL import Image

def extract_pdf_visual_elements(
    pdf_path: str,
    max_images_per_doc: int = 8,
    min_width: int = 150,
    min_height: int = 150
) -> List[Dict[str, Any]]:
    """
    Extract embedded figures, charts, and image diagrams from a single PDF file.
    Returns list of image dicts with image bytes, metadata, page number, and resolution.
    """
    if not os.path.exists(pdf_path):
        return []

    visuals = []
    try:
        doc = fitz.open(pdf_path)
        doc_name = os.path.basename(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                if len(visuals) >= max_images_per_doc:
                    break
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                width = base_image["width"]
                height = base_image["height"]

                # Filter out tiny icons / logos / decorative lines
                if width < min_width or height < min_height:
                    continue

                # Classify visual element
                ratio = width / max(1, height)
                elem_type = "📊 Bảng biểu / Đồ thị" if (0.7 <= ratio <= 2.2) else "🖼️ Sơ đồ / Hình ảnh"

                visuals.append({
                    "doc_name": doc_name,
                    "page_number": page_num + 1,
                    "img_index": img_index + 1,
                    "image_bytes": image_bytes,
                    "image_ext": image_ext,
                    "width": width,
                    "height": height,
                    "elem_type": elem_type,
                    "caption": f"{elem_type} (Trang {page_num + 1} • {width}x{height}px)"
                })
                
        doc.close()
    except Exception as e:
        print(f"Error extracting visuals from {pdf_path}: {e}")

    return visuals

def batch_extract_visuals_from_directory(
    pdf_dir: str,
    max_total_visuals: int = 30
) -> List[Dict[str, Any]]:
    """
    Scan a directory of downloaded PDFs and extract all charts, figures, and table elements.
    """
    if not os.path.exists(pdf_dir):
        return []

    all_visuals = []
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    
    for f in pdf_files:
        if len(all_visuals) >= max_total_visuals:
            break
        full_p = os.path.join(pdf_dir, f)
        doc_visuals = extract_pdf_visual_elements(full_p, max_images_per_doc=6)
        all_visuals.extend(doc_visuals)

    return all_visuals[:max_total_visuals]
