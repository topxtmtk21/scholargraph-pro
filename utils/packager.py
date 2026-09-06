import io
import re
import zipfile
from typing import Dict, Union, Any, Optional
import pandas as pd

def markdown_to_docx(title: str, markdown_text: str, author: str = "TRẦN DUY", subtitle: str = "ScholarGraph Pro — AI Academic Research Dossier") -> bytes:
    """
    Generate professional Microsoft Word / Google Docs (.docx) file from markdown text.
    Developed by TRẦN DUY.
    """
    try:
        import docx
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.style import WD_STYLE_TYPE

        doc = docx.Document()

        # Set standard margins (1 inch / 2.54 cm for APA 7)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

        # Document Title
        p_title = doc.add_paragraph()
        run_title = p_title.add_run(title)
        run_title.font.name = "Times New Roman"
        run_title.font.size = Pt(18)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(17, 24, 39)
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_title.paragraph_format.space_after = Pt(4)

        # Document Subtitle & Metadata
        p_meta = doc.add_paragraph()
        run_meta = p_meta.add_run(f"{subtitle}\nNgười phát triển hệ thống: {author} • Chuẩn xuất bản quốc tế APA 7 & Swales CARS")
        run_meta.font.name = "Times New Roman"
        run_meta.font.size = Pt(10.5)
        run_meta.font.italic = True
        run_meta.font.color.rgb = RGBColor(107, 114, 128)
        p_meta.paragraph_format.space_after = Pt(16)

        # Parse markdown lines
        lines = markdown_text.split("\n")
        in_table = False
        table_rows = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_table and table_rows:
                    # Flush table
                    _add_docx_table(doc, table_rows)
                    in_table = False
                    table_rows = []
                continue

            # Check table line
            if stripped.startswith("|") and stripped.endswith("|"):
                in_table = True
                if not re.match(r"^\|(\s*:?-+:?\s*\|)+$", stripped):
                    cols = [c.strip() for c in stripped[1:-1].split("|")]
                    table_rows.append(cols)
                continue
            else:
                if in_table and table_rows:
                    _add_docx_table(doc, table_rows)
                    in_table = False
                    table_rows = []

            # Headings
            if stripped.startswith("# "):
                h = doc.add_heading(level=1)
                _format_run(h.add_run(stripped[2:]), size=14, bold=True, color=RGBColor(31, 41, 55))
                h.paragraph_format.space_before = Pt(14)
                h.paragraph_format.space_after = Pt(4)
            elif stripped.startswith("## "):
                h = doc.add_heading(level=2)
                _format_run(h.add_run(stripped[3:]), size=12.5, bold=True, color=RGBColor(55, 65, 81))
                h.paragraph_format.space_before = Pt(12)
                h.paragraph_format.space_after = Pt(4)
            elif stripped.startswith("### "):
                h = doc.add_heading(level=3)
                _format_run(h.add_run(stripped[4:]), size=11.5, bold=True, italic=True, color=RGBColor(75, 85, 99))
                h.paragraph_format.space_before = Pt(8)
                h.paragraph_format.space_after = Pt(3)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                p = doc.add_paragraph(style='List Bullet')
                _append_inline_formatted_text(p, stripped[2:])
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.15
            elif re.match(r"^\d+\.\s", stripped):
                match = re.match(r"^\d+\.\s", stripped)
                p = doc.add_paragraph(style='List Number')
                _append_inline_formatted_text(p, stripped[match.end():])
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.15
            elif stripped.startswith("> "):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                p.paragraph_format.space_after = Pt(6)
                _append_inline_formatted_text(p, stripped[2:], italic=True, color=RGBColor(75, 85, 99))
            else:
                p = doc.add_paragraph()
                _append_inline_formatted_text(p, stripped)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.15

        if in_table and table_rows:
            _add_docx_table(doc, table_rows)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        print(f"[markdown_to_docx error] {e}")
        # Return fallback text in byte stream
        return markdown_text.encode("utf-8")

def _format_run(run, size=11, bold=False, italic=False, color=None):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color

