import json
import re
from typing import Dict, Any, List, Optional
from utils.llm_helper import LLMHelper

class PeerReviewerAgent:
    """
    Trợ lý AI mô phỏng quy trình bình duyệt khoa học kép độc lập (Double-Blind Peer Review Simulation).
    Đóng vai trò Reviewer 1 (Phương pháp luận) và Reviewer 2 (Tính mới mẻ & Đóng góp học thuật).
    """
    def __init__(self, llm_helper: Optional[LLMHelper] = None):
        self.llm = llm_helper or LLMHelper(provider="mock")

    def simulate_peer_review(
        self,
        manuscript_text: str,
        evidence_pool: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive, rigorous peer review report with score card and challenging review questions.
        """
        prompt = f"""Bạn là 2 Chuyên gia Phản biện Học thuật Độc lập (Senior Peer Reviewers) của tạp chí Scopus Q1 (Digital Journalism / New Media & Society).
Nhiệm vụ: Đánh giá nghiêm ngặt bản thảo bài báo khoa học sau đây:

BẢN THẢO CẦN PHẢN BIỆN:
\"\"\"
{manuscript_text[:4500]}
\"\"\"

HÃY ĐÁNH GIÁ VÀ XUẤT RA BÁO CÁO PHẢN BIỆN HOÀN CHỈNH BẰNG TIẾNG VIỆT THEO CẤU TRÚC SAU:

### 1. BẢNG ĐIỂM ĐÁNH GIÁ (THANG ĐIỂM 10):
- **Tính mới mẻ & Đột phá (Novelty & Originality):** [Điểm]/10 — [Nhận xét 1 câu]
- **Độ chặt chẽ phương pháp luận (Methodological Rigor):** [Điểm]/10 — [Nhận xét 1 câu]
- **Độ tin cậy & Bám sát dẫn chứng (Evidence Grounding):** [Điểm]/10 — [Nhận xét 1 câu]
- **Tính sắc nét của Khoảng trống nghiên cứu (Research Gap Clarity):** [Điểm]/10 — [Nhận xét 1 câu]
- **Cấu trúc & Văn phong CARS (Writing & Academic Cohesion):** [Điểm]/10 — [Nhận xét 1 câu]
- **ĐIỂM TRUNG BÌNH TỔNG THỂ:** [Điểm TB]/10
- **QUYẾT ĐỊNH XUẤT BẢN DỰ KIẾN:** [Chấp nhận (Accept) / Sửa đổi nhỏ (Minor Revision) / Sửa đổi lớn (Major Revision)]

### 2. Ý KIẾN CỦA PHẢN BIỆN 1 (REVIEWER 1 — PHƯƠNG PHÁP & TÍNH KHÁCH QUAN):
- **Điểm mạnh then chốt:** (2 gạch đầu dòng)
- **Hạn chế cần khắc phục:** (2 gạch đầu dòng)

### 3. Ý KIẾN CỦA PHẢN BIỆN 2 (REVIEWER 2 — TÍNH MỚI & ĐÓNG GÓP THỰC TIỄN):
- **Ý nghĩa đối với giới học thuật & tòa soạn:** (2 gạch đầu dòng)
- **Những điểm còn mơ hồ:** (2 gạch đầu dòng)

### 4. 4 CÂU HỎI CHẤT VẤN KHÓ MÀ TÁC GIẢ BẮT BUỘC PHẢI GIẢI TRÌNH:
1. ...
2. ...
3. ...
4. ...

### 5. 3 KHUYẾN NGHỊ HÀNH ĐỘNG ĐỂ BÀI BÁO ĐẠT CHUẨN ĐĂNG SCOPUS Q1:
1. ...
2. ...
3. ...
"""
        review_md = self.llm.generate(prompt, temperature=0.3)

        # Extract basic score estimate
        score_match = re.search(r"(?i)điểm trung bình.*?:?\s*(\d+(?:\.\d+)?)", review_md)
        avg_score = float(score_match.group(1)) if score_match else 8.5
        
        status = "Minor Revision" if avg_score >= 8.0 else ("Major Revision" if avg_score >= 6.5 else "Reject")

        return {
            "review_report_md": review_md,
            "overall_score": avg_score,
            "decision": status,
            "passed_initial_screen": avg_score >= 7.0
        }
