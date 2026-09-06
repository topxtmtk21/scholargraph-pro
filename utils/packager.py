import io
import re
import zipfile
from typing import Dict, Union, Any, Optional
import pandas as pd

try:
    import docx
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    docx = None
    Pt = Inches = RGBColor = WD_ALIGN_PARAGRAPH = None

def _clean_xml_string(text: str) -> str:
    """Strip invalid XML control characters that cause Word/Google Docs parsing errors."""
    if not isinstance(text, str):
        text = str(text)
    # Remove control characters except newline (\n), carriage return (\r), and tab (\t)
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

def _strip_markdown_formatting(text: str) -> str:
    """Remove raw markdown syntax symbols (###, **, *, _, `, [], ()) for clean text presentation."""
    if not text:
        return ""
    t = str(text)
    # Remove markdown links [text](url) -> text
    t = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", t)
    # Remove bold & italic
    t = re.sub(r"\*\*+(.*?)\*\*+", r"\1", t)
    t = re.sub(r"\*+(.*?)\*+", r"\1", t)
    t = re.sub(r"__+(.*?)__+", r"\1", t)
    t = re.sub(r"`+(.*?)`+", r"\1", t)
    # Remove heading markers at start of lines
    t = re.sub(r"^#+\s*", "", t)
    return t.strip()

def markdown_to_docx(title: str, markdown_text: str, author: str = "TRẦN DUY", subtitle: str = "ScholarGraph Pro — AI Academic Research Dossier") -> bytes:
    """
    Generate professional Microsoft Word & Google Docs (.docx) file from markdown text.
    100% compliant with MS Word 2016+, Office 365, and Google Docs import.
    Developed by TRẦN DUY.
    """
    try:
        import docx
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = docx.Document()

        # Set standard margins (1 inch / 2.54 cm for APA 7)
        for section in doc.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

        # Document Title
        p_title = doc.add_paragraph()
        run_title = p_title.add_run(_clean_xml_string(_strip_markdown_formatting(title)))
        run_title.font.name = "Times New Roman"
        run_title.font.size = Pt(18)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(17, 24, 39)
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_title.paragraph_format.space_after = Pt(4)

        # Document Subtitle & Metadata
        p_meta = doc.add_paragraph()
        meta_clean = _clean_xml_string(f"{subtitle}\nNgười phát triển hệ thống: {author} • Chuẩn xuất bản quốc tế APA 7 & Swales CARS")
        run_meta = p_meta.add_run(meta_clean)
        run_meta.font.name = "Times New Roman"
        run_meta.font.size = Pt(10.5)
        run_meta.font.italic = True
        run_meta.font.color.rgb = RGBColor(107, 114, 128)
        p_meta.paragraph_format.space_after = Pt(16)

        # Parse markdown lines
        lines = _clean_xml_string(markdown_text).split("\n")
        in_table = False
        table_rows = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_table and table_rows:
                    _add_docx_table(doc, table_rows)
                    in_table = False
                    table_rows = []
                continue

            # Check table line
            if stripped.startswith("|") and stripped.endswith("|"):
                in_table = True
                if not re.match(r"^\|(\s*:?-+:?\s*\|)+$", stripped):
                    cols = [_strip_markdown_formatting(c.strip()) for c in stripped[1:-1].split("|")]
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
                _format_run(h.add_run(_strip_markdown_formatting(stripped[2:])), size=14, bold=True, color=RGBColor(31, 41, 55))
                h.paragraph_format.space_before = Pt(14)
                h.paragraph_format.space_after = Pt(4)
            elif stripped.startswith("## "):
                h = doc.add_heading(level=2)
                _format_run(h.add_run(_strip_markdown_formatting(stripped[3:])), size=12.5, bold=True, color=RGBColor(55, 65, 81))
                h.paragraph_format.space_before = Pt(12)
                h.paragraph_format.space_after = Pt(4)
            elif stripped.startswith("### "):
                h = doc.add_heading(level=3)
                _format_run(h.add_run(_strip_markdown_formatting(stripped[4:])), size=11.5, bold=True, italic=True, color=RGBColor(75, 85, 99))
                h.paragraph_format.space_before = Pt(8)
                h.paragraph_format.space_after = Pt(3)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                run_bullet = p.add_run("• ")
                _format_run(run_bullet, size=11, bold=True, color=RGBColor(55, 65, 81))
                _append_inline_formatted_text(p, stripped[2:])
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.15
            elif re.match(r"^\d+\.\s", stripped):
                match = re.match(r"^(\d+\.)\s*(.*)", stripped)
                num_prefix = match.group(1) if match else "1."
                rest_text = match.group(2) if match else stripped
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                run_num = p.add_run(f"{num_prefix} ")
                _format_run(run_num, size=11, bold=True, color=RGBColor(55, 65, 81))
                _append_inline_formatted_text(p, rest_text)
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
        return markdown_text.encode("utf-8")

