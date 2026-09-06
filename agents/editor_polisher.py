import re
from typing import Dict, Any, Optional
from utils.llm_helper import LLMHelper

class EditorPolisherAgent:
    """
    Trợ lý AI chuyên trách hiệu đính, trau chuốt và tinh chỉnh văn phong học thuật chuẩn Scopus Q1.
    """
    def __init__(self, llm_helper: Optional[LLMHelper] = None):
        self.llm = llm_helper or LLMHelper(provider="mock")

    def polish_text(
        self,
        text: str,
        action_type: str = "polish",  # "polish", "expand", "shorten", "cohesion"
        language: str = "vi"
    ) -> Dict[str, Any]:
        """
        Refine, polish, expand, or summarize academic manuscript draft.
        """
        if not text.strip():
            return {"result_text": text, "changes_summary": "Văn bản trống."}

        action_prompts = {
            "polish": """Hãy đóng vai trò là Tổng biên tập tạp chí khoa học Scopus Q1.
Nhiệm vụ: Hiệu đính, trau chuốt văn phong của đoạn văn sau đây để đạt chuẩn mực học thuật quốc tế cao nhất:
- Loại bỏ ngôn từ cảm tính, khẩu ngữ hoặc diễn đạt dài dòng.
- Sử dụng thuật ngữ chuyên môn chính xác, văn phong khách quan, đĩnh đạc và lập luận sắc bén.
- Giữ nguyên toàn bộ các trích dẫn khoa học (như Beckett et al., 2023; Diakopoulos, 2019).
- Giữ nguyên ngôn ngữ gốc của đoạn văn.""",
            "expand": """Hãy đóng vai trò là Nhà nghiên cứu học thuật cấp cao.
Nhiệm vụ: Mở rộng sâu sắc các luận điểm trong đoạn văn sau:
- Bổ sung thêm góc nhìn đa chiều về bối cảnh, cơ chế tác động và ý nghĩa phương pháp luận.
- Làm rõ tính logic giữa các câu, giải thích cặn kẽ các hệ quả thực tiễn.
- Giữ nguyên toàn bộ trích dẫn hiện có và phong cách học thuật trang trọng.""",
            "shorten": """Hãy đóng vai trò là Biên tập viên khoa học.
Nhiệm vụ: Tinh giản, rút gọn đoạn văn sau mà không làm mất đi các luận điểm cốt lõi và bằng chứng khoa học:
- Cắt bỏ các câu từ dư thừa, trùng lặp.
- Cô đọng ý tứ thành các câu văn súc tích, đắt giá, dồn nén thông tin cao độ.
- Giữ nguyên toàn bộ các trích dẫn APA 7.""",
            "cohesion": """Hãy đóng vai trò là Chuyên gia cấu trúc bài báo John Swales CARS.
Nhiệm vụ: Tăng cường tính liên kết (Academic Cohesion & Transitions) cho đoạn văn:
- Sử dụng các liên từ chuyển ý học thuật tự nhiên (e.g., 'Do đó', 'Hơn thế nữa', 'Trái ngược với quan điểm trước đây', 'Các bằng chứng thực nghiệm này chỉ ra rằng').
- Đảm bảo mạch lập luận từ Move 1 (Thiết lập lãnh thổ) ➔ Move 2 (Xác lập khoảng trống) ➔ Move 3 (Chiếm lĩnh vị thế) diễn ra liền mạch."""
        }

        system_inst = action_prompts.get(action_type, action_prompts["polish"])

        prompt = f"""{system_inst}

ĐOẠN VĂN GỐC CẦN XỬ LÝ:
\"\"\"
{text}
\"\"\"

TRẢ VỀ KẾT QUẢ THEO ĐỊNH DẠNG:
[BẢN VĂN ĐÃ TRAU CHUỐT HOÀN CHỈNH]
(Nội dung đoạn văn hoàn chỉnh sau khi xử lý)

[TÓM TẮT ĐIỂM CẢI TIẾN]
(1-2 câu tóm tắt những thay đổi then chốt)
"""
        raw_res = self.llm.generate(prompt, temperature=0.25)

        # Parse output
        if "[BẢN VĂN ĐÃ TRAU CHUỐT HOÀN CHỈNH]" in raw_res:
            parts = raw_res.split("[TÓM TẮT ĐIỂM CẢI TIẾN]")
            res_body = parts[0].replace("[BẢN VĂN ĐÃ TRAU CHUỐT HOÀN CHỈNH]", "").strip()
            res_notes = parts[1].strip() if len(parts) > 1 else "Đã hoàn thành trau chuốt theo chuẩn học thuật."
        else:
            res_body = raw_res.strip()
            res_notes = "Đã hiệu đính và tối ưu hóa văn phong khoa học."

        return {
            "result_text": res_body,
            "changes_summary": res_notes
        }
