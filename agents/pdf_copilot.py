import os
from typing import List, Dict, Any, Optional
from utils.llm_helper import LLMHelper
from utils.pdf_parser import chunk_pdf_document, search_relevant_chunks, extract_pdf_sections

class PDFCopilotAgent:
    """
    Trợ lý AI Copilot chuyên trách đọc hiểu toàn văn tài liệu PDF.
    Hỏi đáp dựa trên bằng chứng trang sách thực tế từ các tệp PDF đã tải về máy.
    """
    def __init__(self, llm_helper: Optional[LLMHelper] = None):
        self.llm = llm_helper or LLMHelper(provider="mock")
        self.cached_chunks: Dict[str, List[Dict[str, Any]]] = {}

    def index_pdf_files(self, pdf_paths: List[str]) -> int:
        """
        Index multiple PDF files into memory chunks.
        """
        total_chunks = 0
        for path in pdf_paths:
            if os.path.exists(path) and path not in self.cached_chunks:
                chunks = chunk_pdf_document(path)
                self.cached_chunks[path] = chunks
                total_chunks += len(chunks)
        return total_chunks

    def answer_pdf_question(
        self,
        query: str,
        target_pdf_paths: Optional[List[str]] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """
        Answer questions about the papers using grounded retrieval across indexed PDF files.
        """
        if not target_pdf_paths:
            target_pdf_paths = list(self.cached_chunks.keys())

        # Gather all relevant chunks from target PDFs
        all_chunks = []
        for path in target_pdf_paths:
            if path not in self.cached_chunks:
                self.cached_chunks[path] = chunk_pdf_document(path)
            all_chunks.extend(self.cached_chunks.get(path, []))

        if not all_chunks:
            return {
                "answer": "⚠️ Không tìm thấy nội dung văn bản trong các tệp PDF đã chọn. Vui lòng kiểm tra lại đường dẫn tệp PDF trên thiết bị.",
                "citations": [],
                "retrieved_count": 0
            }

        # Retrieve top 5 most relevant chunks
        top_chunks = search_relevant_chunks(all_chunks, query, top_k=5)
        if not top_chunks:
            # Fallback: take first 3 introductory/abstract chunks
            top_chunks = all_chunks[:3]

        context_blocks = []
        citations = []
        for idx, c in enumerate(top_chunks, 1):
            fname = c.get("filename", "Paper.pdf")
            pnum = c.get("page", 1)
            ctext = c.get("chunk_text", "").strip()
            context_blocks.append(f"[ĐOẠN TRÍCH #{idx} — Tệp: {fname} | Trang: {pnum}]\n{ctext}")
            citations.append({
                "source": fname,
                "page": pnum,
                "snippet": ctext[:140] + "..." if len(ctext) > 140 else ctext
            })

        context_str = "\n\n".join(context_blocks)

        prompt = f"""Bạn là Trợ lý Nghiên cứu Khoa học Chuyên sâu (Scholar AI Copilot).
Dưới đây là các đoạn trích xuất thực tế kèm số trang từ các tệp tài liệu PDF:

{context_str}

CÂU HỎI CỦA NHÀ NGHIÊN CỨU:
"{query}"

YÊU CẦU TRẢ LỜI:
1. Trả lời chi tiết, súc tích, khách quan và chuyên nghiệp bằng TIẾNG VIỆT học thuật chuẩn mực.
2. BẮT BUỘC trích dẫn nguồn gốc và số trang cụ thể cho từng luận điểm theo định dạng [Tên tệp, Trang X].
3. Nếu dữ liệu trong đoạn trích chưa đề cập đến câu hỏi, hãy nêu rõ giới hạn thay vì tự suy đoán.
4. Gợi ý 2 câu hỏi mở rộng tiếp theo cho nhà nghiên cứu.
"""
        response_text = self.llm.generate(prompt, temperature=0.2)

        return {
            "answer": response_text,
            "citations": citations,
            "retrieved_count": len(top_chunks),
            "context_used": context_str
        }