def _format_run(run, size=11, bold=False, italic=False, color=None):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color

def _append_inline_formatted_text(paragraph, text, italic=False, color=None):
    clean_t = _clean_xml_string(text)
    parts = re.split(r"(\*\*.*?\*\*|\*.*?\*|\[.*?\]\(.*?\))", clean_t)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            run = paragraph.add_run(part[2:-2])
            _format_run(run, size=11, bold=True, italic=italic, color=color)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
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
                cell.text = _clean_xml_string(cell_text)
                for p in cell.paragraphs:
                    for run in p.runs:
                        _format_run(run, size=9.5, bold=(r_idx == 0))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

def dataframe_to_xlsx(df: pd.DataFrame, sheet_name: str = "Data Matrix") -> bytes:
    """
    Export pandas DataFrame to standardized Excel (.xlsx) file with active hyperlinks on DOIs and URLs.
    Includes auto column width adjustment, header styling, and freeze panes.
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        clean_df = df.copy()
        clean_df.to_excel(writer, index=False, sheet_name=sheet_name[:30])
        
        ws = writer.sheets[sheet_name[:30]]
        
        try:
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter

            header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
            header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
            link_font = Font(name="Arial", size=10, color="0055CC", underline="single")
            regular_font = Font(name="Arial", size=10, color="1E293B")
            
            thin_border = Border(
                left=Side(style='thin', color='E2E8F0'),
                right=Side(style='thin', color='E2E8F0'),
                top=Side(style='thin', color='E2E8F0'),
                bottom=Side(style='thin', color='E2E8F0')
            )

            # Style header row
            for col_idx in range(1, len(clean_df.columns) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            # Map column names to indices
            col_names = [str(c).lower().strip() for c in clean_df.columns]
            
            doi_col_idx = None
            pdf_col_idx = None
            url_col_idx = None
            title_col_idx = None

            for i, name in enumerate(col_names, 1):
                if name in ["doi", "doi_url", "mã doi", "doi (hyperlink)"]:
                    doi_col_idx = i
                elif "pdf" in name or "fulltext" in name:
                    pdf_col_idx = i
                elif "url" in name or "landing" in name or "link" in name:
                    url_col_idx = i
                elif name in ["title", "tiêu đề", "tiêu đề bài báo", "paper title"]:
                    title_col_idx = i

            # Format data cells and add hyperlinks
            for row_idx in range(2, len(clean_df) + 2):
                for col_idx in range(1, len(clean_df.columns) + 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.border = thin_border
                    val_str = str(cell.value or "").strip()
                    col_header = str(clean_df.columns[col_idx - 1]).lower()

                    # Apply hyperlinks
                    if val_str and val_str not in ["nan", "None", ""]:
                        if val_str.startswith("http://") or val_str.startswith("https://"):
                            cell.hyperlink = val_str
                            cell.font = link_font
                            if "pdf" in col_header:
                                cell.value = "🔗 Tải tệp PDF"
                            elif "doi" in col_header or "link" in col_header:
                                cell.value = "🌐 Mở liên kết"
                        elif col_idx == doi_col_idx or "mã doi" in col_header:
                            clean_doi = val_str.replace("https://doi.org/", "").replace("http://dx.doi.org/", "").strip()
                            if clean_doi.startswith("10.") or "/" in clean_doi:
                                cell.hyperlink = f"https://doi.org/{clean_doi}"
                                cell.font = link_font
                        elif col_idx == title_col_idx:
                            # Attach link to title if DOI exists in row
                            if doi_col_idx:
                                raw_doi = str(ws.cell(row=row_idx, column=doi_col_idx).value or "").strip()
                                clean_doi = raw_doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "").strip()
                                if clean_doi.startswith("10."):
                                    cell.hyperlink = f"https://doi.org/{clean_doi}"
                                    cell.font = link_font
                            elif regular_font:
                                cell.font = regular_font
                        else:
                            cell.font = regular_font

            # Auto-fit column widths
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    val = str(cell.value or "")
                    if len(val) > max_len:
                        max_len = len(val)
                ws.column_dimensions[col_letter].width = max(12, min(50, max_len + 3))

            # Freeze top header
            ws.freeze_panes = "A2"

        except Exception as err:
            print(f"[dataframe_to_xlsx styling warning] {err}")

    buffer.seek(0)
    return buffer.getvalue()

def generate_printable_html(title: str, markdown_content: str, author: str = "TRẦN DUY") -> str:
    """Generate high-fidelity printable HTML document (for PDF export / Google Docs import)."""
    # Clean markdown
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
