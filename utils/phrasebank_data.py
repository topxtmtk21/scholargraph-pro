"""
Academic Phrasebank Database for ScholarGraph Pro
Curated collection of academic phrases inspired by Manchester Academic Phrasebank & Swales CARS Model.
"""

from typing import Dict, List, Any

ACADEMIC_PHRASEBANK: Dict[str, Dict[str, Any]] = {
    "establishing_territory": {
        "title": "🎯 1. Thiết lập Bối cảnh & Tầm quan trọng (Move 1 - Establishing Territory)",
        "description": "Các mẫu câu khẳng định tính cấp thiết, vị trí trọng yếu của chủ đề nghiên cứu trong thời đại AI & Báo chí số.",
        "phrases": [
            {
                "en": "In recent years, the integration of artificial intelligence into journalism workflows has attracted widespread scholarly and industrial interest.",
                "vi": "Trong những năm gần đây, việc tích hợp trí tuệ nhân tạo vào quy trình tác nghiệp báo chí đã thu hút sự quan tâm sâu rộng từ giới học thuật và công nghiệp truyền thông."
            },
            {
                "en": "Automated content generation has increasingly become a central pillar of contemporary digital newsroom architectures.",
                "vi": "Sản xuất nội dung tự động hóa ngày càng trở thành một trụ cột cốt lõi trong kiến trúc tòa soạn số đương đại."
            },
            {
                "en": "A substantial body of empirical literature underscores the transformative potential of algorithmic systems in news production.",
                "vi": "Một khối lượng lớn tài liệu nghiên cứu thực nghiệm đã nhấn mạnh tiềm năng chuyển đổi mang tính cách mạng của các hệ thống thuật toán trong sản xuất tin tức."
            },
            {
                "en": "Understanding the interaction between automated journalism and human editorial oversight represents a critical frontier in modern communication studies.",
                "vi": "Hiểu rõ sự tương tác giữa báo chí tự động hóa và sự giám sát biên tập của con người đại diện cho một ranh giới then chốt trong nghiên cứu truyền thông hiện đại."
            }
        ]
    },
    "creating_niche": {
        "title": "⚠️ 2. Chỉ ra Khoảng trống & Hạn chế Học thuật (Move 2 - Highlighting Research Gaps)",
        "description": "Các mẫu câu phản biện, chỉ ra điểm nghẽn lý thuyết, mâu thuẫn thực nghiệm hoặc khía cạnh chưa được khảo sát đầy đủ.",
        "phrases": [
            {
                "en": "Despite significant progress in algorithmic efficiency, relatively little empirical research has examined reader perceptions of credibility across diverse news genres.",
                "vi": "Mặc dù đã có những bước tiến đáng kể về hiệu quả thuật toán, tương đối ít nghiên cứu thực nghiệm kiểm tra nhận thức của độc giả về độ tin cậy giữa các thể loại báo chí khác nhau."
            },
            {
                "en": "Previous investigations have predominantly focused on news production mechanics, largely overlooking ethical governance and algorithmic bias.",
                "vi": "Các cuộc điều tra trước đây chủ yếu tập trung vào cơ chế sản xuất tin tức mà phần lớn bỏ qua khía cạnh quản trị đạo đức và thiên vị thuật toán."
            },
            {
                "en": "The existing literature remains inconclusive regarding whether algorithmic transparency notices foster or undermine audience trust.",
                "vi": "Các tài liệu hiện có vẫn chưa đưa ra kết luận thống nhất về việc liệu các thông báo minh bạch thuật toán có thúc đẩy hay làm suy giảm niềm tin của công chúng."
            },
            {
                "en": "To date, empirical evidence exploring the lived experiences of beat journalists collaborating with generative AI tools remains scarce.",
                "vi": "Cho đến nay, bằng chứng thực nghiệm khám phá trải nghiệm thực tế của các phóng viên tuyến đầu khi cộng tác với các công cụ AI tạo sinh vẫn còn rất khan hiếm."
            }
        ]
    },
    "occupying_niche": {
        "title": "🔬 3. Trình bày Phương pháp & Mục tiêu Nghiên cứu (Move 3 - Occupying the Niche)",
        "description": "Các mẫu câu giới thiệu mục đích, phương pháp luận thực nghiệm và thiết kế nghiên cứu cụ thể.",
        "phrases": [
            {
                "en": "To address this empirical gap, the present study employs a mixed-methods design combining survey experiments with in-depth newsroom interviews.",
                "vi": "Nhằm giải quyết khoảng trống thực nghiệm này, nghiên cứu hiện tại áp dụng thiết kế đa phương pháp kết hợp giữa thực nghiệm khảo sát và phỏng vấn sâu tại tòa soạn."
            },
            {
                "en": "This paper aims to systematically evaluate the impact of automated text generation on editorial autonomy and journalistic standards.",
                "vi": "Bài viết này nhằm mục đích đánh giá một cách có hệ thống tác động của việc tạo văn bản tự động đối với quyền tự chủ biên tập và các chuẩn mực đạo đức báo chí."
            },
            {
                "en": "Drawing upon gatekeeping theory and algorithmic affordances, we investigate how journalists negotiate professional boundaries alongside automated agents.",
                "vi": "Dựa trên lý thuyết người gác cổng (gatekeeping) và đặc tính cấu trúc thuật toán, chúng tôi điều tra cách các nhà báo thương lượng ranh giới nghề nghiệp khi làm việc cùng các tác tử tự động."
            },
            {
                "en": "The primary objective of this investigation is to provide a grounded, empirical framework for ethical AI adoption in media organizations.",
                "vi": "Mục tiêu hàng đầu của cuộc điều tra này là cung cấp một khung thực nghiệm có cơ sở vững chắc cho việc ứng dụng AI có đạo đức trong các tổ chức truyền thông."
            }
        ]
    },
    "discussing_findings": {
        "title": "📊 4. Thảo luận Phát hiện & Đóng góp Khoa học (Highlighting Findings & Contributions)",
        "description": "Các mẫu câu khái quát hóa kết quả thực nghiệm, so sánh với các nghiên cứu tiền nhiệm và nêu bật đóng góp mới.",
        "phrases": [
            {
                "en": "Our empirical findings demonstrate a statistically significant difference in perceived credibility when algorithmic authorship is explicitly disclosed.",
                "vi": "Các phát hiện thực nghiệm của chúng tôi chứng minh sự khác biệt có ý nghĩa thống kê về độ tin cậy được cảm nhận khi quyền tác giả thuật toán được công khai rõ ràng."
            },
            {
                "en": "These results challenge the conventional assumption that audience skepticism uniformly penalizes automated journalism.",
                "vi": "Những kết quả này thách thức giả định truyền thống cho rằng sự hoài nghi của độc giả luôn tạo ra định kiến tiêu cực đối với báo chí tự động."
            },
            {
                "en": "This investigation contributes to the emerging field of computational communication by demonstrating how human-in-the-loop workflows safeguard editorial integrity.",
                "vi": "Công trình này đóng góp vào lĩnh vực truyền thông tính toán đang phát triển bằng cách chứng minh cách quy trình có con người kiểm soát (human-in-the-loop) bảo vệ tính toàn vẹn của biên tập."
            },
            {
                "en": "Collectively, these insights offer critical practical implications for newsroom leaders formulating guidelines for responsible AI deployment.",
                "vi": "Tổng thể, những phát hiện sâu sắc này mang lại hàm ý thực tiễn quan trọng cho các nhà lãnh đạo tòa soạn trong việc xây dựng các hướng dẫn triển khai AI có trách nhiệm."
            }
        ]
    }
}

def get_phrasebank_categories() -> Dict[str, Dict[str, Any]]:
    """Return all categories in the academic phrasebank."""
    return ACADEMIC_PHRASEBANK

def search_phrasebank(query: str) -> List[Dict[str, str]]:
    """Search phrasebank entries by keyword in either English or Vietnamese."""
    query_lower = query.lower().strip()
    results = []
    if not query_lower:
        return results

    for cat_id, cat_data in ACADEMIC_PHRASEBANK.items():
        for p in cat_data["phrases"]:
            if query_lower in p["en"].lower() or query_lower in p["vi"].lower():
                results.append({
                    "category_id": cat_id,
                    "category_title": cat_data["title"],
                    "en": p["en"],
                    "vi": p["vi"]
                })
    return results
