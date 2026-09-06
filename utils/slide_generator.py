"""
PowerPoint Presentation Slide Deck Generator for ScholarGraph Pro
Generates professional academic slide decks (.pptx) summarizing research landscape,
methodologies, empirical findings, and APA 7 references.
"""

import io
from typing import Dict, List, Any
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# Premium Academic Presentation Palette
BG_COLOR = RGBColor(15, 23, 42)          # Slate 900
CARD_BG = RGBColor(30, 41, 59)           # Slate 800
ACCENT_CYAN = RGBColor(56, 189, 248)     # Sky 400
ACCENT_GREEN = RGBColor(52, 211, 153)    # Emerald 400
TEXT_WHITE = RGBColor(248, 250, 252)     # White
TEXT_MUTED = RGBColor(148, 163, 184)     # Slate 400
BORDER_COLOR = RGBColor(51, 65, 85)      # Slate 700

def set_slide_background(slide):
    """Set slide background color to dark slate."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def add_header(slide, title_text: str, category_text: str = "SCHOLARGRAPH PRO • BÁO CÁO HỌC THUẬT QUỐC TẾ"):
    """Add standardized top header with category and title."""
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    
    # Category / Super-title
    p0 = tf.paragraphs[0]
    p0.text = category_text.upper()
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_CYAN
    p0.font.name = "Arial"
    
    # Main Title
    p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.font.name = "Arial"

def add_footer(slide, current_page: int, total_pages: int = 8):
    """Add footer with attribution and page number."""
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(8.4), Inches(0.4))
    tf = footer_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"Người phát triển: TRẦN DUY (Lead AI Research Engineer)  |  Trang {current_page}/{total_pages}"
    p.font.size = Pt(9)
    p.font.color.rgb = TEXT_MUTED
    p.font.name = "Arial"

def create_presentation_deck(
    pipeline_results: Dict[str, Any],
    topic_title: str = "Nghiên cứu Báo chí AI & Tòa soạn Tự động hóa"
) -> bytes:
    """
    Generate complete 8-slide academic PowerPoint presentation from pipeline data.
    Returns bytes in-memory for instant download.
    """
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    synth_res = pipeline_results.get("synthdesk", {})
    citenet_res = pipeline_results.get("citenet", {})
    evidence_pool = synth_res.get("evidence_pool", [])
    papers_list = citenet_res.get("papers_list", [])
    seed_paper = citenet_res.get("seed_paper", {})
    grounding_stats = synth_res.get("grounding_stats", {})

    total_slides = 8

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide (Cover)
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(8.0), Inches(3.8))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "BÁO CÁO TỔNG QUAN HỌC THUẬT & MẠNG LƯỚI TRI THỨC"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_CYAN
    p0.font.name = "Arial"

    p1 = tf1.add_paragraph()
    p1.text = topic_title
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.font.name = "Arial"

    p2 = tf1.add_paragraph()
    seed_title = seed_paper.get("title", "") if isinstance(seed_paper, dict) else ""
    p2.text = f"\nBài báo trọng tâm (Seed Paper): {seed_title[:80]}..." if seed_title else "\nPhân tích mạng lưới trích dẫn Scopus Q1/Q2 & Tổng quan bằng chứng thực nghiệm"
    p2.font.size = Pt(13)
    p2.font.italic = True
    p2.font.color.rgb = TEXT_MUTED
    p2.font.name = "Arial"

    p3 = tf1.add_paragraph()
    p3.text = f"\n✦ Công nghệ: ScholarGraph Pro AI  |  Người phát triển: TRẦN DUY (Lead AI Research Engineer)"
    p3.font.size = Pt(11)
    p3.font.color.rgb = ACCENT_GREEN
    p3.font.name = "Arial"

    add_footer(s1, 1, total_slides)

    # -------------------------------------------------------------
    # SLIDE 2: Research Problem & Context (CARS Move 1 & 2)
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "1. Đặt Vấn Đề & Bối Cảnh Tòa Soạn Số")

    cbox2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.8))
    tf2 = cbox2.text_frame
    tf2.word_wrap = True

    p_p1 = tf2.paragraphs[0]
    p_p1.text = "🎯 Bối Cảnh Chuyển Đổi Số & Tác Nghiệp Báo Chí:"
    p_p1.font.size = Pt(15)
    p_p1.font.bold = True
    p_p1.font.color.rgb = ACCENT_CYAN

    # Get sample problem points
    prob_samples = [p.get("newsroom_problem") for p in evidence_pool if p.get("newsroom_problem")][:3]
    if not prob_samples:
        prob_samples = ["Sự phát triển mạnh mẽ của công nghệ AI và mô hình ngôn ngữ lớn đang tái định hình quy trình sản xuất tin tức tại các tòa soạn hiện đại."]

    for item in prob_samples:
        p_sub = tf2.add_paragraph()
        p_sub.text = f"• {item[:160]}..."
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_WHITE
        p_sub.space_before = Pt(8)

    p_gap = tf2.add_paragraph()
    p_gap.text = "\n⚠️ Khoảng Trống Học Thuật Cần Giải Quyết:"
    p_gap.font.size = Pt(15)
    p_gap.font.bold = True
    p_gap.font.color.rgb = RGBColor(251, 113, 133) # Rose

    gap_samples = [p.get("ethical_limitation_gap") for p in evidence_pool if p.get("ethical_limitation_gap")][:2]
    if not gap_samples:
        gap_samples = ["Cần đánh giá thực nghiệm tác động của tính minh bạch thuật toán đến niềm tin độc giả và ranh giới đạo đức tác nghiệp."]

    for g in gap_samples:
        p_sub = tf2.add_paragraph()
        p_sub.text = f"• {g[:160]}..."
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_WHITE
        p_sub.space_before = Pt(6)

    add_footer(s2, 2, total_slides)

    # -------------------------------------------------------------
    # SLIDE 3: Scientometric Landscape & Citation Network
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "2. Toàn Cảnh Mạng Lưới Trích Dẫn & Thẩm Định Scopus")

    cbox3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.8))
    tf3 = cbox3.text_frame
    tf3.word_wrap = True

    p_s1 = tf3.paragraphs[0]
    p_s1.text = "📊 Thống Kê Tổng Quan Mạng Lưới Tri Thức:"
    p_s1.font.size = Pt(15)
    p_s1.font.bold = True
    p_s1.font.color.rgb = ACCENT_CYAN

    p_stat = tf3.add_paragraph()
    p_stat.text = f"• Tổng số công trình thẩm định: {len(papers_list)} bài báo quốc tế chuẩn Scopus Q1/Q2\n" \
                  f"• Số công trình bóc tách chuyên sâu: {len(evidence_pool)} bài (Độ phủ neo ngữ cảnh: {grounding_stats.get('coverage_percent', 100)}%)\n" \
                  f"• Số liên kết trích dẫn chéo: {len(citenet_res.get('edges', []))} quan hệ kế thừa học thuật"
    p_stat.font.size = Pt(13)
    p_stat.font.color.rgb = TEXT_WHITE
    p_stat.space_before = Pt(8)

    p_s2 = tf3.add_paragraph()
    p_s2.text = "\n🌐 5 Chuẩn Trắc Lượng Khoa Học Được Áp Dụng:"
    p_s2.font.size = Pt(14)
    p_s2.font.bold = True
    p_s2.font.color.rgb = ACCENT_GREEN

    p_modes = tf3.add_paragraph()
    p_modes.text = "1. VOSviewer Co-Citation: Nhận diện cụm chủ đề theo lực hút đồng trích dẫn.\n" \
                   "2. HistCite Chronology: Dòng thời gian tiến hóa từ nền tảng lý thuyết đến hiện tại.\n" \
                   "3. Concentric Ego-Network: Quỹ đạo phân bố bán kính (Gen-0, Gen-1, Gen-2).\n" \
                   "4. CiteSpace Hierarchical DAG: Cây phả hệ phân tầng từ gốc đến ngọn.\n" \
                   "5. Scimago/Clarivate Grid: Phân làn uy tín tạp chí (Scopus Q1, Q2, Q3)."
    p_modes.font.size = Pt(11.5)
    p_modes.font.color.rgb = TEXT_MUTED
    p_modes.space_before = Pt(6)

    add_footer(s3, 3, total_slides)

    # -------------------------------------------------------------
    # SLIDE 4: Timeline & Evolutionary Milestones
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "3. Mốc Thời Gian Tiến Hóa & Các Công Trình Trọng Tâm")

    cbox4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.8))
    tf4 = cbox4.text_frame
    tf4.word_wrap = True

    p_t1 = tf4.paragraphs[0]
    p_t1.text = "⏳ Các Mốc Công Bố Tiên Phong & Kế Thừa:"
    p_t1.font.size = Pt(15)
    p_t1.font.bold = True
    p_t1.font.color.rgb = ACCENT_CYAN

    sorted_papers = sorted(papers_list, key=lambda x: str(x.get("year", "2020")))
    for p in sorted_papers[:4]:
        p_item = tf4.add_paragraph()
        auth = p.get("first_author", "Unknown")
        yr = p.get("year", "n.d.")
        cites = p.get("citation_count", 0)
        venue = p.get("venue", "Scopus Journal")
        title = p.get("title", "")[:75]
        p_item.text = f"• [{yr}] {auth} — \"{title}...\" ({venue} • {cites} trích dẫn)"
        p_item.font.size = Pt(12)
        p_item.font.color.rgb = TEXT_WHITE
        p_item.space_before = Pt(8)

    add_footer(s4, 4, total_slides)

    # -------------------------------------------------------------
    # SLIDE 5: AI Technologies & Research Methodologies
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "4. Công Nghệ AI & Phương Pháp Nghiên Cứu Thực Nghiệm")

    cbox5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.8))
    tf5 = cbox5.text_frame
    tf5.word_wrap = True

    p_m1 = tf5.paragraphs[0]
    p_m1.text = "🔬 Tổng Hợp Phương Pháp Luận Được Sử Dụng:"
    p_m1.font.size = Pt(15)
    p_m1.font.bold = True
    p_m1.font.color.rgb = ACCENT_CYAN

    meth_samples = [p.get("ai_methodology") for p in evidence_pool if p.get("ai_methodology")][:4]
    for m in meth_samples:
        p_sub = tf5.add_paragraph()
        p_sub.text = f"• {m[:160]}..."
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_WHITE
        p_sub.space_before = Pt(8)

    add_footer(s5, 5, total_slides)

    # -------------------------------------------------------------
    # SLIDE 6: Key Empirical Findings
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "5. Phát Hiện Thực Nghiệm & Tác Động Tòa Soạn")

    cbox6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.8))
    tf6 = cbox6.text_frame
    tf6.word_wrap = True

    p_f1 = tf6.paragraphs[0]
    p_f1.text = "📊 Các Kết Quả Thực Nghiệm Cốt Lõi:"
    p_f1.font.size = Pt(15)
    p_f1.font.bold = True
    p_f1.font.color.rgb = ACCENT_GREEN

    find_samples = [p.get("empirical_finding") for p in evidence_pool if p.get("empirical_finding")][:4]
    for f in find_samples:
        p_sub = tf6.add_paragraph()
        p_sub.text = f"• {f[:160]}..."
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_WHITE
        p_sub.space_before = Pt(8)

    add_footer(s6, 6, total_slides)

    # -------------------------------------------------------------
    # SLIDE 7: Future Research Agenda
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "6. Đề Xuất Hướng Nghiên Cứu Tương Lai & Khuyến Nghị")

    cbox7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.8))
    tf7 = cbox7.text_frame
    tf7.word_wrap = True

    p_r1 = tf7.paragraphs[0]
    p_r1.text = "💡 Định Hướng Đề Tài Phát Triển Tiềm Năng:"
    p_r1.font.size = Pt(15)
    p_r1.font.bold = True
    p_r1.font.color.rgb = ACCENT_CYAN

    recs = [
        "Nghiên cứu định lượng diện rộng về phản ứng của độc giả đối với tin tức do mô hình LLM đa phương tiện tạo ra.",
        "Xây dựng khung đạo đức và cơ chế kiểm toán thuật toán (algorithmic accountability) cho tòa soạn quy mô vừa và nhỏ.",
        "Đánh giá tác động dài hạn của AI đến kỹ năng phỏng vấn, tư duy phản biện và phúc lợi nghề nghiệp của nhà báo.",
        "Thiết kế mô hình cộng tác Người - Máy (Human-in-the-loop) tối ưu hóa tốc độ xuất bản mà không tổn hại độ tin cậy."
    ]
    for r in recs:
        p_sub = tf7.add_paragraph()
        p_sub.text = f"• {r}"
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_WHITE
        p_sub.space_before = Pt(8)

    add_footer(s7, 7, total_slides)

    # -------------------------------------------------------------
    # SLIDE 8: Selected References (APA 7th)
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "7. Tài Liệu Tham Khảo Chọn Lọc (Chuẩn APA 7th)")

    cbox8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.8))
    tf8 = cbox8.text_frame
    tf8.word_wrap = True

    for p in evidence_pool[:5]:
        p_ref = tf8.add_paragraph() if tf8.paragraphs[0].text else tf8.paragraphs[0]
        auth = p.get("first_author", "Unknown")
        yr = p.get("year", "n.d.")
        title = p.get("title", "")[:60]
        venue = p.get("venue", "Journal")
        doi = p.get("doi", "")
        doi_s = f" https://doi.org/{doi}" if doi else ""
        p_ref.text = f"• {auth} ({yr}). {title}... {venue}.{doi_s}"
        p_ref.font.size = Pt(11)
        p_ref.font.color.rgb = TEXT_MUTED
        p_ref.space_before = Pt(6)

    add_footer(s8, 8, total_slides)

    # Save presentation to in-memory buffer
    out_buf = io.BytesIO()
    prs.save(out_buf)
    out_buf.seek(0)
    return out_buf.getvalue()
