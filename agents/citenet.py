import math
import json
import html
from typing import Dict, List, Any, Tuple, Optional, Union
from utils.openalex_client import OpenAlexClient, parse_doi_list
from utils.bib_formatter import generate_bibtex, generate_ris, papers_to_dataframe

class CiteNetAgent:
    """
    Trợ lý 1: CiteNet (Graph Expansion & Network Builder)
    Nhận 1 hoặc NHIỀU seed DOIs, tự động dò tìm và dựng đồ thị trích dẫn đa tầng (2 thế hệ).
    Chuẩn hóa theo các quy chuẩn thư mục học quốc tế (Bibliometric & Scientometric standards).
    """
    def __init__(self, email: Optional[str] = None):
        self.client = OpenAlexClient(email=email)

    def run(
        self,
        seed_dois: Union[str, List[str]],
        gen1_limit: int = 20,
        gen2_limit: int = 68,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Execute CiteNet pipeline for single or multiple DOIs.
        """
        nodes_dict, edges_list, seed_papers = self.client.build_2gen_network(
            seed_dois=seed_dois,
            gen1_limit=gen1_limit,
            gen2_limit=gen2_limit,
            progress_callback=progress_callback
        )

        papers_list = list(nodes_dict.values())
        primary_seed = seed_papers[0] if seed_papers else (papers_list[0] if papers_list else {})

        if progress_callback:
            progress_callback(85, "Đang khởi tạo đồ thị tương tác chuẩn quốc tế và tính toán layout thời gian...")

        network_html = self.generate_network_html(nodes_dict, edges_list)

        if progress_callback:
            progress_callback(95, "Đang xuất thư viện trích dẫn BibTeX, RIS và bảng dữ liệu CSV...")

        df_refs = papers_to_dataframe(papers_list)
        refs_csv = df_refs.to_csv(index=False, encoding="utf-8")
        refs_bib = generate_bibtex(papers_list)
        refs_ris = generate_ris(papers_list)

        gen0_count = len(seed_papers)
        gen1_count = sum(1 for p in papers_list if p.get("generation") == 1)
        gen2_count = sum(1 for p in papers_list if p.get("generation") == 2)
        
        oa_papers = [p for p in papers_list if p.get("is_oa") or bool(p.get("pdf_url"))]
        paywall_papers = [p for p in papers_list if not (p.get("is_oa") or bool(p.get("pdf_url")))]
        oa_count = len(oa_papers)
        paywall_count = len(paywall_papers)
        oa_percent = round((oa_count / len(papers_list) * 100), 1) if papers_list else 0.0

        stats = {
            "total_papers": len(papers_list),
            "total_links": len(edges_list),
            "seed_count": gen0_count,
            "seed_titles": [p.get("title", "") for p in seed_papers],
            "seed_dois": [p.get("doi", "") for p in seed_papers],
            "seed_title": primary_seed.get("title", "Seed Paper"),
            "seed_doi": primary_seed.get("doi", ""),
            "gen0_count": gen0_count,
            "gen1_count": gen1_count,
            "gen2_count": gen2_count,
            "oa_count": oa_count,
            "paywall_count": paywall_count,
            "oa_percent": oa_percent
        }

        return {
            "nodes": nodes_dict,
            "edges": edges_list,
            "papers_list": papers_list,
            "seed_papers": seed_papers,
            "seed_paper": primary_seed,
            "dataframe": df_refs,
            "network_html": network_html,
            "refs_csv": refs_csv,
            "refs_bib": refs_bib,
            "refs_ris": refs_ris,
            "stats": stats
        }

    def generate_network_html(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        height: str = "720px",
        width: str = "100%"
    ) -> str:
        """
        Construct interactive HTML graph with commercial Obsidian styling, international bibliometric node sizing,
        dynamic zoom controls, and a Dual-Mode (Force-directed vs Chronological Timeline evolution) layout.
        """
        color_map = {
            0: {"background": "#EA4335", "border": "#FF8A80", "highlight": "#FFEBEE"}, # Red for Seed Core
            1: {"background": "#0284C7", "border": "#38BDF8", "highlight": "#E0F2FE"}, # Cyan/Blue for Gen-1
            2: {"background": "#059669", "border": "#34D399", "highlight": "#ECFDF5"}  # Emerald for Gen-2
        }

        years_list = []
        for n in nodes.values():
            try:
                y = int(n.get("year", 2020))
                years_list.append(y)
            except Exception:
                pass
        min_yr = min(years_list) if years_list else 2017
        max_yr = max(years_list) if years_list else 2026

        vis_nodes = []
        for node_id, meta in nodes.items():
            gen = meta.get("generation", 2)
            cites = meta.get("citation_count", 0) or 0
            
            # Chuẩn quốc tế: Tính kích cỡ node theo quy luật lũy thừa / logarit số trích dẫn (Price's Law)
            base_size = 16
            if cites > 0:
                log_scale = math.log(cites + 1, 1.5) * 4.2
                node_size = max(16, min(56, int(base_size + log_scale)))
            else:
                node_size = 16
            if gen == 0:
                node_size = max(node_size + 10, 36)

            colors = color_map.get(gen, color_map[2])
            first_auth = meta.get("first_author", "Tác giả").split()[-1] if meta.get("first_author") else "Paper"
            year = meta.get("year", "n.d.")
            
            # Nhãn học thuật kèm trực tiếp số lượt trích dẫn
            if gen == 0:
                short_label = f"★ {first_auth} ({year})\n[{cites} trích dẫn]"
            else:
                short_label = f"{first_auth} ({year})\n[{cites} trích dẫn]"

            # Tính tọa độ timeline ban đầu
            try:
                yr_int = int(year)
            except Exception:
                yr_int = min_yr
            x_timeline = (yr_int - min_yr) * 240 - ((max_yr - min_yr) * 120)
            
            vis_nodes.append({
                "id": node_id,
                "label": short_label,
                "value": cites + 1,
                "size": node_size,
                "color": colors,
                "borderWidth": 3.5 if gen == 0 else 1.8,
                "font": {
                    "size": 12 if gen == 0 else 11,
                    "color": "#F8FAFC",
                    "face": "Plus Jakarta Sans, sans-serif",
                    "strokeWidth": 3,
                    "strokeColor": "#0B0C0E"
                },
                "shape": "star" if gen == 0 else "dot",
                "x_timeline": x_timeline,
                "year": yr_int,
                "citations": cites
            })

        vis_edges = []
        for src, dst in edges:
            if src in nodes and dst in nodes:
                vis_edges.append({
                    "from": src,
                    "to": dst,
                    "color": {"color": "rgba(100, 116, 139, 0.45)", "highlight": "#38BDF8", "hover": "#60A5FA"},
                    "arrows": {"to": {"enabled": True, "scaleFactor": 0.85}},
                    "width": 1.4,
                    "smooth": {"type": "curvedCW", "roundness": 0.18}
                })

        extended_meta = {}
        for node_id, meta in nodes.items():
            outgoing = [dst for s, dst in edges if s == node_id]
            incoming = [s for s, dst in edges if dst == node_id]
            
            doi_val = meta.get("doi", "")
            doi_url = meta.get("doi_url") or (f"https://doi.org/{doi_val}" if doi_val else "")
            landing_url = meta.get("landing_url") or doi_url
            pdf_url = meta.get("pdf_url") or ""
            
            abs_vi = meta.get("abstract_vi") or meta.get("abstract") or "Đang cập nhật tóm tắt tiếng Việt..."
            abs_en = meta.get("abstract_en") or meta.get("abstract") or "Abstract in English..."

            extended_meta[node_id] = {
                "id": node_id,
                "title": meta.get("title", "Untitled Paper"),
                "authors": meta.get("authors", "Unknown Authors"),
                "first_author": meta.get("first_author", "Unknown"),
                "year": meta.get("year", "n.d."),
                "venue": meta.get("venue", "N/A"),
                "scopus_tier": meta.get("scopus_tier", "Scopus Indexed"),
                "study_type": meta.get("study_type", "Empirical Journalism Study"),
                "doi": doi_val,
                "doi_url": doi_url,
                "landing_url": landing_url,
                "pdf_url": pdf_url,
                "openalex_url": meta.get("openalex_url", ""),
                "citation_count": meta.get("citation_count", 0) or 0,
                "generation": meta.get("generation", 2),
                "is_oa": meta.get("is_oa", False) or bool(pdf_url),
                "abstract": abs_vi,
                "abstract_vi": abs_vi,
                "abstract_en": abs_en,
                "outgoing_ids": outgoing,
                "incoming_ids": incoming,
                "total_connections": len(outgoing) + len(incoming)
            }

        nodes_json = json.dumps(vis_nodes, ensure_ascii=False)
        edges_json = json.dumps(vis_edges, ensure_ascii=False)
        meta_dict_json = json.dumps(extended_meta, ensure_ascii=False)

        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Citation Knowledge Graph — ScholarGraph Pro</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style type="text/css">
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #0B0C0E;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            color: #F8FAFC;
        }}
        #network-wrapper {{
            position: relative;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #12141A 0%, #0B0C0E 100%);
            border-radius: 16px;
            border: 1px solid #262B38;
            overflow: hidden;
        }}
        #network-container {{
            width: 100%;
            height: 100%;
        }}
        
        /* Floating Control HUD Toolbar */
        .hud-toolbar {{
            position: absolute;
            top: 14px;
            left: 14px;
            display: flex;
            gap: 6px;
            z-index: 100;
            background: rgba(18, 20, 26, 0.94);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 8px 12px;
            border-radius: 14px;
            border: 1px solid #262B38;
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
            align-items: center;
            flex-wrap: wrap;
            max-width: calc(100% - 28px);
        }}
        .hud-btn {{
            background: #181B24;
            border: 1px solid #262B38;
            color: #F8FAFC;
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.18s ease;
            white-space: nowrap;
        }}
        .hud-btn:hover {{
            background: #232836;
            border-color: #38BDF8;
            color: #FFFFFF;
            transform: translateY(-1px);
        }}
        .hud-btn.active {{
            background: rgba(37, 99, 235, 0.25);
            border-color: #38BDF8;
            color: #38BDF8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
        }}
        .hud-btn.primary {{
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            border-color: #38BDF8;
            color: #FFFFFF;
        }}
        .hud-search-box {{
            background: #141720;
            border: 1px solid #262B38;
            color: #FFFFFF;
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 12.5px;
            width: 170px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .hud-search-box:focus {{
            border-color: #38BDF8;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
        }}
        
        .hud-legend {{
            position: absolute;
            bottom: 14px;
            right: 14px;
            z-index: 90;
            background: rgba(18, 20, 26, 0.94);
            backdrop-filter: blur(14px);
            padding: 10px 14px;
            border-radius: 12px;
            border: 1px solid #262B38;
            font-size: 11.5px;
            font-weight: 600;
            display: flex;
            gap: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.4);
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}

        /* Timeline Axis Overlay */
        #timeline-axis-bar {{
            display: none;
            position: absolute;
            bottom: 54px;
            left: 20px;
            right: 20px;
            z-index: 80;
            background: rgba(18, 20, 26, 0.9);
            border: 1px solid #262B38;
            border-radius: 10px;
            padding: 6px 14px;
            display: none;
            justify-content: space-between;
            font-size: 11px;
            color: #94A3B8;
            font-family: 'JetBrains Mono', monospace;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        }}

        /* Floating Info Card HUD */
        #floating-hover-card {{
            display: none;
            position: absolute;
            pointer-events: none;
            z-index: 150;
            width: 380px;
            max-width: 92%;
            background: rgba(18, 20, 26, 0.97);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid #262B38;
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 14px 36px rgba(0,0,0,0.65);
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #F8FAFC;
        }}

        /* Modal Drawer */
        #paper-modal {{
            position: absolute;
            top: 14px;
            right: 14px;
            width: 440px;
            max-width: 90%;
            max-height: calc(100% - 28px);
            background: rgba(18, 20, 26, 0.98);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid #262B38;
            border-radius: 16px;
            z-index: 200;
            box-shadow: 0 16px 40px rgba(0,0,0,0.6);
            display: none;
            flex-direction: column;
            overflow: hidden;
            animation: slideIn 0.2s ease-out;
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        .modal-header {{
            padding: 14px 18px;
            background: #181B24;
            border-bottom: 1px solid #262B38;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .modal-body {{
            padding: 18px;
            overflow-y: auto;
            flex: 1;
        }}
        .modal-title {{
            font-size: 15.5px;
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.45;
            margin-bottom: 8px;
        }}
        .modal-meta-row {{
            font-size: 13px;
            color: #94A3B8;
            margin-bottom: 6px;
            line-height: 1.5;
        }}
        .modal-badge {{
            display: inline-block;
            padding: 3px 9px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge-seed {{ background: rgba(234, 67, 53, 0.2); color: #F28B82; border: 1px solid rgba(234, 67, 53, 0.4); }}
        .badge-gen1 {{ background: rgba(2, 132, 199, 0.2); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4); }}
        .badge-gen2 {{ background: rgba(5, 150, 105, 0.2); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4); }}
        
        .modal-section-title {{
            font-size: 12px;
            font-weight: 700;
            color: #38BDF8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin: 14px 0 6px 0;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .bilingual-tabs-nav {{
            display: flex;
            gap: 6px;
            background: #141720;
            padding: 4px;
            border-radius: 10px;
            border: 1px solid #262B38;
            margin-bottom: 8px;
        }}
        .bilingual-tab-btn {{
            flex: 1;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 700;
            color: #94A3B8;
            background: transparent;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .bilingual-tab-btn:hover {{
            color: #FFFFFF;
            background: #181B24;
        }}
        .bilingual-tab-btn.active {{
            background: #2563EB;
            color: #FFFFFF;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35);
        }}
        
        .modal-abstract-box {{
            background: #141720;
            border: 1px solid #262B38;
            border-radius: 10px;
            padding: 12px 14px;
            font-size: 13px;
            color: #F8FAFC;
            line-height: 1.65;
            max-height: 180px;
            overflow-y: auto;
        }}
        .modal-abstract-box.en-mode {{
            font-style: italic;
            color: #CBD5E1;
        }}
        
        .action-link-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            text-decoration: none;
            color: #FFFFFF;
            background: #2563EB;
            border: 1px solid #38BDF8;
            transition: all 0.15s ease;
            margin-right: 6px;
            margin-top: 6px;
        }}
        .action-link-btn:hover {{
            background: #1D4ED8;
            transform: translateY(-1px);
        }}
        .action-link-btn.secondary {{
            background: #181B24;
            border-color: #262B38;
            color: #38BDF8;
        }}
        .action-link-btn.secondary:hover {{
            background: #232836;
        }}

        .lineage-chip {{
            display: block;
            background: #141720;
            border: 1px solid #262B38;
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 11.5px;
            color: #CBD5E1;
            margin-bottom: 4px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .lineage-chip:hover {{
            background: #181B24;
            border-color: #38BDF8;
            color: #FFFFFF;
        }}
        
        .close-btn {{
            background: transparent;
            border: none;
            color: #94A3B8;
            font-size: 18px;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 6px;
            line-height: 1;
        }}
        .close-btn:hover {{
            background: #262B38;
            color: #FFFFFF;
        }}

        /* Tối ưu hóa hiển thị trên Máy tính bảng (Tablet) & Điện thoại (Mobile) */
        @media (max-width: 992px) {{
            .hud-toolbar {{
                top: 8px;
                left: 8px;
                max-width: calc(100% - 16px);
                gap: 5px;
                padding: 6px 10px;
            }}
            .hud-btn {{
                padding: 6px 10px;
                font-size: 11.5px;
            }}
            .hud-search-box {{
                width: 140px;
                font-size: 11.5px;
                padding: 6px 10px;
            }}
        }}

        @media (max-width: 768px) {{
            .hud-toolbar {{
                top: 6px;
                left: 6px;
                right: 6px;
                max-width: calc(100% - 12px);
                overflow-x: auto;
                flex-wrap: nowrap;
                white-space: nowrap;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
                padding: 6px 8px;
                gap: 4px;
                border-radius: 10px;
            }}
            .hud-toolbar::-webkit-scrollbar {{
                display: none;
            }}
            .hud-btn {{
                padding: 6px 9px;
                font-size: 11px;
                flex-shrink: 0;
            }}
            .hud-search-box {{
                width: 130px;
                font-size: 11px;
                padding: 5px 8px;
                flex-shrink: 0;
            }}
            .hud-legend {{
                bottom: 8px;
                left: 8px;
                right: 8px;
                font-size: 10px;
                padding: 6px 10px;
                gap: 8px;
                justify-content: center;
                border-radius: 8px;
            }}
            #floating-hover-card {{
                display: none !important; /* Ẩn hover card trên thiết bị cảm ứng để tránh vướng màn hình */
            }}
            #paper-modal {{
                top: auto !important;
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                width: 100% !important;
                max-width: 100% !important;
                max-height: 82vh !important;
                border-radius: 20px 20px 0 0 !important;
                border-bottom: none !important;
                box-shadow: 0 -10px 40px rgba(0,0,0,0.8) !important;
                animation: slideUpModal 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
            }}
            @keyframes slideUpModal {{
                from {{ transform: translateY(100%); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}
            .modal-header {{
                padding: 12px 16px !important;
            }}
            .modal-body {{
                padding: 14px 16px !important;
                -webkit-overflow-scrolling: touch;
            }}
            .modal-title {{
                font-size: 14px !important;
            }}
        }}
    </style>
</head>
<body>
<div id="network-wrapper">
    <!-- Floating HUD Controls Toolbar -->
    <div class="hud-toolbar">
        <input type="text" id="nodeSearch" class="hud-search-box" placeholder="🔍 Tìm tác giả / bài báo..." oninput="searchAndFocusNode(this.value)">
        
        <!-- Zoom & Fit Controls -->
        <button class="hud-btn" onclick="zoomIn()" title="Phóng to mạng lưới">🔍+ Phóng to</button>
        <button class="hud-btn" onclick="zoomOut()" title="Thu nhỏ mạng lưới">🔍- Thu nhỏ</button>
        <button class="hud-btn" onclick="fitView()" title="Căn giữa toàn cảnh">🎯 Căn giữa</button>
        
        <!-- 5 International Scientometric Layout Modes -->
        <button class="hud-btn active" id="btnModeForce" onclick="switchLayoutMode('force')" title="1. Chuẩn VOSviewer: Cụm lực hút đồng trích dẫn (Force-directed Co-citation)">🕸️ Mạng lưới Cụm</button>
        <button class="hud-btn" id="btnModeTimeline" onclick="switchLayoutMode('timeline')" title="2. Chuẩn HistCite: Dòng thời gian tiến hóa học thuật (Chronological Lineage)">⏳ Dòng Thời gian</button>
        <button class="hud-btn" id="btnModeConcentric" onclick="switchLayoutMode('concentric')" title="3. Chuẩn Ego-Network: Quỹ đạo đồng tâm theo thế hệ trích dẫn (Concentric Orbit)">🎯 Quỹ đạo Đồng tâm</button>
        <button class="hud-btn" id="btnModeHierarchical" onclick="switchLayoutMode('hierarchical')" title="4. Chuẩn CiteSpace: Cây phả hệ phân tầng (Hierarchical DAG Tree)">🌳 Cây Phả hệ</button>
        <button class="hud-btn" id="btnModeQuartile" onclick="switchLayoutMode('quartile')" title="5. Chuẩn Clarivate / Scimago: Phân làn xếp hạng Scopus Q1/Q2 & Tạp chí (Journal Quartile Grid)">📊 Phân làn Scopus</button>
        
        <!-- Physics & Window Controls -->
        <button class="hud-btn" id="physicsBtn" onclick="togglePhysics()" title="Bật/Tắt mô phỏng vật lý">⚡ Tự sắp xếp</button>
        <button class="hud-btn" onclick="toggleFullScreen()" title="Phóng to toàn màn hình">⛶ Toàn màn hình</button>
        <button class="hud-btn primary" onclick="popoutWindow()" title="Mở trong cửa sổ riêng để kéo sang màn hình phụ">🪟 Màn hình phụ</button>
    </div>

    <!-- Timeline / Mode Axis Marker Bar (Dynamic across modes) -->
    <div id="timeline-axis-bar">
        <span>◀ <b>QUÁ KHỨ ({min_yr})</b>: Nền tảng lý thuyết ban đầu</span>
        <span style="color:#38BDF8;">DÒNG TIẾN HÓA TRÍCH DẪN THEO NĂM XUẤT BẢN</span>
        <span><b>HIỆN TẠI ({max_yr})</b>: Khám phá mới nhất ▶</span>
    </div>

    <!-- Floating Hover Info Card -->
    <div id="floating-hover-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div id="hover-badge" style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em;"></div>
            <div id="hover-conn-badge" style="font-size:11px; font-weight:600;"></div>
        </div>
        <div id="hover-title" style="font-size:13px; font-weight:700; color:#FFFFFF; line-height:1.4; margin-bottom:6px;"></div>
        <div id="hover-meta" style="font-size:11.5px; color:#94A3B8; line-height:1.5; margin-bottom:8px;"></div>
        <div style="background:#141720; border:1px solid #262B38; border-radius:8px; padding:8px 10px; margin-bottom:8px;">
            <div style="font-size:10.5px; font-weight:700; color:#38BDF8; text-transform:uppercase; margin-bottom:3px;">Tóm tắt nội dung (Tiếng Việt):</div>
            <div id="hover-abstract-vi" style="font-size:11.5px; color:#E2E8F0; line-height:1.5; max-height:85px; overflow:hidden; text-overflow:ellipsis;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11px; color:#38BDF8; font-weight:600;">
            <span>Nhấp chuột để mở toàn văn song ngữ & bài gốc ↗</span>
        </div>
    </div>

    <!-- Interactive Paper Detail Modal -->
    <div id="paper-modal">
        <div class="modal-header">
            <div id="modal-gen-badge"></div>
            <button class="close-btn" onclick="closePaperModal()">✕</button>
        </div>
        <div class="modal-body">
            <div id="modal-title" class="modal-title"></div>
            <div id="modal-authors" class="modal-meta-row"></div>
            <div id="modal-venue" class="modal-meta-row"></div>
            <div id="modal-citations" class="modal-meta-row"></div>
            
            <div style="margin: 10px 0;">
                <a id="modal-doi-link" class="action-link-btn" href="#" target="_blank">Mở bài báo gốc (DOI) ↗</a>
                <a id="modal-pdf-link" class="action-link-btn secondary" href="#" target="_blank" style="display:none;">📄 Tải tệp PDF ↗</a>
                <a id="modal-openalex-link" class="action-link-btn secondary" href="#" target="_blank">🌐 OpenAlex ↗</a>
            </div>

            <div class="modal-section-title">📄 TÓM TẮT NỘI DUNG NGHIÊN CỨU (SONG NGỮ)</div>
            <div class="bilingual-tabs-nav">
                <button id="tabBtnVi" class="bilingual-tab-btn active" onclick="switchModalLang('vi')">🇻🇳 Tiếng Việt</button>
                <button id="tabBtnEn" class="bilingual-tab-btn" onclick="switchModalLang('en')">🇬🇧 Nguyên bản (English)</button>
            </div>
            <div id="modal-abstract-vi" class="modal-abstract-box"></div>
            <div id="modal-abstract-en" class="modal-abstract-box en-mode" style="display: none;"></div>

            <div class="modal-section-title">🧬 PHẢ HỆ & LIÊN KẾT TRÍCH DẪN</div>
            <div id="modal-lineage-content"></div>
        </div>
    </div>

    <div class="hud-legend">
        <div class="legend-item"><span class="legend-dot" style="background:#EA4335;"></span> Bài báo gốc (Seed Core)</div>
        <div class="legend-item"><span class="legend-dot" style="background:#0284C7;"></span> Tham khảo trực tiếp (Gen-1)</div>
        <div class="legend-item"><span class="legend-dot" style="background:#059669;"></span> Mở rộng chân trời (Gen-2)</div>
        <div class="legend-item"><span style="color:#38BDF8; font-size:12px;">● Kích cỡ = Số trích dẫn (Impact)</span></div>
    </div>

    <div id="network-container"></div>
</div>

<script type="text/javascript">
    var rawNodes = {nodes_json};
    var rawEdges = {edges_json};
    var metaDict = {meta_dict_json};
    var minYrVal = {min_yr};
    var maxYrVal = {max_yr};
    
    var nodes = new vis.DataSet(rawNodes);
    var edges = new vis.DataSet(rawEdges);
    var container = document.getElementById('network-container');
    var data = {{ nodes: nodes, edges: edges }};
    var isPhysicsOn = true;
    var currentLayoutMode = 'force'; // 'force', 'timeline', 'concentric', 'hierarchical', 'quartile'

    var forceOptions = {{
        nodes: {{
            shadow: {{
                enabled: true,
                color: 'rgba(0,0,0,0.4)',
                size: 6,
                x: 2,
                y: 2
            }}
        }},
        edges: {{
            smooth: {{
                type: 'continuous',
                forceDirection: 'none'
            }}
        }},
        physics: {{
            forceAtlas2Based: {{
                gravitationalConstant: -60,
                centralGravity: 0.012,
                springLength: 120,
                springConstant: 0.08,
                damping: 0.45
            }},
            minVelocity: 0.75,
            solver: 'forceAtlas2Based',
            stabilization: {{ iterations: 140 }}
        }},
        interaction: {{
            hover: true,
            navigationButtons: false,
            keyboard: true,
            zoomView: true,
            dragNodes: true,
            dragView: true,
            tooltipDelay: 30
        }}
    }};

    var network = new vis.Network(container, data, forceOptions);

    // Zoom Controls
    function zoomIn() {{
        var scale = network.getScale();
        network.moveTo({{
            scale: scale * 1.35,
            animation: {{ duration: 250, easingFunction: 'easeInOutQuad' }}
        }});
    }}

    function zoomOut() {{
        var scale = network.getScale();
        network.moveTo({{
            scale: scale / 1.35,
            animation: {{ duration: 250, easingFunction: 'easeInOutQuad' }}
        }});
    }}

    function fitView() {{
        network.fit({{ animation: {{ duration: 500, easingFunction: 'easeInOutQuad' }} }});
    }}

    // 5 International Scientometric Layouts Switcher
    function switchLayoutMode(mode) {{
        currentLayoutMode = mode;
        var btnForce = document.getElementById('btnModeForce');
        var btnTimeline = document.getElementById('btnModeTimeline');
        var btnConcentric = document.getElementById('btnModeConcentric');
        var btnHierarchical = document.getElementById('btnModeHierarchical');
        var btnQuartile = document.getElementById('btnModeQuartile');
        var axisBar = document.getElementById('timeline-axis-bar');

        [btnForce, btnTimeline, btnConcentric, btnHierarchical, btnQuartile].forEach(function(b) {{
            if (b) b.className = 'hud-btn';
        }});

        if (mode === 'timeline') {{
            if (btnTimeline) btnTimeline.className = 'hud-btn active';
            axisBar.style.display = 'flex';
            axisBar.innerHTML = '<span>◀ <b>QUÁ KHỨ (' + minYrVal + ')</b>: Nền tảng lý thuyết ban đầu</span><span style="color:#38BDF8; font-weight:700;">DÒNG TIẾN HÓA TRÍCH DẪN THEO NĂM XUẤT BẢN (CHRONOLOGICAL)</span><span><b>HIỆN TẠI (' + maxYrVal + ')</b>: Khám phá mới nhất ▶</span>';

            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            
            var updates = [];
            var yearGroups = {{}};
            rawNodes.forEach(function(n) {{
                var yr = n.year || 2020;
                if (!yearGroups[yr]) yearGroups[yr] = [];
                yearGroups[yr].push(n.id);
            }});

            rawNodes.forEach(function(n) {{
                var yr = n.year || 2020;
                var listInYear = yearGroups[yr] || [n.id];
                var indexInYear = listInYear.indexOf(n.id);
                var totalInYear = listInYear.length;
                var yOffset = (indexInYear - (totalInYear - 1) / 2) * 90;
                updates.push({{
                    id: n.id,
                    x: n.x_timeline,
                    y: yOffset,
                    physics: false
                }});
            }});
            nodes.update(updates);
            setTimeout(function() {{ fitView(); }}, 200);

        }} else if (mode === 'concentric') {{
            if (btnConcentric) btnConcentric.className = 'hud-btn active';
            axisBar.style.display = 'flex';
            axisBar.innerHTML = '<span>⭐ <b>TÂM ĐIỂM (R=0)</b>: Bài báo gốc</span><span style="color:#38BDF8; font-weight:700;">QUỸ ĐẠO ĐỒNG TÂM: VÒNG TRONG (Gen-1 Trực tiếp) ── VÒNG NGOÀI (Gen-2 Mở rộng)</span><span>🌐 <b>BIÊN GIỚI (R=480)</b>: Chân trời học thuật</span>';

            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});

            var updates = [];
            var gen0 = rawNodes.filter(function(n) {{ return (metaDict[n.id] && metaDict[n.id].generation === 0); }});
            var gen1 = rawNodes.filter(function(n) {{ return (metaDict[n.id] && metaDict[n.id].generation === 1); }});
            var gen2 = rawNodes.filter(function(n) {{ return (!metaDict[n.id] || (metaDict[n.id].generation !== 0 && metaDict[n.id].generation !== 1)); }});

            gen0.forEach(function(n) {{
                updates.push({{ id: n.id, x: 0, y: 0, physics: false }});
            }});

            var r1 = 250;
            var count1 = gen1.length || 1;
            gen1.forEach(function(n, i) {{
                var angle = (2 * Math.PI * i) / count1 - Math.PI / 2;
                updates.push({{
                    id: n.id,
                    x: Math.round(r1 * Math.cos(angle)),
                    y: Math.round(r1 * Math.sin(angle)),
                    physics: false
                }});
            }});

            var r2 = 490;
            var count2 = gen2.length || 1;
            gen2.forEach(function(n, j) {{
                var angle = (2 * Math.PI * j) / count2 - Math.PI / 2;
                updates.push({{
                    id: n.id,
                    x: Math.round(r2 * Math.cos(angle)),
                    y: Math.round(r2 * Math.sin(angle)),
                    physics: false
                }});
            }});

            nodes.update(updates);
            setTimeout(function() {{ fitView(); }}, 200);

        }} else if (mode === 'hierarchical') {{
            if (btnHierarchical) btnHierarchical.className = 'hud-btn active';
            axisBar.style.display = 'flex';
            axisBar.innerHTML = '<span>🌳 <b>TẦNG TRÊN (Gốc rễ)</b>: Công trình tiên phong</span><span style="color:#38BDF8; font-weight:700;">CÂY PHẢ HỆ HỌC THUẬT PHÂN TẦNG (HIERARCHICAL DAG TREE)</span><span>🍃 <b>TẦNG DƯỚI (Ngọn cây)</b>: Nghiên cứu kế thừa</span>';

            var updates = [];
            rawNodes.forEach(function(n) {{
                updates.push({{ id: n.id, physics: true }});
            }});
            nodes.update(updates);

            network.setOptions({{
                layout: {{
                    hierarchical: {{
                        enabled: true,
                        direction: 'UD',
                        sortMethod: 'directed',
                        levelSeparation: 150,
                        nodeSpacing: 180,
                        treeSpacing: 220,
                        blockShifting: true,
                        edgeMinimization: true
                    }}
                }},
                physics: {{
                    hierarchicalRepulsion: {{
                        centralGravity: 0.0,
                        springLength: 100,
                        springConstant: 0.01,
                        nodeDistance: 170,
                        damping: 0.09
                    }},
                    solver: 'hierarchicalRepulsion'
                }}
            }});
            setTimeout(function() {{ fitView(); }}, 350);

        }} else if (mode === 'quartile') {{
            if (btnQuartile) btnQuartile.className = 'hud-btn active';
            axisBar.style.display = 'flex';
            axisBar.innerHTML = '<span>⭐ <b>LÀN 1</b>: Bài báo gốc</span><span>🏆 <b>LÀN 2</b>: Scopus Q1 (Top Tier)</span><span>📊 <b>LÀN 3</b>: Scopus Q2 / Q3</span><span>🌐 <b>LÀN 4</b>: Tạp chí khác & Hội thảo</span>';

            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});

            var lanes = {{
                core: [],
                q1: [],
                q2: [],
                other: []
            }};

            rawNodes.forEach(function(n) {{
                var p = metaDict[n.id] || {{}};
                var tier = (p.scopus_tier || '').toLowerCase();
                if (p.generation === 0) {{
                    lanes.core.push(n.id);
                }} else if (tier.indexOf('q1') !== -1 || tier.indexOf('top tier') !== -1) {{
                    lanes.q1.push(n.id);
                }} else if (tier.indexOf('q2') !== -1 || tier.indexOf('q3') !== -1) {{
                    lanes.q2.push(n.id);
                }} else {{
                    lanes.other.push(n.id);
                }}
            }});

            var laneX = {{
                core: -440,
                q1: -150,
                q2: 150,
                other: 440
            }};

            var updates = [];
            ['core', 'q1', 'q2', 'other'].forEach(function(k) {{
                var list = lanes[k];
                var total = list.length;
                list.forEach(function(id, idx) {{
                    var yOffset = (idx - (total - 1) / 2) * 95;
                    updates.push({{
                        id: id,
                        x: laneX[k],
                        y: yOffset,
                        physics: false
                    }});
                }});
            }});

            nodes.update(updates);
            setTimeout(function() {{ fitView(); }}, 200);

        }} else {{
            // 'force'
            if (btnForce) btnForce.className = 'hud-btn active';
            axisBar.style.display = 'none';

            network.setOptions({{ layout: {{ hierarchical: false }} }});
            var updates = [];
            rawNodes.forEach(function(n) {{
                updates.push({{
                    id: n.id,
                    physics: true
                }});
            }});
            nodes.update(updates);
            network.setOptions(forceOptions);
            setTimeout(function() {{ fitView(); }}, 200);
        }}
    }}


    // Hover Event
    network.on('hoverNode', function(params) {{
        var nodeId = params.node;
        var p = metaDict[nodeId];
        if (!p) return;
        var card = document.getElementById('floating-hover-card');
        
        var badgeColor = p.generation === 0 ? '#EA4335' : (p.generation === 1 ? '#0284C7' : '#059669');
        var badgeLabel = p.generation === 0 ? '⭐ Bài báo gốc (Tâm điểm)' : (p.generation === 1 ? '🔗 Tham khảo trực tiếp (Gen-1)' : '🌐 Mở rộng cùng chủ đề (Gen-2)');
        
        document.getElementById('hover-badge').style.color = badgeColor;
        document.getElementById('hover-badge').innerText = badgeLabel;
        
        var connBadge = document.getElementById('hover-conn-badge');
        var totalConn = p.total_connections || 0;
        connBadge.innerHTML = '<span style="color:#38BDF8; background:rgba(56,189,248,0.12); padding:2px 8px; border-radius:6px; border:1px solid rgba(56,189,248,0.3);">🔗 ' + totalConn + ' liên kết • ' + p.citation_count + ' trích dẫn</span>';

        document.getElementById('hover-title').innerText = p.title;
        document.getElementById('hover-meta').innerHTML = '<b>✍️ Tác giả:</b> ' + p.authors + ' (' + p.year + ')<br/><b>🏛️ Tạp chí:</b> ' + p.venue + ' <span style="color:#38BDF8; font-weight:600;">(' + (p.scopus_tier || 'Scopus Indexed') + ')</span>';
        
        var absPreview = p.abstract_vi || p.abstract || 'Đang cập nhật tóm tắt tiếng Việt...';
        if (absPreview.length > 210) {{
            absPreview = absPreview.substring(0, 210) + '...';
        }}
        document.getElementById('hover-abstract-vi').innerText = absPreview;

        var domPos = network.canvasToDOM(network.getPosition(nodeId));
        var cardLeft = Math.min(window.innerWidth - 400, Math.max(15, domPos.x + 18));
        var cardTop = Math.min(window.innerHeight - 240, Math.max(15, domPos.y - 50));
        
        card.style.left = cardLeft + 'px';
        card.style.top = cardTop + 'px';
        card.style.display = 'block';
    }});

    network.on('blurNode', function() {{
        document.getElementById('floating-hover-card').style.display = 'none';
    }});

    function switchModalLang(lang) {{
        var btnVi = document.getElementById('tabBtnVi');
        var btnEn = document.getElementById('tabBtnEn');
        var boxVi = document.getElementById('modal-abstract-vi');
        var boxEn = document.getElementById('modal-abstract-en');
        if (lang === 'vi') {{
            btnVi.className = 'bilingual-tab-btn active';
            btnEn.className = 'bilingual-tab-btn';
            boxVi.style.display = 'block';
            boxEn.style.display = 'none';
        }} else {{
            btnEn.className = 'bilingual-tab-btn active';
            btnVi.className = 'bilingual-tab-btn';
            boxVi.style.display = 'none';
            boxEn.style.display = 'block';
        }}
    }}

    network.on('click', function(params) {{
        if (params.nodes.length > 0) {{
            var nodeId = params.nodes[0];
            showPaperModal(nodeId);
        }}
    }});

    function showPaperModal(nodeId) {{
        var p = metaDict[nodeId];
        if (!p) return;

        var modal = document.getElementById('paper-modal');
        
        var badgeHtml = '';
        if (p.generation === 0) {{
            badgeHtml = '<span class="modal-badge badge-seed">Bài báo gốc (Tâm điểm)</span>';
        }} else if (p.generation === 1) {{
            badgeHtml = '<span class="modal-badge badge-gen1">Tham khảo trực tiếp (Gen-1)</span>';
        }} else {{
            badgeHtml = '<span class="modal-badge badge-gen2">Mở rộng cùng chủ đề (Gen-2)</span>';
        }}
        badgeHtml += ' <span style="font-size:12px; color:#38BDF8; font-weight:600; margin-left:8px;">' + (p.scopus_tier || 'Scopus Indexed') + '</span>';

        if (p.is_oa || p.pdf_url) {{
            badgeHtml += '<div style="background:rgba(16, 185, 129, 0.12); border:1px solid rgba(16, 185, 129, 0.35); border-radius:8px; padding:6px 10px; margin-top:8px; color:#34D399; font-size:11.5px; font-weight:700;">🔓 BẢN PDF MIỄN PHÍ (OPEN ACCESS): Có thể tải trực tiếp.</div>';
        }} else {{
            badgeHtml += '<div style="background:rgba(244, 63, 94, 0.1); border:1px solid rgba(244, 63, 94, 0.3); border-radius:8px; padding:6px 10px; margin-top:8px; color:#FB7185; font-size:11.5px; font-weight:700;">🔒 CẦN QUYỀN TRUY CẬP (PAYWALL): Yêu cầu tài khoản thư viện hoặc mua bài.</div>';
        }}

        document.getElementById('modal-gen-badge').innerHTML = badgeHtml;
        document.getElementById('modal-title').innerText = p.title;
        document.getElementById('modal-authors').innerHTML = '<b>Tác giả:</b> ' + p.authors + ' (' + p.year + ')';
        document.getElementById('modal-venue').innerHTML = '<b>Tạp chí:</b> ' + p.venue + ' | <b>Phân loại:</b> ' + p.study_type;
        document.getElementById('modal-citations').innerHTML = '<b>Trích dẫn Scopus:</b> <span style="color:#38BDF8; font-weight:bold;">' + p.citation_count + '</span> lượt trích dẫn';

        var doiBtn = document.getElementById('modal-doi-link');
        if (p.doi_url || p.landing_url) {{
            doiBtn.href = p.doi_url || p.landing_url;
            doiBtn.innerText = 'Mở bài báo gốc (DOI) ↗';
            doiBtn.style.display = 'inline-flex';
        }} else {{
            doiBtn.style.display = 'none';
        }}

        var pdfBtn = document.getElementById('modal-pdf-link');
        if (p.pdf_url) {{
            pdfBtn.href = p.pdf_url;
            pdfBtn.innerText = '🔓 Tải bản full PDF miễn phí ↗';
            pdfBtn.style.background = '#059669';
            pdfBtn.style.borderColor = '#10B981';
            pdfBtn.style.color = '#FFFFFF';
            pdfBtn.style.display = 'inline-flex';
        }} else {{
            pdfBtn.style.display = 'none';
        }}

        var oaBtn = document.getElementById('modal-openalex-link');
        oaBtn.href = p.openalex_url || ('https://openalex.org/works?filter=doi:' + p.doi);
        oaBtn.innerText = 'Hồ sơ OpenAlex ↗';

        document.getElementById('modal-abstract-vi').innerText = p.abstract_vi || p.abstract || 'Đang cập nhật tóm tắt tiếng Việt...';
        document.getElementById('modal-abstract-en').innerText = p.abstract_en || p.abstract || 'Abstract in English...';
        switchModalLang('vi');

        var lineageHtml = '';
        var outList = p.outgoing_ids || [];
        var inList = p.incoming_ids || [];

        if (outList.length > 0) {{
            lineageHtml += '<div style="font-size:11.5px; color:#38BDF8; font-weight:700; margin-bottom:4px;">⬇️ TÀI LIỆU CÔNG TRÌNH NÀY TRÍCH DẪN (' + outList.length + ' bài):</div>';
            outList.forEach(function(targetId) {{
                var targetP = metaDict[targetId];
                if (targetP) {{
                    lineageHtml += '<div class="lineage-chip" onclick="jumpToNode(\\'' + targetId + '\\')">↳ ' + targetP.first_author + ' (' + targetP.year + '): ' + targetP.title.substring(0, 52) + '...</div>';
                }}
            }});
        }}

        if (inList.length > 0) {{
            lineageHtml += '<div style="font-size:11.5px; color:#34D399; font-weight:700; margin:8px 0 4px 0;">⬆️ ĐƯỢC TRÍCH DẪN BỞI CÁC BÀI (' + inList.length + ' bài):</div>';
            inList.forEach(function(srcId) {{
                var srcP = metaDict[srcId];
                if (srcP) {{
                    lineageHtml += '<div class="lineage-chip" onclick="jumpToNode(\\'' + srcId + '\\')">↰ ' + srcP.first_author + ' (' + srcP.year + '): ' + srcP.title.substring(0, 52) + '...</div>';
                }}
            }});
        }}

        document.getElementById('modal-lineage-content').innerHTML = lineageHtml;
        modal.style.display = 'flex';
        
        network.focus(nodeId, {{
            scale: 1.25,
            animation: {{ duration: 350, easingFunction: 'easeInOutQuad' }}
        }});
    }}

    function jumpToNode(nodeId) {{
        showPaperModal(nodeId);
        network.selectNodes([nodeId]);
    }}

    function closePaperModal() {{
        document.getElementById('paper-modal').style.display = 'none';
    }}

    function togglePhysics() {{
        isPhysicsOn = !isPhysicsOn;
        network.setOptions({{ physics: {{ enabled: isPhysicsOn }} }});
        var btn = document.getElementById('physicsBtn');
        btn.innerHTML = isPhysicsOn ? '⚡ Tắt Physics' : '⚡ Bật Physics';
    }}

    function toggleFullScreen() {{
        var elem = document.getElementById('network-wrapper');
        if (!document.fullscreenElement) {{
            if (elem.requestFullscreen) elem.requestFullscreen();
            else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
        }} else {{
            if (document.exitFullscreen) document.exitFullscreen();
        }}
    }}

    function popoutWindow() {{
        var currentHtml = document.documentElement.outerHTML;
        var blob = new Blob([currentHtml], {{type: 'text/html;charset=utf-8'}});
        var blobUrl = URL.createObjectURL(blob);
        var win = window.open(blobUrl, '_blank', 'width=1340,height=880,menubar=no,toolbar=no,location=no,status=no');
        if (!win) {{
            alert('Trình duyệt đã chặn popup. Vui lòng cho phép popup để mở màn hình phụ!');
        }}
    }}

    function searchAndFocusNode(query) {{
        if (!query || query.trim() === '') return;
        var q = query.toLowerCase().trim();
        var foundId = null;
        rawNodes.forEach(function(n) {{
            var lbl = (n.label || '').toLowerCase();
            if (lbl.indexOf(q) !== -1) {{
                if (!foundId) foundId = n.id;
            }}
        }});
        if (foundId) {{
            showPaperModal(foundId);
            network.selectNodes([foundId]);
        }}
    }}
</script>
</body>
</html>"""
        return html_template

    def filter_and_generate_network_html(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        min_year: int = 1990,
        max_year: int = 2030,
        min_citations: int = 0,
        study_type: str = "Tất cả chủ đề",
        only_oa: bool = False,
        height: str = "720px",
        width: str = "100%"
    ) -> str:
        """
        Dynamically filter nodes and edges based on publication year, citations, study theme, and OA status.
        """
        filtered_nodes = {}
        for nid, meta in nodes.items():
            try:
                yr = int(meta.get("year", 2020))
            except (ValueError, TypeError):
                yr = 2020
                
            cites = meta.get("citation_count", 0) or 0
            is_oa = meta.get("is_oa", False) or bool(meta.get("pdf_url"))
            stype = meta.get("study_type", "Empirical Journalism Study")
            
            if yr < min_year or yr > max_year:
                continue
            if cites < min_citations:
                continue
            if only_oa and not is_oa:
                continue
            if study_type != "Tất cả chủ đề" and stype != study_type:
                continue
                
            filtered_nodes[nid] = meta

        filtered_edges = [(u, v) for u, v in edges if u in filtered_nodes and v in filtered_nodes]
        
        if not filtered_nodes:
            return self.generate_network_html(nodes, edges, height=height, width=width)
            
        return self.generate_network_html(filtered_nodes, filtered_edges, height=height, width=width)
