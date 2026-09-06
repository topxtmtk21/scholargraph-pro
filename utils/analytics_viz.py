import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Tuple
from utils.theme_manager import get_theme

def get_plotly_theme_layout(theme_id: str = "obsidian_dark") -> Dict[str, Any]:
    t = get_theme(theme_id)
    c = t["colors"]
    return dict(
        paper_bgcolor=c["plotly_bg"],
        plot_bgcolor=c["bg_surface_elevated"],
        font=dict(family="Plus Jakarta Sans, sans-serif", color=c["plotly_font"], size=12),
        margin=dict(l=50, r=40, t=50, b=50),
        xaxis=dict(gridcolor=c["plotly_grid"], zerolinecolor=c["plotly_grid"]),
        yaxis=dict(gridcolor=c["plotly_grid"], zerolinecolor=c["plotly_grid"])
    )

def create_evolution_timeline_chart(papers_list: List[Dict[str, Any]], theme_id: str = "obsidian_dark") -> go.Figure:
    """
    Generate an interactive publication & citation timeline showing research evolution over years.
    Ensures horizontal, highly readable year labels and rich academic tooltips.
    """
    layout_cfg = get_plotly_theme_layout(theme_id)
    t = get_theme(theme_id)
    c = t["colors"]

    if not papers_list:
        fig = go.Figure()
        fig.update_layout(title="Không có dữ liệu bài báo", **layout_cfg)
        return fig

    years = []
    data = []
    for p in papers_list:
        try:
            yr = int(p.get("year", 2020))
        except (ValueError, TypeError):
            yr = 2020
        years.append(yr)

        cites = p.get("citation_count", 0) or 0
        study_type = p.get("study_type", "Empirical Study")
        scopus = p.get("scopus_tier", "Scopus Indexed")
        title = p.get("title", "Untitled")
        author = p.get("first_author", "Unknown")
        venue = p.get("venue", "Academic Journal")

        data.append({
            "year": yr,
            "citations": cites,
            "study_type": study_type,
            "scopus_tier": scopus,
            "title": title,
            "author": author,
            "venue": venue,
            "display_label": f"{author} ({yr})",
            "size": max(14, min(48, int((cites + 1) ** 0.44 * 5.5 + 8)))
        })

    df = pd.DataFrame(data)
    min_yr = min(years) if years else 2017
    max_yr = max(years) if years else 2026

    # Build multi-trace scatter with custom styling
    fig = px.scatter(
        df,
        x="year",
        y="citations",
        color="study_type",
        size="size",
        hover_name="title",
        custom_data=["author", "study_type", "venue", "scopus_tier"],
        title="📈 Dòng Thời Gian Phát Triển & Tiến Hóa Đề Tài Nghiên Cứu (2017 - 2026)",
        labels={
            "year": "Năm xuất bản",
            "citations": "Số lượt trích dẫn học thuật (Citations)",
            "study_type": "Trường phái nghiên cứu"
        },
        color_discrete_sequence=["#38BDF8", "#34D399", "#FBBF24", "#FB7185", "#A78BFA", "#F472B6"]
    )

    # Clean, human-friendly hovertemplate
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br><br>" +
                      "✍️ <b>Tác giả:</b> %{customdata[0]} (%{x})<br>" +
                      "🏛️ <b>Tạp chí:</b> %{customdata[2]} (%{customdata[3]})<br>" +
                      "📊 <b>Trích dẫn:</b> <b style='color:#38BDF8;'>%{y}</b> lượt<br>" +
                      "🏷️ <b>Trường phái:</b> %{customdata[1]}<extra></extra>"
    )

    fig.update_layout(**layout_cfg)
    fig.update_layout(
        title_font=dict(size=16, color=c["primary_accent"]),
        xaxis=dict(
            title=dict(text="Năm xuất bản (Chronological Year)", font=dict(size=13, color=c["text_secondary"])),
            tickmode="linear",
            tick0=min_yr,
            dtick=1,
            tickangle=0, # BẮT BUỘC NGANG 0 ĐỘ - KHÔNG BAO GIỜ HIỂN THỊ CHỮ DỌC
            tickformat="d", # Định dạng số nguyên 4 chữ số, không dấu phẩy
            gridcolor=c["plotly_grid"],
            zerolinecolor=c["plotly_grid"],
            tickfont=dict(size=12, color=c["text_primary"], family="Plus Jakarta Sans, sans-serif")
        ),
        yaxis=dict(
            title=dict(text="Số lượt trích dẫn học thuật (Citations)", font=dict(size=13, color=c["text_secondary"])),
            gridcolor=c["plotly_grid"],
            zerolinecolor=c["plotly_grid"],
            tickfont=dict(size=11, color=c["text_secondary"])
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor=c["bg_surface"],
            bordercolor=c["border_subtle"],
            borderwidth=1,
            font=dict(color=c["text_primary"], size=11.5)
        )
    )

    return fig