def _append_inline_formatted_text(paragraph, text, italic=False, color=None):
    # Regex for bold **text** or italic *text*
    parts = re.split(r"(\*\*.*?\*\*|\*.*?\*|\[.*?\]\(.*?\))", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            _format_run(run, size=11, bold=True, italic=italic, color=color)
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            _format_run(run, size=11, bold=False, italic=True, color=color)
        elif part.startswith("[") and "](" in part and part.endswith(")"):
            m = re.match(r"\[(.*?)\]\((.*?)\)", part)
            if m:
                label, url = m.groups()
                run = paragraph.add_run(f"{label} ({url})")
                _format_run(run, size=10, bold=False, italic=False, color=RGBColor(37, 99, 235))
            else:
                run = paragraph.add_run(part)
                _format_run(run, size=11, italic=italic, color=color)
        else:
            run = paragraph.add_run(part)
            _format_run(run, size=11, italic=italic, color=color)

def _add_docx_table(doc, table_rows):
    if not table_rows:
        return
    cols_count = max(len(r) for r in table_rows)
    table = doc.add_table(rows=len(table_rows), cols=cols_count)
    table.style = 'Table Grid'
    for r_idx, row in enumerate(table_rows):
        for c_idx, cell_text in enumerate(row):
            if c_idx < cols_count:
                cell = table.cell(r_idx, c_idx)
                cell.text = cell_text
                for p in cell.paragraphs:
                    for run in p.runs:
                        _format_run(run, size=9.5, bold=(r_idx == 0))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

def dataframe_to_xlsx(df: pd.DataFrame, sheet_name: str = "Data Matrix") -> bytes:
    """Export pandas DataFrame to standardized Excel (.xlsx) file in RAM."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:30])
    buffer.seek(0)
    return buffer.getvalue()

def generate_printable_html(title: str, markdown_content: str, author: str = "TRẦN DUY") -> str:
    """Generate high-fidelity printable HTML document (for PDF export / browser print)."""
    # Simple markdown to HTML converter for printable view
    content_html = markdown_content.replace("\n", "<br/>")
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} — ScholarGraph Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Times+New+Roman&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: A4;
            margin: 25mm 25mm 25mm 25mm;
        }}
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #111827;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{ font-size: 18pt; font-weight: bold; margin-bottom: 4px; color: #000000; }}
        h2 {{ font-size: 14pt; font-weight: bold; margin-top: 18px; margin-bottom: 6px; border-bottom: 1px solid #E5E7EB; padding-bottom: 4px; }}
        h3 {{ font-size: 12pt; font-style: italic; margin-top: 14px; margin-bottom: 4px; }}
        .doc-meta {{
            font-size: 10pt;
            font-style: italic;
            color: #4B5563;
            margin-bottom: 24px;
            border-bottom: 1.5px solid #111827;
            padding-bottom: 8px;
        }}
        .print-btn {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #2563EB;
            color: #FFFFFF;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .print-btn:hover {{ background: #1D4ED8; }}
        @media print {{
            .print-btn {{ display: none; }}
            body {{ padding: 0; }}
        }}
    </style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">🖨️ In / Lưu file PDF</button>
    <h1>{title}</h1>
    <div class="doc-meta">
        Hệ thống: ScholarGraph Pro • Người phát triển: <b>{author}</b> • Chuẩn APA 7 & Swales CARS
    </div>
    <div class="doc-content">
        {content_html}
    </div>
</body>
</html>"""
    return html_doc

def create_research_bundle_zip(artifacts: Dict[str, Any]) -> bytes:
    """
    Package all research artifacts into a single in-memory ZIP file.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in artifacts.items():
            if content is None:
                continue
            if isinstance(content, str):
                encoded_content = content.encode("utf-8")
            elif isinstance(content, bytes):
                encoded_content = content
            else:
                encoded_content = str(content).encode("utf-8")
            
            zip_file.writestr(filename, encoded_content)
            
    buffer.seek(0)
    return buffer.getvalue()