def create_research_gap_heatmap(evidence_pool: List[Dict[str, Any]], theme_id: str = "obsidian_dark") -> Tuple[go.Figure, str]:
    """
    Generate 2D Matrix of Research Themes vs Methodologies identifying under-researched gaps.
    """
    layout_cfg = get_plotly_theme_layout(theme_id)
    t = get_theme(theme_id)
    c = t["colors"]

    themes = [
        "Quy trình tòa soạn & Tự động hóa",
        "Đạo đức, Minh bạch & Trách nhiệm",
        "Độ tin cậy độc giả & Hành vi tiếp nhận",
        "Mô hình ngôn ngữ lớn LLM & Thuật toán"
    ]
    
    methods = [
        "Khảo sát định lượng (Survey)",
        "Thực nghiệm ngẫu nhiên (Experiment)",
        "Phỏng vấn sâu & Định tính (Interview)",
        "Tổng quan hệ thống (Meta-Analysis)"
    ]

    matrix_counts = {th: {m: 0 for m in methods} for th in themes}

    for p in evidence_pool:
        stype = p.get("study_type", "").lower()
        method_desc = (p.get("ai_methodology", "") + " " + p.get("abstract", "")).lower()

        # Classify theme
        if any(k in stype for k in ["newsroom", "workflow", "tòa soạn"]):
            theme_key = themes[0]
        elif any(k in stype for k in ["ethic", "transparency", "đạo đức"]):
            theme_key = themes[1]
        elif any(k in stype for k in ["audience", "trust", "độc giả"]):
            theme_key = themes[2]
        else:
            theme_key = themes[3]

        # Classify methodology
        if any(k in method_desc for k in ["survey", "khảo sát", "bảng hỏi", "mẫu n ="]):
            meth_key = methods[0]
        elif any(k in method_desc for k in ["experiment", "thực nghiệm", "đối chứng"]):
            meth_key = methods[1]
        elif any(k in method_desc for k in ["interview", "phỏng vấn", "chuyên gia", "định tính"]):
            meth_key = methods[2]
        else:
            meth_key = methods[3]

        matrix_counts[theme_key][meth_key] += 1

    z_values = [[matrix_counts[th][m] for m in methods] for th in themes]

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=methods,
        y=themes,
        colorscale=[
            [0.0, "#0F172A"],    # 0 papers (High Opportunity Gap)
            [0.3, "#047857"],    # 1 paper (Under-researched)
            [0.6, "#D97706"],    # 2-3 papers (Moderate)
            [1.0, "#E11D48"]     # 4+ papers (Saturated)
        ],
        text=z_values,
        texttemplate="%{text} bài báo",
        textfont={"size": 13, "color": "white", "family": "Plus Jakarta Sans"},
        hoverongaps=False
    ))

    fig.update_layout(**layout_cfg)
    fig.update_layout(
        title="🎯 Bản Đồ Nhiệt Khoảng Trống Nghiên Cứu (Research Gap & Saturation Heatmap)",
        title_font=dict(size=16, color=c["badge_green_text"]),
        xaxis=dict(
            title=dict(text="Phương pháp nghiên cứu", font=dict(size=13, color=c["text_secondary"])),
            tickangle=0,
            tickfont=dict(size=11.5, color=c["text_primary"])
        ),
        yaxis=dict(
            title=dict(text="Chủ đề học thuật", font=dict(size=13, color=c["text_secondary"])),
            tickfont=dict(size=11.5, color=c["text_primary"])
        )
    )

    # Generate Analytical Narrative
    lowest_cells = []
    highest_cells = []
    for t_idx, th in enumerate(themes):
        for m_idx, m in enumerate(methods):
            cnt = z_values[t_idx][m_idx]
            if cnt == 0:
                lowest_cells.append(f"• **{th}** kết hợp **{m}** (0 bài — *Khoảng trống vàng để xuất bản mới*)")
            elif cnt >= 3:
                highest_cells.append(f"• **{th}** bằng **{m}** ({cnt} bài — *Mức độ bão hòa cao*)")

    gap_report = f"""### 💡 Báo Cáo Phân Tích Khoảng Trống & Cơ Hội Xuất Bản:
1. **Khoảng trống học thuật tiềm năng (Research Gaps - Nên khai thác):**
{chr(10).join(lowest_cells[:3]) if lowest_cells else "• Các chủ đề hiện tại được phân bổ tương đối đồng đều."}

2. **Các khía cạnh đã bão hòa (Saturated Areas - Cần tạo góc nhìn mới):**
{chr(10).join(highest_cells[:3]) if highest_cells else "• Chưa có khu vực nào rơi vào tình trạng quá bão hòa trích dẫn."}
"""

    return fig, gap_report
