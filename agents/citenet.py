import math
import json
import html
from typing import Dict, List, Any, Tuple, Optional, Union
from utils.openalex_client import OpenAlexClient, parse_doi_list
from utils.bib_formatter import generate_bibtex, generate_ris, papers_to_dataframe

class CiteNetAgent:
    """
    Trợ lý 1: CiteNet (Graph Expansion & Diamond Network Builder)
    Nhận 1 hoặc NHIỀU seed DOIs, tự động dò tìm và dựng Mạng lưới Tri thức Kim cương 2 chiều (Bidirectional Diamond Knowledge Graph):
    - Khám phá cội nguồn lý thuyết (Backward References R1-R3: Theoretical Roots & Seminal Works)
    - Khám phá bước tiến tương lai (Forward Citations F1-F3: Frontier Advances & Derivative Works)
    - Tự động bóc tách Citation Closure & Cross-links.
    Chuẩn hóa theo các quy chuẩn thư mục học quốc tế (Bibliometric & Scientometric standards).
    """
    def __init__(self, email: Optional[str] = None):
        self.client = OpenAlexClient(email=email)

    def run(
        self,
        seed_dois: Union[str, List[str]],
        *args,
        backward_limit: Optional[int] = None,
        forward_limit: Optional[int] = None,
        max_depth: int = 2,
        gen1_limit: Optional[int] = None,
        gen2_limit: Optional[int] = None,
        progress_callback=None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute CiteNet pipeline with Bidirectional Diamond Knowledge Graph.
        Hỗ trợ phân giải linh hoạt 100% các biến số tương thích ngược.
        """
        # Phân giải backward_limit
        if backward_limit is None:
            backward_limit = kwargs.get("backward_lim", 15)
            
        # Phân giải forward_limit
        if forward_limit is None:
            if "forward_lim" in kwargs:
                forward_limit = kwargs["forward_lim"]
            elif gen1_limit is not None:
                forward_limit = gen1_limit
            elif "g1_lim" in kwargs:
                forward_limit = kwargs["g1_lim"]
            else:
                forward_limit = 25
                
        # Phân giải max_depth
        if "depth" in kwargs:
            max_depth = kwargs["depth"]
        elif "cfg_depth" in kwargs:
            max_depth = kwargs["cfg_depth"]

        if progress_callback is None and "cb" in kwargs:
            progress_callback = kwargs["cb"]

        nodes_dict, edges_list, seed_papers = self.client.build_bidirectional_diamond_network(
            seed_dois=seed_dois,
            backward_limit=backward_limit,
            forward_limit=forward_limit,
            max_depth=max_depth,
            progress_callback=progress_callback
        )

        papers_list = list(nodes_dict.values())
        primary_seed = seed_papers[0] if seed_papers else (papers_list[0] if papers_list else {})

        if progress_callback:
            progress_callback(85, "Đang khởi tạo đồ thị tương tác Kim cương 2 chiều và tính toán layout thời gian...")

        network_html = self.generate_network_html(nodes_dict, edges_list)

        if progress_callback:
            progress_callback(95, "Đang xuất thư viện trích dẫn BibTeX, RIS và bảng dữ liệu CSV...")

        df_refs = papers_to_dataframe(papers_list)
        refs_csv = df_refs.to_csv(index=False, encoding="utf-8")
        refs_bib = generate_bibtex(papers_list)
        refs_ris = generate_ris(papers_list)

        seed_count = len(seed_papers)
        backward_papers = [p for p in papers_list if p.get("layer") == "backward" or (isinstance(p.get("level"), (int, float)) and p.get("level") < 0)]
        forward_papers = [p for p in papers_list if p.get("layer") == "forward" or (isinstance(p.get("level"), (int, float)) and p.get("level") > 0)]
        
        backward_count = len(backward_papers)
        forward_count = len(forward_papers)
        
        # Đếm thế hệ chi tiết
        r1_count = sum(1 for p in papers_list if p.get("level") == -1)
        r2_count = sum(1 for p in papers_list if p.get("level") == -2)
        r3_count = sum(1 for p in papers_list if p.get("level") <= -3)
        f1_count = sum(1 for p in papers_list if p.get("level") == 1)
        f2_count = sum(1 for p in papers_list if p.get("level") == 2)
        f3_count = sum(1 for p in papers_list if p.get("level") >= 3)
        
        oa_papers = [p for p in papers_list if p.get("is_oa") or bool(p.get("pdf_url"))]
        paywall_papers = [p for p in papers_list if not (p.get("is_oa") or bool(p.get("pdf_url")))]
        oa_count = len(oa_papers)
        paywall_count = len(paywall_papers)
        oa_percent = round((oa_count / len(papers_list) * 100), 1) if papers_list else 0.0

        # Phân loại và tính toán chỉ số Topo liên kết (Edge Ontology Metrics)
        edge_set = set(edges_list)
        direct_edges_cnt = 0
        mutual_edges_cnt = 0
        cross_bridge_cnt = 0
        intra_layer_cnt = 0

        for src, dst in edges_list:
            s_node = nodes_dict.get(src, {})
            d_node = nodes_dict.get(dst, {})
            s_lvl = s_node.get("level", 0)
            d_lvl = d_node.get("level", 0)
            
            if (dst, src) in edge_set and src != dst:
                mutual_edges_cnt += 1
            elif (s_lvl >= 2 and d_lvl <= -1) or (s_lvl <= -2 and d_lvl >= 1) or (s_lvl >= 1 and d_lvl <= -2) or (abs(s_lvl - d_lvl) >= 2 and s_lvl != 0 and d_lvl != 0):
                cross_bridge_cnt += 1
            elif s_lvl == d_lvl and s_lvl != 0:
                intra_layer_cnt += 1
            else:
                direct_edges_cnt += 1

        reciprocity_rate = round((mutual_edges_cnt / len(edges_list) * 100), 1) if edges_list else 0.0

        stats = {
            "total_papers": len(papers_list),
            "total_links": len(edges_list),
            "seed_count": seed_count,
            "seed_titles": [p.get("title", "") for p in seed_papers],
            "seed_dois": [p.get("doi", "") for p in seed_papers],
            "seed_title": primary_seed.get("title", "Seed Paper"),
            "seed_doi": primary_seed.get("doi", ""),
            "backward_count": backward_count,
            "forward_count": forward_count,
            "r1_count": r1_count,
            "r2_count": r2_count,
            "r3_count": r3_count,
            "f1_count": f1_count,
            "f2_count": f2_count,
            "f3_count": f3_count,
            # Các chỉ số Topo liên kết mới
            "direct_links_count": direct_edges_cnt,
            "mutual_links_count": mutual_edges_cnt,
            "cross_bridge_count": cross_bridge_cnt,
            "intra_layer_count": intra_layer_cnt,
            "reciprocity_rate": reciprocity_rate,
            # Giữ tương thích ngược với các trường cũ
            "gen0_count": seed_count,
            "gen1_count": f1_count if f1_count > 0 else forward_count,
            "gen2_count": f2_count if f2_count > 0 else backward_count,
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
        width: str = "100%",
        standalone_fullscreen: bool = False,
        hide_bottom_panels: bool = False
    ) -> str:
        """
        Construct interactive HTML graph with commercial Obsidian styling, international bibliometric node sizing,
        dynamic zoom controls, and a Dual-Mode (Force-directed vs Chronological Timeline evolution) layout.
        Color coding follows the Bidirectional Diamond Knowledge Graph standard:
        - 🔴 F0 (Seed): Ruby Red (#EA4335)
        - 🟣 R1-R3 (Backward Theoretical Roots): Royal Purple (#7C3AED), Indigo (#6366F1), Deep Indigo (#4338CA)
        - 🟢 F1-F3 (Forward Frontier Advances): Sky Cyan (#0284C7), Emerald (#059669), Amber (#D97706)
        
        Nếu standalone_fullscreen=True hoặc hide_bottom_panels=True, đồ thị sẽ tự động tối ưu hóa cho màn hình phụ độc lập
        (chỉ hiển thị Header HUD Bar + Slim Left Dock + Canvas mạng lưới phát sáng 100vh toàn màn hình).
        """
        is_standalone = standalone_fullscreen or hide_bottom_panels
        deck_height_css = "height: 100vh; min-height: 100vh;" if is_standalone else "height: 860px; min-height: 860px;"
        middle_height_css = "height: calc(100vh - 76px); min-height: calc(100vh - 76px);" if is_standalone else "height: 540px; min-height: 480px;"
        bottom_display_css = "display: none !important;" if is_standalone else "display: grid;"
        body_min_height_css = "min-height: 100vh;" if is_standalone else "min-height: 860px;"
        
        # Bảng màu Kim Cương Tri Thức Đa Tầng Mặc Định (Synapse Cyan Theme)
        color_map = {
            0: {"background": "#EA4335", "border": "#FF8A80", "highlight": "#FFEBEE"},   # F0: Seed Core (Ruby Red)
            -1: {"background": "#7C3AED", "border": "#A78BFA", "highlight": "#EDE9FE"},  # R1: Tham chiếu Nền tảng trực tiếp (Royal Purple)
            -2: {"background": "#6366F1", "border": "#818CF8", "highlight": "#EEF2FF"},  # R2: Cội nguồn lý thuyết mở rộng (Indigo)
            -3: {"background": "#4338CA", "border": "#6366F1", "highlight": "#E0E7FF"},  # R3: Nền tảng sâu xa (Deep Indigo)
            1: {"background": "#0284C7", "border": "#38BDF8", "highlight": "#E0F2FE"},   # F1: Kế thừa & Phát triển trực tiếp (Sky Cyan)
            2: {"background": "#059669", "border": "#34D399", "highlight": "#ECFDF5"},   # F2: Bước tiến phái sinh mở rộng (Emerald Green)
            3: {"background": "#D97706", "border": "#FBBF24", "highlight": "#FFFBEB"}    # F3: Chân trời nghiên cứu mới (Amber Gold)
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

        outgoing_map = {}
        incoming_map = {}
        for s, dst in edges:
            if s in nodes and dst in nodes:
                outgoing_map[s] = outgoing_map.get(s, 0) + 1
                incoming_map[dst] = incoming_map.get(dst, 0) + 1

        vis_nodes = []
        for node_id, meta in nodes.items():
            level = meta.get("level", 0)
            layer = meta.get("layer", "seed")
            cites = meta.get("citation_count", 0) or 0
            tot_conn = outgoing_map.get(node_id, 0) + incoming_map.get(node_id, 0)
            is_isolated = (tot_conn == 0)
            
            # Chuẩn quốc tế: Tính kích cỡ node theo quy luật logarit số trích dẫn (Price's Law)
            base_size = 16
            if cites > 0:
                log_scale = math.log(cites + 1, 1.5) * 4.2
                node_size = max(16, min(56, int(base_size + log_scale)))
            else:
                node_size = 16
            if level == 0 or layer == "seed":
                node_size = max(node_size + 10, 36)

            # Chọn màu theo cấp bậc level
            if level in color_map:
                colors = color_map[level]
            elif level < -3:
                colors = color_map[-3]
            elif level > 3:
                colors = color_map[3]
            else:
                colors = color_map[2]

            first_auth = meta.get("first_author", "Tác giả").split()[-1] if meta.get("first_author") else "Paper"
            year = meta.get("year", "n.d.")
            raw_title = meta.get("title", "Untitled Paper")
            clean_title = raw_title.replace('"', '').replace("'", "")
            truncated_title = clean_title[:45] + "..." if len(clean_title) > 45 else clean_title
            
            # Nhãn rút gọn chuẩn học thuật [Tác giả, Năm, Tầng & Số trích dẫn]
            if level == 0 or layer == "seed":
                short_label = f"★ {first_auth} ({year})\n[F0 • {cites} tc]"
                full_label = f"★ {first_auth} ({year})\n{truncated_title}\n[F0 • {cites} trích dẫn]"
            elif level < 0 or layer == "backward":
                r_tag = f"R{abs(level)}" if level != 0 else "R"
                if is_isolated:
                    short_label = f"⚡ {first_auth} ({year})\n[{r_tag} • {cites} tc • Độc lập]"
                    full_label = f"⚡ {first_auth} ({year})\n{truncated_title}\n[{r_tag} • {cites} tc • Độc lập]"
                else:
                    short_label = f"🏛️ {first_auth} ({year})\n[{r_tag} • {cites} tc]"
                    full_label = f"🏛️ {first_auth} ({year})\n{truncated_title}\n[{r_tag} • {cites} trích dẫn]"
            else:
                f_tag = f"F{level}" if level != 0 else "F"
                if is_isolated:
                    short_label = f"⚡ {first_auth} ({year})\n[{f_tag} • {cites} tc • Độc lập]"
                    full_label = f"⚡ {first_auth} ({year})\n{truncated_title}\n[{f_tag} • {cites} tc • Độc lập]"
                else:
                    short_label = f"🚀 {first_auth} ({year})\n[{f_tag} • {cites} tc]"
                    full_label = f"🚀 {first_auth} ({year})\n{truncated_title}\n[{f_tag} • {cites} trích dẫn]"

            # Tính tọa độ timeline ban đầu
            try:
                yr_int = int(year)
            except Exception:
                yr_int = min_yr
            x_timeline = (yr_int - min_yr) * 260 - ((max_yr - min_yr) * 130)
            
            is_seed = (level == 0 or layer == "seed")
            node_item = {
                "id": node_id,
                "label": short_label,
                "label_short": short_label,
                "label_full": full_label,
                "label_minimal": "",
                "value": cites + 1,
                "size": node_size,
                "color": colors,
                "borderWidth": 3.5 if is_seed else (2.6 if is_isolated else 1.8),
                "shapeProperties": {"borderDashes": [4, 4]} if is_isolated else {"borderDashes": False},
                "font": {
                    "size": 12 if is_seed else 11,
                    "color": "#F8FAFC",
                    "face": "Plus Jakarta Sans, sans-serif",
                    "strokeWidth": 3.2,
                    "strokeColor": "#0B0C0E"
                },
                "shape": "star" if is_seed else "dot",
                "x_timeline": x_timeline,
                "year": yr_int,
                "level": level,
                "layer": layer,
                "citations": cites,
                "is_isolated": is_isolated,
                "title": ""
            }
            vis_nodes.append(node_item)

        edge_set = set(edges)
        vis_edges = []
        for src, dst in edges:
            if src in nodes and dst in nodes:
                s_node = nodes.get(src, {})
                d_node = nodes.get(dst, {})
                s_lvl = s_node.get("level", 0)
                d_lvl = d_node.get("level", 0)
                s_auth = s_node.get("first_author", "Paper")
                d_auth = d_node.get("first_author", "Paper")
                s_yr = s_node.get("year", "")
                d_yr = d_node.get("year", "")

                is_mutual = (dst, src) in edge_set and src != dst
                is_cross_bridge = (s_lvl >= 2 and d_lvl <= -1) or (s_lvl <= -2 and d_lvl >= 1) or (s_lvl >= 1 and d_lvl <= -2) or (abs(s_lvl - d_lvl) >= 2 and s_lvl != 0 and d_lvl != 0)
                is_intra = (s_lvl == d_lvl and s_lvl != 0)

                if is_mutual:
                    edge_type = "mutual"
                    edge_color = {"color": "rgba(245, 158, 11, 0.85)", "highlight": "#F59E0B", "hover": "#F59E0B"}
                    edge_width = 2.6
                    edge_dashes = False
                    arrows = {"to": {"enabled": True, "scaleFactor": 0.95}, "from": {"enabled": True, "scaleFactor": 0.95}}
                elif is_cross_bridge:
                    edge_type = "cross_bridge"
                    edge_color = {"color": "rgba(192, 132, 252, 0.88)", "highlight": "#C084FC", "hover": "#C084FC"}
                    edge_width = 2.2
                    edge_dashes = [6, 4]
                    arrows = {"to": {"enabled": True, "scaleFactor": 0.95}}
                elif is_intra:
                    edge_type = "intra_layer"
                    edge_color = {"color": "rgba(52, 211, 153, 0.80)", "highlight": "#34D399", "hover": "#34D399"}
                    edge_width = 1.6
                    edge_dashes = [3, 3]
                    arrows = {"to": {"enabled": True, "scaleFactor": 0.85}}
                else:
                    edge_type = "direct"
                    edge_color = {"color": "rgba(56, 189, 248, 0.70)", "highlight": "#38BDF8", "hover": "#38BDF8"}
                    edge_width = 1.8
                    edge_dashes = False
                    arrows = {"to": {"enabled": True, "scaleFactor": 0.90}}

                vis_edges.append({
                    "id": f"e_{src}_{dst}",
                    "from": src,
                    "to": dst,
                    "edge_type": edge_type,
                    "color": edge_color,
                    "arrows": arrows,
                    "width": edge_width,
                    "dashes": edge_dashes,
                    "title": "",
                    "smooth": {"type": "curvedCW", "roundness": 0.22 if is_mutual else 0.16}
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
                "level": meta.get("level", 0),
                "layer": meta.get("layer", "seed"),
                "layer_label": meta.get("layer_label", "★ BÀI BÁO GỐC"),
                "is_oa": meta.get("is_oa", False) or bool(pdf_url),
                "abstract": abs_vi,
                "abstract_vi": abs_vi,
                "abstract_en": abs_en,
                "outgoing_ids": outgoing,
                "incoming_ids": incoming,
                "total_connections": len(outgoing) + len(incoming),
                "is_isolated": (len(outgoing) + len(incoming) == 0)
            }

        # Trích xuất tên đề tài chính từ bài gốc
        seed_nodes = [n for n in nodes.values() if n.get("level") == 0 or n.get("layer") == "seed"]
        primary_seed = seed_nodes[0] if seed_nodes else (list(nodes.values())[0] if nodes else {})
        seed_title = primary_seed.get("title", "Quantum Knowledge & Scientific Discovery")
        clean_seed_title = str(seed_title).replace('"', '').replace("'", "")
        short_project_name = clean_seed_title[:38] + "..." if len(clean_seed_title) > 38 else clean_seed_title

        nodes_json = json.dumps(vis_nodes, ensure_ascii=False)
        edges_json = json.dumps(vis_edges, ensure_ascii=False)
        meta_dict_json = json.dumps(extended_meta, ensure_ascii=False)

        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Synapse Academic — Global Citation Network HUD</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style type="text/css">
        :root {{
            --theme-glow: #00F2FE;
            --theme-glow-rgb: 0, 242, 254;
            --theme-bg-base: #040914;
            --theme-panel-bg: rgba(6, 14, 28, 0.84);
            --theme-panel-border: rgba(0, 242, 254, 0.32);
            --theme-accent: #00F2FE;
            --theme-accent-hover: #38BDF8;
            --theme-text-main: #F8FAFC;
            --theme-text-dim: #94A3B8;
            --theme-badge-bg: rgba(0, 242, 254, 0.14);
            --theme-hud-shadow: 0 0 20px rgba(0, 242, 254, 0.20), 0 4px 20px rgba(0, 0, 0, 0.45);
        }}

        /* 10 HIGH-CONTRAST THEMES (BAO GỒM MATRIX & MONOCHROME CLASSIC ĐEN TRẮNG) */
        body.theme-synapse-cyan {{
            --theme-glow: #00F2FE;
            --theme-glow-rgb: 0, 242, 254;
            --theme-bg-base: #040914;
            --theme-panel-bg: rgba(6, 14, 28, 0.86);
            --theme-panel-border: rgba(0, 242, 254, 0.35);
            --theme-accent: #00F2FE;
            --theme-accent-hover: #38BDF8;
            --theme-text-main: #F8FAFC;
            --theme-text-dim: #94A3B8;
            --theme-badge-bg: rgba(0, 242, 254, 0.14);
            --theme-hud-shadow: 0 0 22px rgba(0, 242, 254, 0.22), 0 4px 20px rgba(0, 0, 0, 0.50);
        }}
        body.theme-emerald-matrix {{
            --theme-glow: #00FF66;
            --theme-glow-rgb: 0, 255, 102;
            --theme-bg-base: #020904;
            --theme-panel-bg: rgba(2, 22, 10, 0.90);
            --theme-panel-border: rgba(0, 255, 102, 0.45);
            --theme-accent: #00FF66;
            --theme-accent-hover: #33FF88;
            --theme-text-main: #E6FFE6;
            --theme-text-dim: #55CC77;
            --theme-badge-bg: rgba(0, 255, 102, 0.16);
            --theme-hud-shadow: 0 0 24px rgba(0, 255, 102, 0.28), 0 4px 20px rgba(0, 0, 0, 0.65);
        }}
        body.theme-monochrome-classic {{
            --theme-glow: #FFFFFF;
            --theme-glow-rgb: 255, 255, 255;
            --theme-bg-base: #0A0A0A;
            --theme-panel-bg: rgba(20, 20, 20, 0.94);
            --theme-panel-border: rgba(255, 255, 255, 0.45);
            --theme-accent: #FFFFFF;
            --theme-accent-hover: #D4D4D8;
            --theme-text-main: #FFFFFF;
            --theme-text-dim: #A1A1AA;
            --theme-badge-bg: rgba(255, 255, 255, 0.15);
            --theme-hud-shadow: 0 0 20px rgba(255, 255, 255, 0.20), 0 4px 20px rgba(0, 0, 0, 0.70);
        }}
        body.theme-nebula-violet {{
            --theme-glow: #C084FC;
            --theme-glow-rgb: 192, 132, 252;
            --theme-bg-base: #090514;
            --theme-panel-bg: rgba(18, 10, 34, 0.88);
            --theme-panel-border: rgba(192, 132, 252, 0.38);
            --theme-accent: #C084FC;
            --theme-accent-hover: #E879F9;
            --theme-text-main: #FAF5FF;
            --theme-text-dim: #C4B5FD;
            --theme-badge-bg: rgba(192, 132, 252, 0.16);
            --theme-hud-shadow: 0 0 22px rgba(192, 132, 252, 0.24), 0 4px 20px rgba(0, 0, 0, 0.50);
        }}
        body.theme-solar-amber {{
            --theme-glow: #F59E0B;
            --theme-glow-rgb: 245, 158, 11;
            --theme-bg-base: #120A03;
            --theme-panel-bg: rgba(30, 18, 6, 0.88);
            --theme-panel-border: rgba(245, 158, 11, 0.40);
            --theme-accent: #F59E0B;
            --theme-accent-hover: #FCD34D;
            --theme-text-main: #FFFBEB;
            --theme-text-dim: #FDE68A;
            --theme-badge-bg: rgba(245, 158, 11, 0.18);
            --theme-hud-shadow: 0 0 22px rgba(245, 158, 11, 0.25), 0 4px 20px rgba(0, 0, 0, 0.55);
        }}
        body.theme-deep-ocean {{
            --theme-glow: #38BDF8;
            --theme-glow-rgb: 56, 189, 248;
            --theme-bg-base: #03132B;
            --theme-panel-bg: rgba(6, 28, 58, 0.90);
            --theme-panel-border: rgba(56, 189, 248, 0.40);
            --theme-accent: #38BDF8;
            --theme-accent-hover: #7DD3FC;
            --theme-text-main: #F0F9FF;
            --theme-text-dim: #BAE6FD;
            --theme-badge-bg: rgba(56, 189, 248, 0.16);
            --theme-hud-shadow: 0 0 22px rgba(56, 189, 248, 0.24), 0 4px 20px rgba(0, 0, 0, 0.55);
        }}
        body.theme-crimson-ruby {{
            --theme-glow: #F43F5E;
            --theme-glow-rgb: 244, 63, 94;
            --theme-bg-base: #160408;
            --theme-panel-bg: rgba(36, 8, 16, 0.90);
            --theme-panel-border: rgba(244, 63, 94, 0.40);
            --theme-accent: #F43F5E;
            --theme-accent-hover: #FB7185;
            --theme-text-main: #FFF1F2;
            --theme-text-dim: #FECDD3;
            --theme-badge-bg: rgba(244, 63, 94, 0.16);
            --theme-hud-shadow: 0 0 22px rgba(244, 63, 94, 0.25), 0 4px 20px rgba(0, 0, 0, 0.55);
        }}
        body.theme-nordic-frost {{
            --theme-glow: #0284C7;
            --theme-glow-rgb: 2, 132, 199;
            --theme-bg-base: #F1F5F9;
            --theme-panel-bg: rgba(255, 255, 255, 0.94);
            --theme-panel-border: rgba(2, 132, 199, 0.40);
            --theme-accent: #0284C7;
            --theme-accent-hover: #0369A1;
            --theme-text-main: #0F172A;
            --theme-text-dim: #475569;
            --theme-badge-bg: rgba(2, 132, 199, 0.12);
            --theme-hud-shadow: 0 0 20px rgba(2, 132, 199, 0.16), 0 4px 20px rgba(15, 23, 42, 0.12);
        }}
        body.theme-vintage-parchment {{
            --theme-glow: #B45309;
            --theme-glow-rgb: 180, 83, 9;
            --theme-bg-base: #FBF8F1;
            --theme-panel-bg: rgba(248, 243, 231, 0.95);
            --theme-panel-border: rgba(180, 83, 9, 0.38);
            --theme-accent: #B45309;
            --theme-accent-hover: #92400E;
            --theme-text-main: #292524;
            --theme-text-dim: #57534E;
            --theme-badge-bg: rgba(180, 83, 9, 0.12);
            --theme-hud-shadow: 0 0 20px rgba(180, 83, 9, 0.14), 0 4px 18px rgba(41, 37, 36, 0.10);
        }}
        body.theme-neon-gold {{
            --theme-glow: #EAB308;
            --theme-glow-rgb: 234, 179, 8;
            --theme-bg-base: #0E0C02;
            --theme-panel-bg: rgba(24, 20, 4, 0.90);
            --theme-panel-border: rgba(234, 179, 8, 0.42);
            --theme-accent: #EAB308;
            --theme-accent-hover: #FACC15;
            --theme-text-main: #FEFCE8;
            --theme-text-dim: #FEF08A;
            --theme-badge-bg: rgba(234, 179, 8, 0.18);
            --theme-hud-shadow: 0 0 22px rgba(234, 179, 8, 0.26), 0 4px 20px rgba(0, 0, 0, 0.60);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }}
        html, body {{
            width: 100%;
            height: 100%;
            {body_min_height_css}
            overflow-x: hidden;
            background-color: var(--theme-bg-base);
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            color: var(--theme-text-main);
            transition: background 0.3s ease, color 0.3s ease;
        }}

        /* MAIN SCI-FI HUD DECK CONTAINER */
        #synapse-hud-deck {{
            display: flex;
            flex-direction: column;
            width: 100%;
            {deck_height_css}
            box-sizing: border-box;
            padding: 10px;
            gap: 10px;
            background: radial-gradient(circle at 50% 20%, rgba(var(--theme-glow-rgb), 0.08) 0%, transparent 70%);
        }}

        /* 1. TOP HEADER HUD BAR (ĐỔ BÓNG ĐỀU TOÀN KHUNG) */
        .synapse-header-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 18px;
            background: var(--theme-panel-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--theme-panel-border);
            border-radius: 14px;
            box-shadow: var(--theme-hud-shadow);
            flex-shrink: 0;
        }}
        .brand-logo-cluster {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .brand-atom-icon {{
            font-size: 20px;
            color: var(--theme-accent);
            text-shadow: 0 0 12px var(--theme-glow);
            animation: atomSpin 18s linear infinite;
        }}
        @keyframes atomSpin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        .brand-title {{
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 0.08em;
            color: var(--theme-text-main);
            text-transform: uppercase;
        }}
        .brand-subtitle {{
            font-size: 10px;
            color: var(--theme-accent);
            font-weight: 700;
            letter-spacing: 0.12em;
        }}

        .header-meta-cluster {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .meta-chip {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: var(--theme-badge-bg);
            border: 1px solid var(--theme-panel-border);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11.5px;
            font-weight: 600;
            color: var(--theme-text-main);
            box-shadow: 0 0 10px rgba(var(--theme-glow-rgb), 0.08);
        }}
        .pulse-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 8px #10B981;
            animation: blink 1.6s infinite ease-in-out;
        }}
        @keyframes blink {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(0.85); }}
        }}

        /* 2. MIDDLE AREA (SLIM DOCK + GRAPH CANVAS) */
        .synapse-middle-deck {{
            display: flex;
            flex: 1;
            gap: 10px;
            {middle_height_css}
            position: relative;
        }}

        /* SLIM VERTICAL DOCK BAR (ĐỔ BÓNG ĐỀU TOÀN KHUNG) */
        .synapse-vertical-dock {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 10px 5px;
            background: var(--theme-panel-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--theme-panel-border);
            border-radius: 14px;
            box-shadow: var(--theme-hud-shadow);
            width: 52px;
            flex-shrink: 0;
            overflow-y: auto;
            scrollbar-width: none;
        }}
        .synapse-vertical-dock::-webkit-scrollbar {{
            display: none;
        }}
        .dock-btn-group {{
            display: flex;
            flex-direction: column;
            gap: 7px;
            width: 100%;
            align-items: center;
        }}
        .dock-icon-btn {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: transparent;
            border: 1px solid transparent;
            color: var(--theme-text-dim);
            font-size: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .dock-icon-btn:hover {{
            color: var(--theme-accent);
            border-color: var(--theme-panel-border);
            background: var(--theme-badge-bg);
            box-shadow: 0 0 14px rgba(var(--theme-glow-rgb), 0.35);
            transform: scale(1.08);
        }}
        .dock-icon-btn.active {{
            color: var(--theme-text-main);
            border-color: var(--theme-accent);
            background: var(--theme-badge-bg);
            box-shadow: 0 0 16px rgba(var(--theme-glow-rgb), 0.45);
        }}

        /* GRAPH CANVAS WRAPPER (ĐỔ BÓNG ĐỀU TOÀN KHUNG) */
        .synapse-graph-container {{
            position: relative;
            flex: 1;
            height: 100%;
            background: var(--theme-panel-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--theme-panel-border);
            border-radius: 16px;
            box-shadow: var(--theme-hud-shadow);
            overflow: hidden;
        }}
        #network-container {{
            width: 100%;
            height: 100%;
        }}

        /* FLOATING HUD CONTROLS INSIDE GRAPH */
        .graph-overlay-header {{
            position: absolute;
            top: 14px;
            left: 16px;
            z-index: 50;
            pointer-events: none;
        }}
        .graph-title {{
            font-size: 15px;
            font-weight: 800;
            letter-spacing: 0.04em;
            color: var(--theme-text-main);
            text-shadow: 0 0 12px rgba(var(--theme-glow-rgb), 0.45);
        }}
        .graph-subtitle {{
            font-size: 11px;
            color: var(--theme-accent);
            font-weight: 600;
            letter-spacing: 0.02em;
        }}

        .graph-top-tools {{
            position: absolute;
            top: 12px;
            right: 14px;
            z-index: 60;
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(var(--theme-glow-rgb), 0.08);
            backdrop-filter: blur(16px);
            padding: 4px 8px;
            border-radius: 12px;
            border: 1px solid var(--theme-panel-border);
            box-shadow: 0 0 16px rgba(var(--theme-glow-rgb), 0.15);
            max-width: calc(100% - 32px);
            flex-wrap: wrap;
            justify-content: flex-end;
        }}
        .hud-mini-btn {{
            background: var(--theme-panel-bg);
            border: 1px solid var(--theme-panel-border);
            color: var(--theme-text-main);
            padding: 5px 9px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.18s ease;
            white-space: nowrap;
            box-shadow: 0 0 8px rgba(var(--theme-glow-rgb), 0.08);
        }}
        .hud-mini-btn:hover {{
            border-color: var(--theme-accent);
            color: #FFFFFF;
            box-shadow: 0 0 14px rgba(var(--theme-glow-rgb), 0.35);
            transform: translateY(-1px);
        }}
        .hud-mini-btn.active {{
            background: var(--theme-accent);
            border-color: var(--theme-accent);
            color: #040914;
            font-weight: 800;
            box-shadow: 0 0 14px var(--theme-glow);
        }}

        /* SPEED SLIDER CLUSTER TRÊN THANH CÔNG CỤ */
        .speed-control-cluster {{
            display: flex;
            align-items: center;
            gap: 5px;
            background: var(--theme-panel-bg);
            border: 1px solid var(--theme-panel-border);
            padding: 3px 8px;
            border-radius: 8px;
            box-shadow: 0 0 8px rgba(var(--theme-glow-rgb), 0.08);
        }}
        .speed-slider-input {{
            width: 60px;
            cursor: pointer;
            accent-color: var(--theme-accent);
            height: 4px;
        }}

        /* SMART HUD HOVER INSPECTOR (CHO NODE - ĐỔ BÓNG ĐỀU TOÀN KHUNG) */
        .hud-hover-inspector {{
            position: absolute;
            top: 58px;
            left: 68px;
            z-index: 65;
            width: 330px;
            max-width: calc(100% - 90px);
            background: var(--theme-panel-bg);
            backdrop-filter: blur(22px);
            -webkit-backdrop-filter: blur(22px);
            border: 1.5px solid var(--theme-accent);
            border-radius: 12px;
            padding: 10px 14px;
            box-shadow: 0 0 24px rgba(var(--theme-glow-rgb), 0.35), 0 4px 20px rgba(0,0,0,0.5);
            pointer-events: auto;
            transition: opacity 0.2s ease, transform 0.2s ease;
            opacity: 0;
            transform: translateY(-4px);
        }}
        .hud-hover-inspector.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        .hover-inspector-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
        }}
        .hover-inspector-title {{
            font-size: 12px;
            font-weight: 800;
            color: var(--theme-text-main);
            line-height: 1.35;
            margin-bottom: 5px;
        }}
        .hover-inspector-meta {{
            font-size: 10.5px;
            color: var(--theme-accent);
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .hover-inspector-links {{
            font-size: 10px;
            color: var(--theme-text-dim);
            border-top: 1px solid rgba(var(--theme-glow-rgb), 0.15);
            padding-top: 4px;
        }}

        /* EDGE EPISTEMIC INSPECTOR (CHO MŨI TÊN - VÙNG AN TOÀN TRÁI DƯỚI) */
        .edge-epistemic-inspector {{
            position: absolute;
            bottom: 20px;
            left: 68px;
            z-index: 65;
            width: 340px;
            max-width: calc(100% - 90px);
            background: rgba(26, 16, 6, 0.94);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1.5px solid #F59E0B;
            border-radius: 12px;
            padding: 9px 13px;
            box-shadow: 0 0 24px rgba(245, 158, 11, 0.35), 0 4px 20px rgba(0,0,0,0.5);
            pointer-events: auto;
            transition: opacity 0.2s ease, transform 0.2s ease;
            opacity: 0;
            transform: translateY(4px);
            font-family: 'Roboto', -apple-system, sans-serif;
            font-weight: 300;
            font-size: 10.5px;
            color: #FFFBEB;
            line-height: 1.45;
        }}
        .edge-epistemic-inspector.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        .edge-inspector-tag {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 9.5px;
            font-weight: 500;
            color: #FDE047;
            background: rgba(245, 158, 11, 0.18);
            border: 1px solid rgba(245, 158, 11, 0.4);
            padding: 2px 7px;
            border-radius: 6px;
            margin-bottom: 5px;
            letter-spacing: 0.03em;
        }}

        /* SLIDE-OUT LEGEND DRAWER FROM SLIM DOCK (ĐỔ BÓNG ĐỀU TOÀN KHUNG) */
        .dock-legend-drawer {{
            position: absolute;
            left: 68px;
            top: 0;
            bottom: 0;
            width: 350px;
            background: var(--theme-panel-bg);
            backdrop-filter: blur(26px);
            -webkit-backdrop-filter: blur(26px);
            border: 1px solid var(--theme-panel-border);
            border-radius: 14px;
            box-shadow: var(--theme-hud-shadow);
            z-index: 100;
            display: none;
            flex-direction: column;
            overflow: hidden;
            animation: drawerSlide 0.22s ease forwards;
        }}
        @keyframes drawerSlide {{
            from {{ opacity: 0; transform: translateX(-15px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        .drawer-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: rgba(var(--theme-glow-rgb), 0.08);
            border-bottom: 1px solid var(--theme-panel-border);
            font-size: 12px;
            font-weight: 800;
            color: var(--theme-accent);
            letter-spacing: 0.04em;
        }}
        .drawer-body {{
            padding: 12px 14px;
            overflow-y: auto;
            flex: 1;
            font-size: 11px;
            line-height: 1.45;
            color: var(--theme-text-main);
        }}
        .legend-item-card {{
            display: flex;
            align-items: flex-start;
            gap: 8px;
            padding: 6px 9px;
            background: rgba(var(--theme-glow-rgb), 0.04);
            border: 1px solid rgba(var(--theme-glow-rgb), 0.15);
            border-radius: 8px;
            margin-bottom: 6px;
            box-shadow: 0 0 8px rgba(var(--theme-glow-rgb), 0.06);
        }}
        .legend-color-chip {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        /* 3. BOTTOM EXPANDABLE PANELS DECK (ĐỔ BÓNG ĐỀU TOÀN KHUNG) */
        .synapse-bottom-deck {{
            {bottom_display_css}
            grid-template-columns: 1fr 1.25fr;
            gap: 10px;
            height: 250px;
            min-height: 230px;
            flex-shrink: 0;
            transition: height 0.25s ease;
        }}
        .hud-panel-card {{
            display: flex;
            flex-direction: column;
            background: var(--theme-panel-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--theme-panel-border);
            border-radius: 14px;
            box-shadow: var(--theme-hud-shadow);
            overflow: hidden;
        }}
        .panel-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 14px;
            border-bottom: 1px solid rgba(var(--theme-glow-rgb), 0.15);
            background: rgba(var(--theme-glow-rgb), 0.04);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.05em;
            color: var(--theme-accent);
            text-transform: uppercase;
        }}
        .panel-card-body {{
            padding: 10px 14px;
            overflow-y: auto;
            flex: 1;
        }}

        /* BẢNG RELATED PAPERS MATRIX */
        .related-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}
        .related-table th {{
            text-align: left;
            padding: 5px 8px;
            color: var(--theme-text-dim);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}
        .related-table td {{
            padding: 6px 8px;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            color: var(--theme-text-main);
        }}
        .related-row {{
            cursor: pointer;
            transition: background 0.15s ease;
        }}
        .related-row:hover {{
            background: rgba(var(--theme-glow-rgb), 0.12);
        }}
        .related-row.selected {{
            background: rgba(var(--theme-glow-rgb), 0.22);
            font-weight: 700;
        }}
        .relevance-bar-track {{
            width: 70px;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-right: 4px;
        }}
        .relevance-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00C6FF 0%, var(--theme-glow) 100%);
            border-radius: 3px;
            box-shadow: 0 0 6px var(--theme-glow);
        }}

        /* SELECTED PAPER DETAILS TWO-COLUMN VIEW */
        .details-grid {{
            display: grid;
            grid-template-columns: 1.35fr 1fr;
            gap: 12px;
            height: 100%;
        }}
        .detail-abstract-pane {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            font-size: 11.5px;
            line-height: 1.55;
            color: var(--theme-text-main);
            overflow-y: auto;
        }}
        .detail-cocitation-pane {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            background: rgba(0,0,0,0.25);
            border: 1px solid rgba(var(--theme-glow-rgb), 0.18);
            border-radius: 10px;
            padding: 8px 10px;
            overflow-y: auto;
        }}
        .cocite-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: var(--theme-text-dim);
            cursor: pointer;
            padding: 3px 6px;
            border-radius: 6px;
            transition: all 0.15s ease;
        }}
        .cocite-item:hover {{
            color: var(--theme-accent);
            background: rgba(var(--theme-glow-rgb), 0.12);
        }}

        /* RESPONSIVE ON MOBILE & TABLET */
        @media (max-width: 900px) {{
            .synapse-bottom-deck {{
                grid-template-columns: 1fr;
                height: auto;
                max-height: 48vh;
            }}
            .synapse-header-bar {{
                padding: 6px 10px;
            }}
            .header-meta-cluster {{
                display: none;
            }}
            .details-grid {{
                grid-template-columns: 1fr;
            }}
            .synapse-vertical-dock {{
                width: 42px;
                padding: 8px 3px;
                border-radius: 10px;
            }}
            .dock-icon-btn {{
                width: 34px;
                height: 34px;
                font-size: 13px;
            }}
            .graph-top-tools {{
                max-width: calc(100% - 20px);
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                padding: 3px 6px;
                gap: 4px;
            }}
            .hud-hover-inspector, .edge-epistemic-inspector {{
                left: 10px !important;
                right: 10px !important;
                width: auto !important;
                max-width: calc(100% - 20px) !important;
                top: 52px !important;
                padding: 8px 10px !important;
            }}
        }}

        @media (max-width: 600px) {{
            #synapse-hud-deck {{
                padding: 6px;
                gap: 6px;
            }}
            .synapse-middle-deck {{
                gap: 6px;
            }}
        }}
    </style>
</head>
<body class="theme-synapse-cyan">
<div id="synapse-hud-deck">
    
    <!-- 1. TOP HEADER HUD BAR -->
    <header class="synapse-header-bar">
        <div class="brand-logo-cluster">
            <span class="brand-atom-icon">⚛️</span>
            <div>
                <div class="brand-title">SYNAPSE ACADEMIC</div>
                <div class="brand-subtitle">SCHOLARGRAPH PRO // QUANTUM DECK</div>
            </div>
        </div>

        <div class="header-meta-cluster">
            <div class="meta-chip" title="Đề tài nghiên cứu hạt nhân">
                <span>📁 PROJECT:</span>
                <b style="color:var(--theme-accent);">{short_project_name}</b>
            </div>
            <div class="meta-chip">
                <span>🎨 THEME:</span>
                <select id="themeSelector" onchange="changeThemeDirectly(this.value)" style="background:transparent; border:none; color:var(--theme-accent); font-weight:700; font-size:11px; outline:none; cursor:pointer;">
                    <option value="theme-synapse-cyan">1. Synapse Cyan</option>
                    <option value="theme-emerald-matrix">2. Matrix Cyber Green</option>
                    <option value="theme-monochrome-classic">3. Monochrome Đen-Trắng</option>
                    <option value="theme-nebula-violet">4. Nebula Violet</option>
                    <option value="theme-solar-amber">5. Solar Amber</option>
                    <option value="theme-deep-ocean">6. Deep Ocean</option>
                    <option value="theme-crimson-ruby">7. Crimson Ruby</option>
                    <option value="theme-nordic-frost">8. Nordic Frost</option>
                    <option value="theme-vintage-parchment">9. Vintage Parchment</option>
                    <option value="theme-neon-gold">10. Neon Gold</option>
                </select>
            </div>
            <div class="meta-chip" style="border-color:#10B981; color:#34D399;">
                <span class="pulse-dot"></span>
                <span>STATUS: ACTIVE</span>
            </div>
            <div class="meta-chip" id="realtimeClock" style="font-family:'JetBrains Mono', monospace; font-size:11px;">
                --:--
            </div>
        </div>
    </header>

    <!-- 2. MIDDLE DECK (DOCK + NETWORK CANVAS) -->
    <div class="synapse-middle-deck">
        <!-- SLIM VERTICAL DOCK (10 CHẾ ĐỘ BỐ CỤC HỌC THUẬT) -->
        <nav class="synapse-vertical-dock" style="position:relative;">
            <div class="dock-btn-group">
                <button class="dock-icon-btn active" id="dockBtnTimeline" onclick="switchLayoutMode('timeline')" title="1. Dòng Thời Gian Thẳng Ngang (Linear Timeline Evolution)">⏳</button>
                <button class="dock-icon-btn" id="dockBtnRadar" onclick="switchLayoutMode('radar')" title="2. Quỹ Đạo Radar Đồng Tâm (Concentric Radar Timeline)">📡</button>
                <button class="dock-icon-btn" id="dockBtnFishbone" onclick="switchLayoutMode('fishbone')" title="3. Sơ Đồ Xương Cá Học Thuật (Ishikawa Fishbone Diagram)">🐟</button>
                <button class="dock-icon-btn" id="dockBtnDendrogram" onclick="switchLayoutMode('dendrogram')" title="4. Cây Thư Mục Phân Cấp (Dendrogram Branching Tree)">🌿</button>
                <button class="dock-icon-btn" id="dockBtnHierarchical" onclick="switchLayoutMode('hierarchical')" title="5. Cây Phả Hệ Có Hướng (CiteSpace DAG)">🌳</button>
                <button class="dock-icon-btn" id="dockBtnMatrix" onclick="switchLayoutMode('matrix')" title="6. Ma Trận Cụm Chủ Đề (Clustered Topic Matrix)">▦</button>
                <button class="dock-icon-btn" id="dockBtnForce" onclick="switchLayoutMode('force')" title="7. Mạng Động Học Lượng Tử (Force-Directed Quantum)">🕸️</button>
                <button class="dock-icon-btn" id="dockBtnQuartile" onclick="switchLayoutMode('quartile')" title="8. Phân Làn Thứ Hạng Scopus (Quartile Lanes Q1-Q4)">📊</button>
                <button class="dock-icon-btn" id="dockBtnDiamond" onclick="switchLayoutMode('diamond')" title="9. Mặt Phẳng Kim Cương Đối Xứng (Dual-Diamond Horizon)">💎</button>
                <button class="dock-icon-btn" id="dockBtnFanChart" onclick="switchLayoutMode('fanchart')" title="10. Quạt Nan Phả Hệ Tỏa Tròn (Ancestry Fan Chart)">🪭</button>
            </div>
            
            <div class="dock-btn-group" style="margin-top:10px; border-top:1px solid rgba(var(--theme-glow-rgb),0.15); padding-top:8px;">
                <button class="dock-icon-btn active" id="dockBtnLayers" onclick="toggleLayerFilterPopover()" title="📑 Chọn Tầng & Lọc Kết Hợp (Checkbox)">📑</button>
                <button class="dock-icon-btn" id="dockBtnLegend" onclick="toggleLegendDrawer()" title="📖 Ghi chú, Thuật ngữ & Hướng dẫn 10 Layout & 10 Theme">📖</button>
                <button class="dock-icon-btn active" id="dockBtnTrace" onclick="toggleLineageMode()" title="🧬 Bật/Tắt Truy Vết Phả Hệ">🧬</button>
                <button class="dock-icon-btn" onclick="cycleThemes()" title="🎨 Chuyển đổi 10 Mẫu Theme Đa Sắc & Đơn Sắc">🎨</button>
                <button class="dock-icon-btn" onclick="openDedicatedViewport()" title="🌐 Mở Màn hình phụ (Cửa sổ mới ↗)">↗️</button>
                <button class="dock-icon-btn" onclick="fitView()" title="🎯 Căn giữa toàn cảnh">🎯</button>
            </div>

            <!-- SLIDE-OUT LEGEND DRAWER TỪ DOCK BÊN TRÁI -->
            <div id="dockLegendDrawer" class="dock-legend-drawer">
                <div class="drawer-header">
                    <span>📖 QUY ƯỚC, THUẬT NGỮ & 10 CHẾ ĐỘ XEM</span>
                    <button onclick="toggleLegendDrawer()" style="background:none; border:none; color:var(--theme-accent); font-size:14px; cursor:pointer; padding:2px 6px;">✕</button>
                </div>
                <!-- Ô TÌM KIẾM THÔNG MINH TRONG HƯỚNG DẪN -->
                <div style="padding: 8px 12px; background: rgba(0,0,0,0.3); border-bottom: 1px solid var(--theme-panel-border);">
                    <input type="text" id="guideSearchInput" placeholder="🔍 Tìm kiếm: Xương cá, Radar, F0, F1-F3, Mũi tên..." oninput="filterGuideDrawer(this.value)" style="width:100%; background:rgba(0,0,0,0.4); border:1px solid var(--theme-panel-border); color:#FFFFFF; border-radius:8px; padding:6px 10px; font-size:11px; outline:none;">
                </div>
                <div class="drawer-body" id="guideDrawerBody">
                    <div id="guideSearchEmpty" style="display:none; color:#F87171; font-size:11px; text-align:center; padding:12px;">Không tìm thấy thuật ngữ phù hợp!</div>

                    <div class="guide-searchable-item" style="font-weight:800; color:var(--theme-accent); margin-bottom:6px; text-transform:uppercase;">1. Cơ Chế Bảo Tồn Bài Báo Gốc F0 (Anchor Pinning) & Phân Tầng:</div>
                    <div class="legend-item-card guide-searchable-item">
                        <span class="legend-color-chip" style="background:#EA4335; box-shadow:0 0 8px #EA4335;"></span>
                        <div><b>🔴 F0 (Seed Paper - Tâm Điểm Nghiên Cứu):</b> Luôn luôn được ghim làm tâm điểm neo (Anchor Node) trong mọi chế độ lọc kết hợp (F0 + F1..F3, F0 + R1..R3), không bao giờ bị biến mất để duy trì mạch tri thức.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <span class="legend-color-chip" style="background:#7C3AED; box-shadow:0 0 6px #7C3AED;"></span>
                        <div><b>🟣 R1-R3 (Backward References - Cội nguồn lý thuyết):</b> Các công trình kinh điển quá khứ mà đề tài gốc kế thừa. Kích thước tỷ lệ thuận với số trích dẫn quốc tế (Price's Law).</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <span class="legend-color-chip" style="background:#0284C7; box-shadow:0 0 6px #0284C7;"></span>
                        <div><b>🟢 F1-F3 (Forward Citations - Bước tiến tương lai):</b> Các công trình phát triển tiếp nối sau bài gốc, kiểm chứng thực nghiệm hoặc mở rộng mô hình.</div>
                    </div>

                    <div class="guide-searchable-item" style="font-weight:800; color:var(--theme-accent); margin:12px 0 6px 0; text-transform:uppercase;">2. 10 Chế Độ Bố Cục Học Thuật (Layout Engines):</div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>1. ⏳ Linear Timeline:</b> Bố cục thời gian thẳng ngang (HistCite), các bài cùng năm tự động so le lệch trục để chống đè chồng.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>2. 📡 Radar Timeline:</b> Quỹ đạo radar đồng tâm, F0 tại tâm điểm, các vòng tròn tỏa rộng đại diện cho các năm/thế hệ.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>3. 🐟 Ishikawa Fishbone:</b> Sơ đồ xương cá học thuật, trục sống lưng là thời gian, cội nguồn R chéo xuống dưới, kế thừa F chéo lên trên.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>4. 🌿 Dendrogram:</b> Cây thư mục phân cấp tỏa nhánh từ bài gốc sang hai phía.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>5. 🌳 CiteSpace DAG:</b> Cây phả hệ có hướng phân tầng từ cội nguồn đến các phát triển mới.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>6. ▦ Clustered Matrix:</b> Ma trận lưới cụm chủ đề và phân hạng tạp chí.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>7. 🕸️ Force Quantum:</b> Mạng lưới động học lực đẩy-hút tự nhiên (VOSviewer).</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>8. 📊 Quartile Lanes:</b> Phân làn theo xếp hạng Scopus Q1, Q2, Q3/Q4.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>9. 💎 Dual-Diamond Horizon:</b> Mặt phẳng kim cương đối xứng 2 chiều.</div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <div><b>10. 🪭 Ancestry Fan Chart:</b> Quạt nan phả hệ tỏa tròn 180 độ.</div>
                    </div>

                    <div class="guide-searchable-item" style="font-weight:800; color:var(--theme-accent); margin:12px 0 6px 0; text-transform:uppercase;">3. Giải Mã 4 Loại Mũi Tên & Dòng Truyền Tri Thức:</div>
                    <div class="legend-item-card guide-searchable-item">
                        <span style="color:#38BDF8; font-weight:800; font-size:14px;">🔷</span>
                        <div>
                            <b>Xanh Sky (1 chiều nét liền): Kế thừa trực tiếp (Direct Citation)</b><br>
                            <i>Ý nghĩa:</i> Công trình sau trích dẫn và tiếp thu khung lý thuyết / mô hình của công trình trước.
                        </div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <span style="color:#F59E0B; font-weight:800; font-size:14px;">🔶</span>
                        <div>
                            <b>Vàng Kim (2 đầu mũi tên): Đối thoại học thuật 2 chiều (Reciprocal Debate)</b><br>
                            <i>Ý nghĩa:</i> Hai nhóm tác giả cùng trích dẫn chéo lẫn nhau, tạo thành trường phái tranh luận đối trọng.
                        </div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <span style="color:#C084FC; font-weight:800; font-size:14px;">🔮</span>
                        <div>
                            <b>Tím Neon (Đứt nét dài): Bắc cầu xuyên tầng cội nguồn (Cross-Bridge)</b><br>
                            <i>Ý nghĩa:</i> Công trình mới neo trực tiếp vào nền tảng kinh điển ban đầu mà không qua tầng trung gian.
                        </div>
                    </div>
                    <div class="legend-item-card guide-searchable-item">
                        <span style="color:#34D399; font-weight:800; font-size:14px;">🟢</span>
                        <div>
                            <b>Ngọc Lục (Chấm nhỏ): Đồng phát triển cùng phân tầng (Intra-Layer)</b><br>
                            <i>Ý nghĩa:</i> Các công trình trong cùng thế hệ nghiên cứu chia sẻ dữ liệu hoặc cùng bối cảnh thực chứng.
                        </div>
                    </div>

                    <div class="guide-searchable-item" style="font-weight:800; color:var(--theme-accent); margin:12px 0 6px 0; text-transform:uppercase;">4. 10 Mẫu Giao Diện / Themes:</div>
                    <div class="guide-searchable-item" style="color:var(--theme-text-dim); font-size:10.5px; line-height:1.55;">
                        • Bao gồm <b>Matrix Cyber Green</b> (chuẩn phim Ma Trận) và <b>Monochrome Classic Đen-Trắng</b> (độ tương phản tuyệt đối cho in ấn/trình chiếu), cùng 8 mẫu màu sắc tinh tế khác.<br>
                        • Toàn bộ khung giao diện áp dụng chuẩn đổ bóng đều xung quanh (Omnidirectional Box-Shadow) mang lại chiều sâu không gian Sci-Fi đồng nhất.
                    </div>
                </div>
            </div>
        </nav>

        <!-- GRAPH CANVAS -->
        <div class="synapse-graph-container" style="position:relative;">
            <div class="graph-overlay-header">
                <div class="graph-title">Global Citation Knowledge Network</div>
                <div class="graph-subtitle">Project: {short_project_name}</div>
            </div>

            <!-- SMART HUD HOVER INSPECTOR Ở VÙNG AN TOÀN TRÁI (CHO NODE - CÓ NÚT ĐÓNG) -->
            <div id="graphHoverInspector" class="hud-hover-inspector">
                <div class="hover-inspector-header">
                    <div style="display:flex; gap:6px; align-items:center;">
                        <span id="hoverChipType" class="meta-chip" style="font-size:9.5px; padding:1px 7px; border-color:var(--theme-accent);">★ BÀI BÁO</span>
                        <span id="hoverChipYear" class="meta-chip" style="font-size:9.5px; padding:1px 7px; color:#FDE047;">2024</span>
                    </div>
                    <button type="button" onclick="hideHoverInspector()" style="background:transparent; border:none; color:var(--theme-accent); font-size:12px; cursor:pointer; padding:0 3px; line-height:1;" title="Đóng bảng chi tiết">✕</button>
                </div>
                <div id="hoverInspectorTitle" class="hover-inspector-title">Paper Title</div>
                <div id="hoverInspectorMeta" class="hover-inspector-meta">Author • Journal • Citations</div>
                <div id="hoverInspectorLinks" class="hover-inspector-links">↳ Đang liên kết: 3 tham chiếu • 5 kế thừa</div>
                <div id="hoverInspectorAbstract" style="font-size:10px; color:#94A3B8; margin-top:4px; line-height:1.35; display:none;"></div>
            </div>

            <!-- EDGE EPISTEMIC INSPECTOR Ở VÙNG AN TOÀN TRÁI DƯỚI (CHO MŨI TÊN - CÓ NÚT ĐÓNG) -->
            <div id="graphEdgeInspector" class="edge-epistemic-inspector">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span id="edgeTypeBadge" class="edge-inspector-tag">⚡ DÒNG TRUYỀN TRI THỨC</span>
                    <button type="button" onclick="hideHoverInspector()" style="background:transparent; border:none; color:#FDE047; font-size:12px; cursor:pointer; padding:0 4px; line-height:1;" title="Đóng bảng giải thích liên kết">✕</button>
                </div>
                <div id="edgeEpistemicBody" style="margin-top:2px;">
                    <!-- Nội dung học thuật độc đáo -->
                </div>
            </div>

            <!-- TOP RIGHT MINI CONTROLS (TÌM KIẾM, LỌC TẦNG KẾT HỢP & BỐ CỤC) -->
            <div class="graph-top-tools">
                <input type="text" id="nodeSearchInput" placeholder="🔍 Tìm DOI, tác giả, năm..." oninput="searchAndFocusNode(this.value)" style="background:rgba(0,0,0,0.45); border:1px solid var(--theme-panel-border); color:#FFFFFF; border-radius:8px; padding:4px 9px; font-size:11px; outline:none; width:135px;" title="Tìm kiếm thông minh theo DOI, Tác giả viết tắt/đầy đủ, Năm (ví dụ: 2024, >2020), Tên bài báo, Từ khóa...">
                
                <!-- BỘ LỌC TẦNG BẰNG TÍNH NĂNG CHECKBOX LINH HOẠT & NHANH -->
                <button type="button" id="layerFilterToggleBtn" class="hud-mini-btn active" onclick="toggleLayerFilterPopover()" title="Chọn hiển thị từng tầng theo ý muốn bằng Checkbox (F0 / R1-R3 / F1-F3 / Độc lập)">📑 Chọn Tầng (Check) ▾</button>

                <!-- POPOVER CHỌN TẦNG CHECKBOX THÔNG MINH (2 CỘT GỌN GÀNG, NGĂN NẮP) -->
                <div id="layerFilterPopover" onclick="event.stopPropagation();" style="display:none; position:absolute; top:46px; right:8px; z-index:99999; background:rgba(15, 23, 42, 0.98); border:1.5px solid var(--theme-accent); border-radius:12px; padding:9px 12px; box-shadow:0 12px 36px rgba(0,0,0,0.8), 0 0 15px rgba(var(--theme-glow-rgb),0.25); width:320px; max-width:92vw; backdrop-filter:blur(16px); text-align:left;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:4px;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="font-size:11px; font-weight:800; color:var(--theme-accent); text-transform:uppercase;">📑 Lọc Phân Tầng</span>
                            <span id="layerFilterCountBadge" style="font-size:9.5px; background:rgba(56,189,248,0.2); color:#38BDF8; padding:1px 5px; border-radius:4px; font-weight:700;">{len(vis_nodes)}/{len(vis_nodes)} bài</span>
                        </div>
                        <button type="button" onclick="toggleLayerFilterPopover()" style="background:transparent; border:none; color:var(--theme-text-dim); font-size:13px; cursor:pointer; padding:0 3px; line-height:1;" title="Đóng menu">✕</button>
                    </div>
                    
                    <!-- Quick Preset Buttons (1 hàng 4 nút cân đối) -->
                    <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:3px; margin-bottom:6px;">
                        <button type="button" class="hud-mini-btn active" style="font-size:9px; padding:2px 2px; text-align:center; white-space:nowrap;" onclick="setLayerPreset('all')">✓ Tất cả</button>
                        <button type="button" class="hud-mini-btn" style="font-size:9px; padding:2px 2px; text-align:center; white-space:nowrap;" onclick="setLayerPreset('f0_forward')">🚀 Kế thừa</button>
                        <button type="button" class="hud-mini-btn" style="font-size:9px; padding:2px 2px; text-align:center; white-space:nowrap;" onclick="setLayerPreset('f0_backward')">🏛️ Cội nguồn</button>
                        <button type="button" class="hud-mini-btn" style="font-size:9px; padding:2px 2px; text-align:center; white-space:nowrap;" onclick="setLayerPreset('f0_only')">★ Chỉ F0</button>
                    </div>

                    <!-- Ghim bài gốc F0 -->
                    <label style="display:flex; align-items:center; gap:6px; background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:6px; padding:3px 7px; margin-bottom:6px; color:#F8FAFC; cursor:pointer; font-size:10px; font-weight:700;">
                        <input type="checkbox" id="chk_pin_f0" checked onchange="applyGraphFilters()" style="accent-color:var(--theme-accent); cursor:pointer;">
                        <span>🔒 Ghim bài gốc F0 (Anchor Pinning)</span>
                    </label>

                    <!-- 2 Cột Đối Xứng: Chiều Kế Thừa & Chiều Cội Nguồn -->
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px;">
                        <!-- Cột Trái: Kế Thừa -->
                        <div style="display:flex; flex-direction:column; gap:3px; background:rgba(0,0,0,0.3); padding:5px; border-radius:6px; border:1px solid rgba(56,189,248,0.15);">
                            <div style="font-size:8.5px; font-weight:800; color:#38BDF8; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px; border-bottom:1px solid rgba(56,189,248,0.2); padding-bottom:2px;">🚀 Chiều Kế Thừa</div>
                            
                            <label style="display:flex; align-items:center; gap:4px; color:#FDE047; cursor:pointer; font-size:9.5px; padding:1px 3px; border-radius:4px;">
                                <input type="checkbox" id="chk_layer_f0" checked onchange="applyGraphFilters()" style="accent-color:#FDE047; cursor:pointer;">
                                <span>★ F0: Bài gốc</span>
                            </label>
                            <label style="display:flex; align-items:center; gap:4px; color:#38BDF8; cursor:pointer; font-size:9.5px; padding:1px 3px; border-radius:4px;">
                                <input type="checkbox" id="chk_layer_f1" checked onchange="applyGraphFilters()" style="accent-color:#38BDF8; cursor:pointer;">
                                <span>🚀 F1: Trực tiếp</span>
                            </label>
                            <label style="display:flex; align-items:center; gap:4px; color:#60A5FA; cursor:pointer; font-size:9.5px; padding:1px 3px; border-radius:4px;">
                                <input type="checkbox" id="chk_layer_f2" checked onchange="applyGraphFilters()" style="accent-color:#60A5FA; cursor:pointer;">
                                <span>🚀 F2: Thế hệ 2</span>
                            </label>
                            <label style="display:flex; align-items:center; gap:4px; color:#93C5FD; cursor:pointer; font-size:9.5px; padding:1px 3px; border-radius:4px;">
                                <input type="checkbox" id="chk_layer_f3" checked onchange="applyGraphFilters()" style="accent-color:#93C5FD; cursor:pointer;">
                                <span>🚀 F3: Mở rộng</span>
                            </label>
                        </div>

                        <!-- Cột Phải: Cội Nguồn & Khác -->
                        <div style="display:flex; flex-direction:column; gap:3px; background:rgba(0,0,0,0.3); padding:5px; border-radius:6px; border:1px solid rgba(192,132,252,0.15);">
                            <div style="font-size:8.5px; font-weight:800; color:#C084FC; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px; border-bottom:1px solid rgba(192,132,252,0.2); padding-bottom:2px;">🏛️ Chiều Cội Nguồn</div>
                            
                            <label style="display:flex; align-items:center; gap:4px; color:#A78BFA; cursor:pointer; font-size:9.5px; padding:1px 3px; border-radius:4px;">
                                <input type="checkbox" id="chk_layer_r1" checked onchange="applyGraphFilters()" style="accent-color:#A78BFA; cursor:pointer;">
                                <span>🏛️ R1: Nền tảng 1</span>
                            </label>
                            <label style="display:flex; align-items:center; gap:4px; color:#C084FC; cursor:pointer; font-size:9.5px; padding:1px 3px; border-radius:4px;">
                                <input type="checkbox" id="chk_layer_r2" checked onchange="applyGraphFilters()" style="accent-color:#C084FC; cursor:pointer;">
                                <span>🏛️ R2: Cội nguồn 2</span>
                            </label>
                            <label style="display:flex; align-items:center; gap:4px; color:#E879F9; cursor:pointer; font-size:9.5px; padding:1px 3px; border-radius:4px;">
                                <input type="checkbox" id="chk_layer_r3" checked onchange="applyGraphFilters()" style="accent-color:#E879F9; cursor:pointer;">
                                <span>🏛️ R3: Kinh điển 3</span>
                            </label>
                            <label style="display:flex; align-items:center; gap:4px; color:#94A3B8; cursor:pointer; font-size:9.5px; padding:1px 3px; border-radius:4px;">
                                <input type="checkbox" id="chk_layer_isolated" checked onchange="applyGraphFilters()" style="accent-color:#94A3B8; cursor:pointer;">
                                <span>⚡ Bài độc lập</span>
                            </label>
                        </div>
                    </div>
                </div>

                <!-- BỘ LỌC MŨI TÊN KẾT NỐI -->
                <select id="edgeFilter" onchange="applyGraphFilters()" style="background:var(--theme-panel-bg); border:1px solid var(--theme-panel-border); color:var(--theme-text-main); border-radius:8px; padding:4px 6px; font-size:11px; font-weight:600; outline:none; cursor:pointer;" title="Lọc loại liên kết mũi tên">
                    <option value="all">⚡ Tất cả mũi tên</option>
                    <option value="direct">🔷 Kế thừa 1 chiều</option>
                    <option value="mutual">🔶 Đối thoại 2 chiều</option>
                    <option value="cross_bridge">🔮 Bắc cầu xuyên tầng</option>
                    <option value="intra_layer">🟢 Cùng phân tầng</option>
                </select>

                <!-- BỘ CHỌN 10 BỐ CỤC HỌC THUẬT -->
                <select id="layoutSelector" onchange="switchLayoutMode(this.value)" style="background:var(--theme-panel-bg); border:1px solid var(--theme-panel-border); color:var(--theme-accent); border-radius:8px; padding:4px 6px; font-size:11px; font-weight:700; outline:none; cursor:pointer;" title="Chọn 1 trong 10 Chế độ Bố Cục Học Thuật">
                    <option value="timeline">1. ⏳ Linear Timeline (HistCite)</option>
                    <option value="radar">2. 📡 Concentric Radar Timeline</option>
                    <option value="fishbone">3. 🐟 Ishikawa Fishbone Diagram</option>
                    <option value="dendrogram">4. 🌿 Dendrogram Branching Tree</option>
                    <option value="hierarchical">5. 🌳 CiteSpace DAG Tree</option>
                    <option value="matrix">6. ▦ Clustered Topic Matrix</option>
                    <option value="force">7. 🕸️ Force-Directed Quantum</option>
                    <option value="quartile">8. 📊 Scopus Quartile Lanes</option>
                    <option value="diamond">9. 💎 Dual-Diamond Horizon</option>
                    <option value="fanchart">10. 🪭 Ancestry Fan Chart</option>
                </select>

                <!-- THANH TRƯỢT ĐIỀU TỐC PHOTON & TIA SÁNG HOVER -->
                <div class="speed-control-cluster" title="Điều chỉnh tốc độ di chuyển hạt Photon & Tia sáng kết nối (0x: Đứng yên -> 3x: Nhanh tối đa)">
                    <span style="font-size:10.5px; font-weight:700; color:var(--theme-accent);">⚡ Tốc độ:</span>
                    <input type="range" id="photonSpeedSlider" class="speed-slider-input" min="0" max="3" step="0.2" value="1.0" oninput="setPhotonSpeed(this.value)">
                    <span id="photonSpeedVal" style="font-size:10.5px; font-family:'JetBrains Mono', monospace; font-weight:700; color:#FDE047; min-width:24px;">1.0x</span>
                </div>

                <button class="hud-mini-btn active" id="labelModeBtn" onclick="cycleLabelMode()" title="Chuyển chế độ nhãn (Gọn / Đầy Đủ / Ẩn)">🏷️ Nhãn: Gọn</button>
                <button class="hud-mini-btn active" id="laserBtn" onclick="toggleLaserBeam()" title="Bật/Tắt Tia Laser Neon & Đường kết nối khi chọn/hover">⚡ Tia Laser</button>
                <button class="hud-mini-btn active" id="particlesBtn" onclick="toggleParticles()" title="Bật/Tắt Dòng Hạt Photon di chuyển">✨ Hạt Photon</button>
                <button class="hud-mini-btn active" id="pulseBtn" onclick="togglePulseGlow()" title="Bật/Tắt Hào Quang Nhịp Thở Node">💓 Nhịp Thở</button>
                <button class="hud-mini-btn active" id="lineageBtn" onclick="toggleLineageMode()" title="Bật/Tắt Chế độ Truy Vết Phả Hệ">🧬 Truy Vết</button>
                <button class="hud-mini-btn" id="timeplayBtn" onclick="toggleTimelinePlayback()" title="Tua Lịch Sử Phát Triển Theo Năm">⏯️ Tua Năm</button>
                <button class="hud-mini-btn" onclick="zoomIn()" title="Phóng to">🔍+</button>
                <button class="hud-mini-btn" onclick="zoomOut()" title="Thu nhỏ">🔍-</button>
                <button class="hud-mini-btn" onclick="openDedicatedViewport()" title="Mở Màn hình phụ độc lập (Cửa sổ mới ↗)">🌐 Cửa Sổ Mới ↗</button>
                <button class="hud-mini-btn" onclick="toggleFullScreen()" title="Toàn màn hình">⛶</button>
            </div>

            <!-- TIMELINE PLAYBACK BAR (NỔI KHI BẬT) -->
            <div id="timelinePlaybackBar" style="display:none; position:absolute; bottom:14px; right:16px; z-index:70; background:var(--theme-panel-bg); border:1.5px solid var(--theme-accent); border-radius:12px; padding:6px 12px; align-items:center; gap:8px; box-shadow:0 0 20px rgba(var(--theme-glow-rgb), 0.35);">
                <button id="playbackPlayBtn" class="hud-mini-btn active" onclick="togglePlaybackPlay()">▶️ Phát</button>
                <span style="font-size:11px; font-weight:700;">NĂM: <b id="playbackYearLabel" style="color:#FDE047;">{max_yr}</b></span>
                <input type="range" id="playbackYearSlider" min="{min_yr}" max="{max_yr}" value="{max_yr}" step="1" oninput="onPlaybackSliderChange(this.value)" style="cursor:pointer; accent-color:var(--theme-accent); width:110px;">
                <button class="hud-mini-btn" onclick="resetPlayback()">↺</button>
            </div>

            <div id="network-container"></div>
        </div>
    </div>

    <!-- 3. BOTTOM EXPANDABLE PANELS DECK -->
    <div class="synapse-bottom-deck">
        <!-- PANEL 1: RELATED PAPERS MATRIX -->
        <div class="hud-panel-card">
            <div class="panel-card-header">
                <span>📑 Related Papers Matrix ({len(vis_nodes)} works)</span>
                <span style="font-size:10.5px; color:var(--theme-text-dim); text-transform:none;">Bấm dòng để focus ↗</span>
            </div>
            <div class="panel-card-body" id="relatedPapersTableContainer">
                <table class="related-table">
                    <thead>
                        <tr>
                            <th>Author & Work</th>
                            <th>Year</th>
                            <th>Journal / Venue</th>
                            <th>Cites</th>
                            <th>AI Relevance</th>
                        </tr>
                    </thead>
                    <tbody id="relatedPapersTbody">
                        <!-- Rendered by JS -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- PANEL 2: SELECTED PAPER DETAILS & CO-CITATION -->
        <div class="hud-panel-card">
            <div class="panel-card-header">
                <span>📄 Selected Paper Details & Co-Citation Path</span>
                <div id="selectedPaperActionBtns" style="display:flex; gap:6px;">
                    <!-- Action Links Rendered by JS -->
                </div>
            </div>
            <div class="panel-card-body">
                <div class="details-grid">
                    <!-- LEFT PANE: TITLE & ABSTRACT -->
                    <div class="detail-abstract-pane">
                        <div id="selTitle" style="font-size:12.5px; font-weight:700; color:#FFFFFF; line-height:1.4;">Vui lòng chọn 1 bài báo trên đồ thị hoặc bảng bên trái</div>
                        <div id="selMeta" style="font-size:11px; color:var(--theme-text-dim);"></div>
                        <div id="selAbstract" style="font-size:11px; color:var(--theme-text-main); line-height:1.55; max-height:85px; overflow-y:auto; background:rgba(0,0,0,0.2); padding:6px 8px; border-radius:6px; border:1px solid rgba(255,255,255,0.05);"></div>
                    </div>

                    <!-- RIGHT PANE: CO-CITATION PATH & LINEAGE -->
                    <div class="detail-cocitation-pane">
                        <div style="font-size:10.5px; font-weight:800; color:var(--theme-accent); text-transform:uppercase; letter-spacing:0.04em;">🧬 AI Co-Citation Path:</div>
                        <div id="selLineageList" style="display:flex; flex-direction:column; gap:4px; overflow-y:auto; max-height:110px;">
                            <div style="color:var(--theme-text-dim); font-size:10.5px; font-style:italic;">Chưa chọn bài báo.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
    var rawNodes = {nodes_json};
    var rawEdges = {edges_json};
    var metaDict = {meta_dict_json};
    var minYrVal = {min_yr};
    var maxYrVal = {max_yr};

    var nodes = new vis.DataSet(rawNodes);
    var edges = new vis.DataSet(rawEdges);

    var nodeView = new vis.DataView(nodes, {{
        filter: function (item) {{
            return item.hidden !== true;
        }}
    }});
    var edgeView = new vis.DataView(edges, {{
        filter: function (item) {{
            return item.hidden !== true;
        }}
    }});

    var container = document.getElementById('network-container');
    var data = {{ nodes: nodeView, edges: edgeView }};

    var isPhysicsOn = true;
    var isParticlesOn = true;
    var isLaserBeamOn = true;
    var isPulsingOn = true;
    var isLineageTracingOn = false;
    var isTimelinePlaybackActive = false;
    var isPlaybackPlaying = false;
    var playbackTimer = null;
    var playbackIntervalMs = 1200;
    var currentPlaybackYear = maxYrVal;
    var selectedLineageNodeId = null;
    var currentLayoutMode = 'timeline';
    var currentLabelMode = 'short';
    var currentThemeIndex = 0;
    
    // 10 THEMES DANH SÁCH TOÀN DIỆN
    var themesList = [
        'theme-synapse-cyan',
        'theme-emerald-matrix',
        'theme-monochrome-classic',
        'theme-nebula-violet',
        'theme-solar-amber',
        'theme-deep-ocean',
        'theme-crimson-ruby',
        'theme-nordic-frost',
        'theme-vintage-parchment',
        'theme-neon-gold'
    ];

    // BẢNG MÀU NODE & MŨI TÊN TƯƠNG PHẢN CAO CHO 10 THEMES
    var themePalettes = {{
        'theme-synapse-cyan': {{
            node_f0: {{ background: '#EA4335', border: '#FF8A80', highlight: '#FFEBEE' }},
            node_r: {{ background: '#7C3AED', border: '#A78BFA', highlight: '#EDE9FE' }},
            node_f: {{ background: '#0284C7', border: '#38BDF8', highlight: '#E0F2FE' }},
            edge_direct: 'rgba(56, 189, 248, 0.75)',
            edge_mutual: 'rgba(245, 158, 11, 0.88)',
            edge_cross: 'rgba(192, 132, 252, 0.90)',
            edge_intra: 'rgba(52, 211, 153, 0.82)',
            font_color: '#F8FAFC'
        }},
        'theme-emerald-matrix': {{
            node_f0: {{ background: '#00FF66', border: '#FFFFFF', highlight: '#E6FFE6' }},
            node_r: {{ background: '#008833', border: '#00FF66', highlight: '#CCFFCC' }},
            node_f: {{ background: '#00CC55', border: '#88FFAA', highlight: '#DDFFEE' }},
            edge_direct: 'rgba(0, 255, 102, 0.78)',
            edge_mutual: 'rgba(255, 204, 0, 0.90)',
            edge_cross: 'rgba(0, 220, 255, 0.90)',
            edge_intra: 'rgba(100, 255, 150, 0.82)',
            font_color: '#E6FFE6'
        }},
        'theme-monochrome-classic': {{
            node_f0: {{ background: '#FFFFFF', border: '#000000', highlight: '#F4F4F5' }},
            node_r: {{ background: '#52525B', border: '#D4D4D8', highlight: '#E4E4E7' }},
            node_f: {{ background: '#A1A1AA', border: '#FFFFFF', highlight: '#F4F4F5' }},
            edge_direct: 'rgba(255, 255, 255, 0.75)',
            edge_mutual: 'rgba(212, 212, 216, 0.90)',
            edge_cross: 'rgba(161, 161, 170, 0.88)',
            edge_intra: 'rgba(113, 113, 122, 0.80)',
            font_color: '#FFFFFF'
        }},
        'theme-nebula-violet': {{
            node_f0: {{ background: '#F43F5E', border: '#FDA4AF', highlight: '#FFF1F2' }},
            node_r: {{ background: '#7C3AED', border: '#C084FC', highlight: '#FAF5FF' }},
            node_f: {{ background: '#A855F7', border: '#E879F9', highlight: '#FDF4FF' }},
            edge_direct: 'rgba(192, 132, 252, 0.78)',
            edge_mutual: 'rgba(245, 158, 11, 0.90)',
            edge_cross: 'rgba(244, 63, 94, 0.90)',
            edge_intra: 'rgba(168, 85, 247, 0.82)',
            font_color: '#FAF5FF'
        }},
        'theme-solar-amber': {{
            node_f0: {{ background: '#DC2626', border: '#FCA5A5', highlight: '#FEF2F2' }},
            node_r: {{ background: '#B45309', border: '#FBBF24', highlight: '#FFFBEB' }},
            node_f: {{ background: '#D97706', border: '#FDE68A', highlight: '#FEF3C7' }},
            edge_direct: 'rgba(245, 158, 11, 0.78)',
            edge_mutual: 'rgba(239, 68, 68, 0.90)',
            edge_cross: 'rgba(168, 85, 247, 0.90)',
            edge_intra: 'rgba(251, 191, 36, 0.82)',
            font_color: '#FFFBEB'
        }},
        'theme-deep-ocean': {{
            node_f0: {{ background: '#E11D48', border: '#FDA4AF', highlight: '#FFF1F2' }},
            node_r: {{ background: '#1D4ED8', border: '#60A5FA', highlight: '#EFF6FF' }},
            node_f: {{ background: '#0284C7', border: '#38BDF8', highlight: '#F0F9FF' }},
            edge_direct: 'rgba(56, 189, 248, 0.78)',
            edge_mutual: 'rgba(245, 158, 11, 0.90)',
            edge_cross: 'rgba(129, 140, 248, 0.90)',
            edge_intra: 'rgba(45, 212, 191, 0.82)',
            font_color: '#F0F9FF'
        }},
        'theme-crimson-ruby': {{
            node_f0: {{ background: '#E11D48', border: '#FFE4E6', highlight: '#FFF1F2' }},
            node_r: {{ background: '#9F1239', border: '#FB7185', highlight: '#FFE4E6' }},
            node_f: {{ background: '#BE123C', border: '#FDA4AF', highlight: '#FFF1F2' }},
            edge_direct: 'rgba(244, 63, 94, 0.78)',
            edge_mutual: 'rgba(251, 191, 36, 0.90)',
            edge_cross: 'rgba(192, 132, 252, 0.90)',
            edge_intra: 'rgba(251, 113, 133, 0.82)',
            font_color: '#FFF1F2'
        }},
        'theme-nordic-frost': {{
            node_f0: {{ background: '#DC2626', border: '#991B1B', highlight: '#FEE2E2' }},
            node_r: {{ background: '#0369A1', border: '#075985', highlight: '#E0F2FE' }},
            node_f: {{ background: '#0D9488', border: '#115E59', highlight: '#CCFBF1' }},
            edge_direct: 'rgba(2, 132, 199, 0.75)',
            edge_mutual: 'rgba(217, 119, 6, 0.90)',
            edge_cross: 'rgba(124, 58, 237, 0.88)',
            edge_intra: 'rgba(13, 148, 136, 0.80)',
            font_color: '#0F172A'
        }},
        'theme-vintage-parchment': {{
            node_f0: {{ background: '#991B1B', border: '#7F1D1D', highlight: '#FEF2F2' }},
            node_r: {{ background: '#78350F', border: '#451A03', highlight: '#FEF3C7' }},
            node_f: {{ background: '#065F46', border: '#064E3B', highlight: '#ECFDF5' }},
            edge_direct: 'rgba(180, 83, 9, 0.75)',
            edge_mutual: 'rgba(185, 28, 28, 0.90)',
            edge_cross: 'rgba(109, 40, 217, 0.88)',
            edge_intra: 'rgba(4, 120, 87, 0.80)',
            font_color: '#292524'
        }},
        'theme-neon-gold': {{
            node_f0: {{ background: '#EF4444', border: '#FCA5A5', highlight: '#FEF2F2' }},
            node_r: {{ background: '#CA8A04', border: '#FDE047', highlight: '#FEF9C3' }},
            node_f: {{ background: '#EAB308', border: '#FEF08A', highlight: '#FEFCE8' }},
            edge_direct: 'rgba(234, 179, 8, 0.78)',
            edge_mutual: 'rgba(249, 115, 22, 0.90)',
            edge_cross: 'rgba(168, 85, 247, 0.90)',
            edge_intra: 'rgba(250, 204, 21, 0.82)',
            font_color: '#FEFCE8'
        }}
    }};

    var forceOptions = {{
        nodes: {{
            shadow: {{
                enabled: true,
                color: 'rgba(0,0,0,0.5)',
                size: 10,
                x: 0,
                y: 0
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

    // Realtime Clock
    function updateClock() {{
        var d = new Date();
        var clockEl = document.getElementById('realtimeClock');
        if (clockEl) {{
            clockEl.innerText = d.toLocaleDateString('en-GB') + ' | ' + d.toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit', second:'2-digit'}});
        }}
    }}
    setInterval(updateClock, 1000);
    updateClock();

    // Populate Related Papers Table
    function renderRelatedPapersTable() {{
        var tbody = document.getElementById('relatedPapersTbody');
        if (!tbody) return;
        var html = '';
        var maxCites = 1;
        rawNodes.forEach(function(n) {{ if ((n.citations || 0) > maxCites) maxCites = n.citations; }});

        rawNodes.forEach(function(n, idx) {{
            var p = metaDict[n.id] || {{}};
            var relPct = Math.min(99, Math.max(30, Math.round(35 + Math.log((n.citations || 1) + 1) / Math.log(maxCites + 2) * 60)));
            if (p.level === 0 || p.layer === 'seed') relPct = 99;
            
            var cleanT = (p.title || '').replace(/"/g, '');
            var shortT = cleanT.length > 32 ? cleanT.substring(0, 32) + '...' : cleanT;
            var shortV = (p.venue || 'Journal').length > 20 ? (p.venue || 'Journal').substring(0, 20) + '...' : (p.venue || 'Journal');

            html += '<tr class="related-row" id="rel_row_' + n.id + '" onclick="selectPaperFromTable(\\'' + n.id + '\\')">' +
                '<td><b>' + p.first_author + '</b>: <span style="color:var(--theme-text-dim);">' + shortT + '</span></td>' +
                '<td style="color:#FDE047;">' + p.year + '</td>' +
                '<td style="color:var(--theme-accent);">' + shortV + '</td>' +
                '<td><b>' + (p.citation_count || 0) + '</b></td>' +
                '<td>' +
                    '<div class="relevance-bar-track"><div class="relevance-bar-fill" style="width:' + relPct + '%;"></div></div>' +
                    '<span style="font-family:JetBrains Mono, monospace; font-size:10px; color:var(--theme-accent);">' + relPct + '%</span>' +
                '</td>' +
            '</tr>';
        }});
        tbody.innerHTML = html;
    }}
    renderRelatedPapersTable();

    // Select Paper from Table or Canvas
    function selectPaperFromTable(nodeId) {{
        var allRows = document.querySelectorAll('.related-row');
        allRows.forEach(function(r) {{ r.classList.remove('selected'); }});
        var activeRow = document.getElementById('rel_row_' + nodeId);
        if (activeRow) {{
            activeRow.classList.add('selected');
            activeRow.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
        }}

        network.selectNodes([nodeId]);
        network.focus(nodeId, {{
            scale: 1.35,
            animation: {{ duration: 350, easingFunction: 'easeInOutQuad' }}
        }});

        updateSelectedDetailsPane(nodeId);

        if (isLineageTracingOn) {{
            traceAncestryAndDescendants(nodeId);
        }}
    }}

    function updateSelectedDetailsPane(nodeId) {{
        var p = metaDict[nodeId];
        if (!p) return;

        var tEl = document.getElementById('selTitle');
        var mEl = document.getElementById('selMeta');
        var aEl = document.getElementById('selAbstract');
        var bEl = document.getElementById('selectedPaperActionBtns');
        var lEl = document.getElementById('selLineageList');

        if (tEl) tEl.innerText = p.title;
        if (mEl) mEl.innerHTML = '<b>✍️ ' + p.authors + '</b> (' + p.year + ') • 🏛️ ' + p.venue + ' • <span style="color:var(--theme-accent); font-weight:700;">' + (p.scopus_tier || 'Scopus Q1') + ' (' + (p.citation_count || 0) + ' tc)</span>';
        if (aEl) aEl.innerText = p.abstract_vi || p.abstract || 'Tóm tắt đang cập nhật...';

        if (bEl) {{
            var btnHtml = '';
            if (p.doi_url || p.landing_url) {{
                btnHtml += '<a href="' + (p.doi_url || p.landing_url) + '" target="_blank" class="hud-mini-btn active" style="text-decoration:none; padding:3px 8px; font-size:10.5px;">DOI ↗</a>';
            }}
            if (p.pdf_url) {{
                btnHtml += '<a href="' + p.pdf_url + '" target="_blank" class="hud-mini-btn" style="background:#059669; border-color:#10B981; color:#FFF; text-decoration:none; padding:3px 8px; font-size:10.5px;">🔓 PDF ↗</a>';
            }}
            btnHtml += '<a href="' + (p.openalex_url || ('https://openalex.org/works?filter=doi:' + p.doi)) + '" target="_blank" class="hud-mini-btn" style="text-decoration:none; padding:3px 8px; font-size:10.5px;">OpenAlex ↗</a>';
            bEl.innerHTML = btnHtml;
        }}

        if (lEl) {{
            var outList = p.outgoing_ids || [];
            var inList = p.incoming_ids || [];
            var listHtml = '';
            
            if (outList.length > 0) {{
                outList.slice(0, 3).forEach(function(tid) {{
                    var tp = metaDict[tid];
                    if (tp) listHtml += '<div class="cocite-item" onclick="selectPaperFromTable(\\'' + tid + '\\')">↳ <b>R (Tham chiếu):</b> ' + tp.first_author + ' (' + tp.year + ')</div>';
                }});
            }}
            if (inList.length > 0) {{
                inList.slice(0, 3).forEach(function(sid) {{
                    var sp = metaDict[sid];
                    if (sp) listHtml += '<div class="cocite-item" onclick="selectPaperFromTable(\\'' + sid + '\\')">↰ <b>F (Kế thừa):</b> ' + sp.first_author + ' (' + sp.year + ')</div>';
                }});
            }}
            if (!listHtml) listHtml = '<div style="color:var(--theme-text-dim); font-size:10.5px;">Không có nhánh trích dẫn trực tiếp trong tập mẫu này.</div>';
            lEl.innerHTML = listHtml;
        }}
    }}

    // Cycle & Apply 10 Themes with Dynamic Contrast Palettes
    function cycleThemes() {{
        currentThemeIndex = (currentThemeIndex + 1) % themesList.length;
        var nextTheme = themesList[currentThemeIndex];
        changeThemeDirectly(nextTheme);
    }}

    function changeThemeDirectly(themeName) {{
        document.body.className = themeName;
        var selector = document.getElementById('themeSelector');
        if (selector) selector.value = themeName;
        currentThemeIndex = themesList.indexOf(themeName);
        applyThemePalette(themeName);
    }}

    function applyThemePalette(themeName) {{
        var pal = themePalettes[themeName] || themePalettes['theme-synapse-cyan'];
        
        var nodeUpdates = [];
        rawNodes.forEach(function(n) {{
            var isSeed = (n.level === 0 || n.layer === 'seed');
            var isBack = (n.level < 0 || n.layer === 'backward');
            var cObj = isSeed ? pal.node_f0 : (isBack ? pal.node_r : pal.node_f);
            nodeUpdates.push({{
                id: n.id,
                color: cObj,
                font: {{
                    size: isSeed ? 12 : 11,
                    color: pal.font_color,
                    face: 'Plus Jakarta Sans, sans-serif',
                    strokeWidth: 3.2,
                    strokeColor: (themeName === 'theme-nordic-frost' || themeName === 'theme-vintage-parchment') ? '#FFFFFF' : '#0B0C0E'
                }}
            }});
        }});
        nodes.update(nodeUpdates);

        var edgeUpdates = [];
        rawEdges.forEach(function(e) {{
            var eColor = pal.edge_direct;
            if (e.edge_type === 'mutual') eColor = pal.edge_mutual;
            else if (e.edge_type === 'cross_bridge') eColor = pal.edge_cross;
            else if (e.edge_type === 'intra_layer') eColor = pal.edge_intra;

            edgeUpdates.push({{
                id: e.id,
                color: {{ color: eColor, highlight: eColor, hover: eColor }}
            }});
        }});
        edges.update(edgeUpdates);
    }}

    // Network Click & Touch Tap Event (Hỗ trợ cảm ứng hoàn hảo trên Mobile & Tablet)
    network.on('click', function(params) {{
        if (params.nodes.length > 0) {{
            var nodeId = params.nodes[0];
            hoveredNodeId = nodeId;
            hoveredEdgeId = null;
            updateHoverInspectorNode(nodeId);
            selectPaperFromTable(nodeId);
        }} else if (params.edges.length > 0) {{
            var edgeId = params.edges[0];
            hoveredEdgeId = edgeId;
            hoveredNodeId = null;
            updateHoverInspectorEdge(edgeId);
        }} else {{
            hoveredNodeId = null;
            hoveredEdgeId = null;
            hideHoverInspector();
            if (isLineageTracingOn) {{
                resetLineageHighlight();
            }}
        }}
    }});

    // Switch Label Mode
    function cycleLabelMode() {{
        var btn = document.getElementById('labelModeBtn');
        if (currentLabelMode === 'short') {{
            currentLabelMode = 'full';
            if (btn) btn.innerHTML = '🏷️ Nhãn: Đầy Đủ';
        }} else if (currentLabelMode === 'full') {{
            currentLabelMode = 'minimal';
            if (btn) btn.innerHTML = '🏷️ Nhãn: Ẩn';
        }} else {{
            currentLabelMode = 'short';
            if (btn) btn.innerHTML = '🏷️ Nhãn: Gọn';
        }}

        var updates = [];
        rawNodes.forEach(function(n) {{
            var lbl = n.label_short;
            if (currentLabelMode === 'full') lbl = n.label_full;
            else if (currentLabelMode === 'minimal') lbl = '';
            updates.push({{ id: n.id, label: lbl }});
        }});
        nodes.update(updates);
    }}

    // Zoom & View Controls
    function zoomIn() {{
        network.moveTo({{ scale: network.getScale() * 1.35, animation: {{ duration: 250, easingFunction: 'easeInOutQuad' }} }});
    }}
    function zoomOut() {{
        network.moveTo({{ scale: network.getScale() / 1.35, animation: {{ duration: 250, easingFunction: 'easeInOutQuad' }} }});
    }}
    function fitView() {{
        network.fit({{ animation: {{ duration: 450, easingFunction: 'easeInOutQuad' }} }});
    }}
    function toggleFullScreen() {{
        var elem = document.getElementById('synapse-hud-deck') || document.documentElement;
        if (!document.fullscreenElement && !document.webkitFullscreenElement) {{
            if (elem.requestFullscreen) elem.requestFullscreen();
            else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
        }} else {{
            if (document.exitFullscreen) document.exitFullscreen();
            else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
        }}
        setTimeout(fitView, 350);
    }}

    // Open Standalone Dedicated Viewport in New Tab/Window
    function openDedicatedViewport() {{
        try {{
            var rawHtml = document.documentElement.outerHTML;
            var customHtml = rawHtml.replace(/height:\\s*860px/g, 'height: 100vh !important')
                                    .replace(/min-height:\\s*860px/g, 'min-height: 100vh !important')
                                    .replace(/display:\\s*grid/g, 'display: none !important');
            var blob = new Blob([customHtml], {{ type: 'text/html;charset=utf-8' }});
            var blobUrl = URL.createObjectURL(blob);
            var win = window.open(blobUrl, '_blank');
            if (!win || win.closed || typeof win.closed === 'undefined') {{
                var fallbackWin = window.open('', '_blank');
                if (fallbackWin) {{
                    fallbackWin.document.open();
                    fallbackWin.document.write(customHtml);
                    fallbackWin.document.close();
                }} else {{
                    alert('Vui lòng cho phép Pop-up trên trình duyệt để mở Màn hình phụ Synapse Academic!');
                }}
            }}
        }} catch(e) {{
            console.error('Open viewport error:', e);
        }}
    }}

    // Toggle Particle Photons & Pulsing Glow & Laser Beam Stream
    function toggleParticles() {{
        isParticlesOn = !isParticlesOn;
        var btn = document.getElementById('particlesBtn');
        if (btn) btn.className = isParticlesOn ? 'hud-mini-btn active' : 'hud-mini-btn';
        network.redraw();
    }}
    function toggleLaserBeam() {{
        isLaserBeamOn = !isLaserBeamOn;
        var btn = document.getElementById('laserBtn');
        if (btn) btn.className = isLaserBeamOn ? 'hud-mini-btn active' : 'hud-mini-btn';
        network.redraw();
    }}
    function togglePulseGlow() {{
        isPulsingOn = !isPulsingOn;
        var btn = document.getElementById('pulseBtn');
        if (btn) btn.className = isPulsingOn ? 'hud-mini-btn active' : 'hud-mini-btn';
        network.redraw();
    }}

    // Timeline Playback
    function toggleTimelinePlayback() {{
        isTimelinePlaybackActive = !isTimelinePlaybackActive;
        var bar = document.getElementById('timelinePlaybackBar');
        var btn = document.getElementById('timeplayBtn');
        if (isTimelinePlaybackActive) {{
            if (bar) bar.style.display = 'flex';
            if (btn) btn.className = 'hud-mini-btn active';
            currentPlaybackYear = minYrVal;
            applyTimelinePlaybackYear(currentPlaybackYear);
            startPlaybackTimer();
        }} else {{
            if (bar) bar.style.display = 'none';
            if (btn) btn.className = 'hud-mini-btn';
            stopPlaybackTimer();
            resetPlayback();
        }}
    }}
    function startPlaybackTimer() {{
        isPlaybackPlaying = true;
        var playBtn = document.getElementById('playbackPlayBtn');
        if (playBtn) playBtn.innerHTML = '⏸️';
        if (playbackTimer) clearInterval(playbackTimer);
        playbackTimer = setInterval(function() {{
            if (currentPlaybackYear >= maxYrVal) {{
                stopPlaybackTimer();
                return;
            }}
            currentPlaybackYear += 1;
            applyTimelinePlaybackYear(currentPlaybackYear);
        }}, playbackIntervalMs);
    }}
    function stopPlaybackTimer() {{
        isPlaybackPlaying = false;
        var playBtn = document.getElementById('playbackPlayBtn');
        if (playBtn) playBtn.innerHTML = '▶️';
        if (playbackTimer) {{
            clearInterval(playbackTimer);
            playbackTimer = null;
        }}
    }}
    function togglePlaybackPlay() {{
        if (isPlaybackPlaying) stopPlaybackTimer();
        else {{
            if (currentPlaybackYear >= maxYrVal) currentPlaybackYear = minYrVal;
            startPlaybackTimer();
        }}
    }}
    function onPlaybackSliderChange(val) {{
        currentPlaybackYear = parseInt(val, 10);
        applyTimelinePlaybackYear(currentPlaybackYear);
    }}
    function applyTimelinePlaybackYear(yr) {{
        var label = document.getElementById('playbackYearLabel');
        var slider = document.getElementById('playbackYearSlider');
        if (label) label.innerText = yr;
        if (slider) slider.value = yr;

        var visibleNodeIds = new Set();
        var nodeUpdates = [];
        rawNodes.forEach(function(n) {{
            var nYr = n.year || 2020;
            var isVisible = (nYr <= yr);
            if (isVisible) visibleNodeIds.add(n.id);
            nodeUpdates.push({{ id: n.id, hidden: !isVisible, opacity: isVisible ? 1.0 : 0.0 }});
        }});
        nodes.update(nodeUpdates);

        var edgeUpdates = [];
        rawEdges.forEach(function(e) {{
            var edgeVisible = visibleNodeIds.has(e.from) && visibleNodeIds.has(e.to);
            edgeUpdates.push({{ id: e.id, hidden: !edgeVisible }});
        }});
        edges.update(edgeUpdates);
    }}
    function resetPlayback() {{
        currentPlaybackYear = maxYrVal;
        applyTimelinePlaybackYear(maxYrVal);
        stopPlaybackTimer();
    }}

    // BẬT / TẮT POPOVER CHỌN TẦNG CHECKBOX
    function toggleLayerFilterPopover() {{
        var pop = document.getElementById('layerFilterPopover');
        var btn = document.getElementById('layerFilterToggleBtn');
        if (pop) {{
            var isHidden = (pop.style.display === 'none' || !pop.style.display);
            pop.style.display = isHidden ? 'block' : 'none';
            if (btn) btn.classList.toggle('active', isHidden);
        }}
    }}

    // THIẾT LẬP NHANH CÁC PRESET CHO CHECKBOX
    function setLayerPreset(preset) {{
        var chkF0 = document.getElementById('chk_layer_f0');
        var chkF1 = document.getElementById('chk_layer_f1');
        var chkF2 = document.getElementById('chk_layer_f2');
        var chkF3 = document.getElementById('chk_layer_f3');
        var chkR1 = document.getElementById('chk_layer_r1');
        var chkR2 = document.getElementById('chk_layer_r2');
        var chkR3 = document.getElementById('chk_layer_r3');
        var chkIso = document.getElementById('chk_layer_isolated');

        if (preset === 'all') {{
            if (chkF0) chkF0.checked = true;
            if (chkF1) chkF1.checked = true;
            if (chkF2) chkF2.checked = true;
            if (chkF3) chkF3.checked = true;
            if (chkR1) chkR1.checked = true;
            if (chkR2) chkR2.checked = true;
            if (chkR3) chkR3.checked = true;
            if (chkIso) chkIso.checked = true;
        }} else if (preset === 'f0_forward') {{
            if (chkF0) chkF0.checked = true;
            if (chkF1) chkF1.checked = true;
            if (chkF2) chkF2.checked = true;
            if (chkF3) chkF3.checked = true;
            if (chkR1) chkR1.checked = false;
            if (chkR2) chkR2.checked = false;
            if (chkR3) chkR3.checked = false;
            if (chkIso) chkIso.checked = true;
        }} else if (preset === 'f0_backward') {{
            if (chkF0) chkF0.checked = true;
            if (chkF1) chkF1.checked = false;
            if (chkF2) chkF2.checked = false;
            if (chkF3) chkF3.checked = false;
            if (chkR1) chkR1.checked = true;
            if (chkR2) chkR2.checked = true;
            if (chkR3) chkR3.checked = true;
            if (chkIso) chkIso.checked = true;
        }} else if (preset === 'f0_only') {{
            if (chkF0) chkF0.checked = true;
            if (chkF1) chkF1.checked = false;
            if (chkF2) chkF2.checked = false;
            if (chkF3) chkF3.checked = false;
            if (chkR1) chkR1.checked = false;
            if (chkR2) chkR2.checked = false;
            if (chkR3) chkR3.checked = false;
            if (chkIso) chkIso.checked = false;
        }}
        applyGraphFilters();
    }}

    // DYNAMIC MULTI-LAYER CHECKBOX FILTERING (CHECK TỪNG TẦNG RIÊNG BIỆT & F0 ANCHOR)
    function applyGraphFilters() {{
        var edgeEl = document.getElementById('edgeFilter');
        var edgeVal = edgeEl ? edgeEl.value : 'all';

        var chkPinF0 = document.getElementById('chk_pin_f0') ? document.getElementById('chk_pin_f0').checked : true;
        var chkF0 = document.getElementById('chk_layer_f0') ? document.getElementById('chk_layer_f0').checked : true;
        var chkF1 = document.getElementById('chk_layer_f1') ? document.getElementById('chk_layer_f1').checked : true;
        var chkF2 = document.getElementById('chk_layer_f2') ? document.getElementById('chk_layer_f2').checked : true;
        var chkF3 = document.getElementById('chk_layer_f3') ? document.getElementById('chk_layer_f3').checked : true;
        var chkR1 = document.getElementById('chk_layer_r1') ? document.getElementById('chk_layer_r1').checked : true;
        var chkR2 = document.getElementById('chk_layer_r2') ? document.getElementById('chk_layer_r2').checked : true;
        var chkR3 = document.getElementById('chk_layer_r3') ? document.getElementById('chk_layer_r3').checked : true;
        var chkIso = document.getElementById('chk_layer_isolated') ? document.getElementById('chk_layer_isolated').checked : true;

        var visibleNodeIds = new Set();
        var nodeUpdates = [];

        rawNodes.forEach(function(n) {{
            var isSeed = (n.level === 0 || n.layer === 'seed');
            var lvl = n.level || 0;
            var isIso = n.is_isolated || false;
            var matchLayer = false;

            if (isSeed) {{
                matchLayer = (chkF0 || chkPinF0);
            }} else if (lvl === 1 || (lvl > 0 && n.layer === 'forward' && lvl === 1)) {{
                matchLayer = chkF1;
            }} else if (lvl === 2) {{
                matchLayer = chkF2;
            }} else if (lvl >= 3 || (lvl > 0 && n.layer === 'forward')) {{
                matchLayer = chkF3;
            }} else if (lvl === -1 || (lvl < 0 && n.layer === 'backward' && lvl === -1)) {{
                matchLayer = chkR1;
            }} else if (lvl === -2) {{
                matchLayer = chkR2;
            }} else if (lvl <= -3 || (lvl < 0 && n.layer === 'backward')) {{
                matchLayer = chkR3;
            }}

            // Nếu bài báo độc lập và người dùng bỏ chọn nhóm độc lập -> ẩn
            if (isIso && !chkIso) {{
                matchLayer = false;
            }}

            if (matchLayer) visibleNodeIds.add(n.id);
            nodeUpdates.push({{ id: n.id, hidden: !matchLayer }});
        }});
        nodes.update(nodeUpdates);

        var edgeUpdates = [];
        rawEdges.forEach(function(e) {{
            var matchEdge = (edgeVal === 'all' || e.edge_type === edgeVal);
            var nodesVisible = visibleNodeIds.has(e.from) && visibleNodeIds.has(e.to);
            var isEdgeShown = matchEdge && nodesVisible;
            edgeUpdates.push({{ id: e.id, hidden: !isEdgeShown }});
        }});
        edges.update(edgeUpdates);

        var badge = document.getElementById('layerFilterCountBadge');
        if (badge) {{
            badge.innerText = visibleNodeIds.size + '/' + rawNodes.length + ' bài';
        }}

        if (typeof nodeView !== 'undefined' && nodeView.refresh) {{
            nodeView.refresh();
        }}
        if (typeof edgeView !== 'undefined' && edgeView.refresh) {{
            edgeView.refresh();
        }}
        if (typeof network !== 'undefined' && network.redraw) {{
            network.redraw();
        }}
    }}

    // Lineage Tracing
    function toggleLineageMode() {{
        isLineageTracingOn = !isLineageTracingOn;
        var btn = document.getElementById('dockBtnTrace');
        var lbtn = document.getElementById('lineageBtn');
        if (btn) btn.classList.toggle('active', isLineageTracingOn);
        if (lbtn) lbtn.classList.toggle('active', isLineageTracingOn);
        if (!isLineageTracingOn) resetLineageHighlight();
        else if (selectedLineageNodeId) traceAncestryAndDescendants(selectedLineageNodeId);
    }}
    function traceAncestryAndDescendants(targetNodeId) {{
        selectedLineageNodeId = targetNodeId;
        var lineageNodes = new Set([targetNodeId]);
        var lineageEdges = new Set();

        var queueUp = [targetNodeId];
        var visitedUp = new Set([targetNodeId]);
        while (queueUp.length > 0) {{
            var curr = queueUp.shift();
            rawEdges.forEach(function(e) {{
                if (e.to === curr && !visitedUp.has(e.from)) {{
                    visitedUp.add(e.from);
                    lineageNodes.add(e.from);
                    lineageEdges.add(e.id);
                    queueUp.push(e.from);
                }}
            }});
        }}

        var queueDown = [targetNodeId];
        var visitedDown = new Set([targetNodeId]);
        while (queueDown.length > 0) {{
            var curr = queueDown.shift();
            rawEdges.forEach(function(e) {{
                if (e.from === curr && !visitedDown.has(e.to)) {{
                    visitedDown.add(e.to);
                    lineageNodes.add(e.to);
                    lineageEdges.add(e.id);
                    queueDown.push(e.to);
                }}
            }});
        }}

        var nodeUpdates = [];
        rawNodes.forEach(function(n) {{
            var inLineage = lineageNodes.has(n.id);
            nodeUpdates.push({{
                id: n.id,
                opacity: inLineage ? 1.0 : 0.18,
                borderWidth: (n.id === targetNodeId) ? 4.5 : (inLineage ? 3.0 : 1.0)
            }});
        }});
        nodes.update(nodeUpdates);

        var edgeUpdates = [];
        rawEdges.forEach(function(e) {{
            var inLineage = lineageEdges.has(e.id);
            edgeUpdates.push({{
                id: e.id,
                color: inLineage ? {{ color: '#F59E0B', opacity: 1.0, highlight: '#F59E0B' }} : {{ color: 'rgba(100,116,139,0.08)', opacity: 0.08 }},
                width: inLineage ? 3.2 : 1.0
            }});
        }});
        edges.update(edgeUpdates);
    }}
    function resetLineageHighlight() {{
        selectedLineageNodeId = null;
        var nodeUpdates = [];
        rawNodes.forEach(function(n) {{
            var isSeed = (n.level === 0 || n.layer === 'seed');
            nodeUpdates.push({{ id: n.id, opacity: 1.0, borderWidth: isSeed ? 3.5 : (n.is_isolated ? 2.6 : 1.8) }});
        }});
        nodes.update(nodeUpdates);

        var edgeUpdates = [];
        rawEdges.forEach(function(e) {{
            edgeUpdates.push({{ id: e.id, color: e.color, width: e.width }});
        }});
        edges.update(edgeUpdates);
    }}

    // 10 ACADEMIC LAYOUT ENGINES VỚI CƠ CHẾ CHỐNG ĐÈ TRÙNG NĂM (SAME-YEAR ANTI-COLLISION)
    function switchLayoutMode(mode) {{
        currentLayoutMode = mode;
        var sel = document.getElementById('layoutSelector');
        if (sel) sel.value = mode;

        var dockMap = {{
            'timeline': 'dockBtnTimeline',
            'radar': 'dockBtnRadar',
            'fishbone': 'dockBtnFishbone',
            'dendrogram': 'dockBtnDendrogram',
            'hierarchical': 'dockBtnHierarchical',
            'matrix': 'dockBtnMatrix',
            'force': 'dockBtnForce',
            'quartile': 'dockBtnQuartile',
            'diamond': 'dockBtnDiamond',
            'fanchart': 'dockBtnFanChart'
        }};

        Object.values(dockMap).forEach(function(btnId) {{
            var b = document.getElementById(btnId);
            if (b) b.classList.remove('active');
        }});
        if (dockMap[mode]) {{
            var activeB = document.getElementById(dockMap[mode]);
            if (activeB) activeB.classList.add('active');
        }}

        // Group nodes by year for anti-collision
        var yearGroups = {{}};
        rawNodes.forEach(function(n) {{
            var yr = n.year || 2020;
            if (!yearGroups[yr]) yearGroups[yr] = [];
            yearGroups[yr].push(n.id);
        }});

        if (mode === 'timeline') {{
            // 1. DÒNG THỜI GIAN THẲNG NGANG (HISTCITE) - So le trục Y
            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            var updates = [];
            rawNodes.forEach(function(n) {{
                var yr = n.year || 2020;
                var listInYr = yearGroups[yr] || [n.id];
                var idxInYr = listInYr.indexOf(n.id);
                var totalInYr = listInYr.length;
                // Staggered Y offset
                var yOffset = (idxInYr - (totalInYr - 1) / 2) * 95 + ((idxInYr % 2 === 0) ? 14 : -14);
                updates.push({{ id: n.id, x: n.x_timeline, y: yOffset, physics: false }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 220);

        }} else if (mode === 'radar') {{
            // 2. QUỸ ĐẠO RADAR ĐỒNG TÂM (CONCENTRIC RADAR)
            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            var updates = [];
            var seedNode = rawNodes.find(function(n) {{ return (n.level === 0 || n.layer === 'seed'); }}) || rawNodes[0];
            var nonSeeds = rawNodes.filter(function(n) {{ return n.id !== (seedNode ? seedNode.id : ''); }});
            
            if (seedNode) {{
                updates.push({{ id: seedNode.id, x: 0, y: 0, physics: false }});
            }}

            var yrSpan = Math.max(1, maxYrVal - minYrVal);
            nonSeeds.forEach(function(n, idx) {{
                var yr = n.year || 2020;
                var yrNorm = (yr - minYrVal) / yrSpan;
                var ringRadius = 180 + yrNorm * 380;
                
                var listInYr = yearGroups[yr] || [n.id];
                var idxInYr = listInYr.indexOf(n.id);
                var totalInYr = listInYr.length;
                
                var baseAngle = ((idx + 0.5) / nonSeeds.length) * 2 * Math.PI;
                var angleOffset = (idxInYr - (totalInYr - 1) / 2) * (Math.PI / 10);
                var finalAngle = baseAngle + angleOffset;

                updates.push({{
                    id: n.id,
                    x: Math.round(ringRadius * Math.cos(finalAngle)),
                    y: Math.round(ringRadius * Math.sin(finalAngle)),
                    physics: false
                }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 220);

        }} else if (mode === 'fishbone') {{
            // 3. SƠ ĐỒ XƯƠNG CÁ HỌC THUẬT (ISHIKAWA FISHBONE)
            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            var updates = [];
            rawNodes.forEach(function(n) {{
                var yr = n.year || 2020;
                var xPos = (yr - minYrVal) * 250 - ((maxYrVal - minYrVal) * 125);
                var isSeed = (n.level === 0 || n.layer === 'seed');
                var isBack = (n.level < 0 || n.layer === 'backward');
                
                var listInYr = yearGroups[yr] || [n.id];
                var idxInYr = listInYr.indexOf(n.id);
                var rankDist = 80 + idxInYr * 85;

                if (isSeed) {{
                    updates.push({{ id: n.id, x: 0, y: 0, physics: false }});
                }} else if (isBack) {{
                    // Xương cá dưới (45 độ)
                    updates.push({{ id: n.id, x: xPos - (rankDist * 0.7), y: rankDist, physics: false }});
                }} else {{
                    // Xương cá trên (-45 độ)
                    updates.push({{ id: n.id, x: xPos + (rankDist * 0.7), y: -rankDist, physics: false }});
                }}
            }});
            nodes.update(updates);
            setTimeout(fitView, 220);

        }} else if (mode === 'dendrogram') {{
            // 4. CÂY THƯ MỤC / NHÁNH CÂY PHÂN CẤP (DENDROGRAM TREE)
            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            var updates = [];
            var seeds = rawNodes.filter(function(n) {{ return (n.level === 0 || n.layer === 'seed'); }});
            var backwardPapers = rawNodes.filter(function(n) {{ return (n.level < 0 || n.layer === 'backward'); }});
            var forwardPapers = rawNodes.filter(function(n) {{ return (n.level > 0 || n.layer === 'forward'); }});

            seeds.forEach(function(n, i) {{
                updates.push({{ id: n.id, x: 0, y: (i * 90) - ((seeds.length - 1) * 45), physics: false }});
            }});

            backwardPapers.forEach(function(n, i) {{
                var lvl = Math.abs(n.level || 1);
                var xPos = - (lvl * 260);
                var yOffset = (i - (backwardPapers.length - 1) / 2) * 85 + ((i % 2 === 0) ? 12 : -12);
                updates.push({{ id: n.id, x: xPos, y: yOffset, physics: false }});
            }});

            forwardPapers.forEach(function(n, j) {{
                var lvl = Math.abs(n.level || 1);
                var xPos = (lvl * 260);
                var yOffset = (j - (forwardPapers.length - 1) / 2) * 85 + ((j % 2 === 0) ? 12 : -12);
                updates.push({{ id: n.id, x: xPos, y: yOffset, physics: false }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 220);

        }} else if (mode === 'hierarchical') {{
            // 5. CÂY PHẢ HỆ CÓ HƯỚNG (CITESPACE DAG)
            var updates = [];
            rawNodes.forEach(function(n) {{ updates.push({{ id: n.id, physics: true }}); }});
            nodes.update(updates);

            network.setOptions({{
                layout: {{ hierarchical: {{ enabled: true, direction: 'UD', sortMethod: 'directed', levelSeparation: 150, nodeSpacing: 180 }} }},
                physics: {{ hierarchicalRepulsion: {{ nodeDistance: 170 }}, solver: 'hierarchicalRepulsion' }}
            }});
            setTimeout(fitView, 350);

        }} else if (mode === 'matrix') {{
            // 6. MA TRẬN CỤM CHỦ ĐỀ & TẠP CHÍ (CLUSTERED TOPIC MATRIX)
            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            var updates = [];
            var cols = Math.ceil(Math.sqrt(rawNodes.length));
            rawNodes.forEach(function(n, idx) {{
                var row = Math.floor(idx / cols);
                var col = idx % cols;
                var xPos = (col - (cols - 1) / 2) * 220;
                var yPos = (row - (Math.ceil(rawNodes.length / cols) - 1) / 2) * 160;
                updates.push({{ id: n.id, x: xPos, y: yPos, physics: false }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 220);

        }} else if (mode === 'quartile') {{
            // 8. PHÂN LÀN SCOPUS Q1-Q4 (QUARTILE LANES)
            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            var lanes = {{ core: [], q1: [], q2: [], other: [] }};
            rawNodes.forEach(function(n) {{
                var p = metaDict[n.id] || {{}};
                var tier = (p.scopus_tier || '').toLowerCase();
                if (p.level === 0 || p.layer === 'seed') lanes.core.push(n.id);
                else if (tier.indexOf('q1') !== -1) lanes.q1.push(n.id);
                else if (tier.indexOf('q2') !== -1) lanes.q2.push(n.id);
                else lanes.other.push(n.id);
            }});

            var laneX = {{ core: -440, q1: -150, q2: 150, other: 440 }};
            var updates = [];
            ['core', 'q1', 'q2', 'other'].forEach(function(k) {{
                var list = lanes[k];
                list.forEach(function(id, idx) {{
                    var yOffset = (idx - (list.length - 1) / 2) * 95 + ((idx % 2 === 0) ? 14 : -14);
                    updates.push({{ id: id, x: laneX[k], y: yOffset, physics: false }});
                }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 220);

        }} else if (mode === 'diamond') {{
            // 9. MẶT PHẲNG KIM CƯƠNG ĐỐI XỨNG (DUAL-DIAMOND HORIZON)
            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            var updates = [];
            var seeds = rawNodes.filter(function(n) {{ return (n.level === 0 || n.layer === 'seed'); }});
            var backwardPapers = rawNodes.filter(function(n) {{ return (n.level < 0 || n.layer === 'backward'); }});
            var forwardPapers = rawNodes.filter(function(n) {{ return (n.level > 0 || n.layer === 'forward'); }});

            seeds.forEach(function(n, i) {{
                updates.push({{ id: n.id, x: (i * 80) - ((seeds.length - 1) * 40), y: 0, physics: false }});
            }});

            var bCount = backwardPapers.length || 1;
            backwardPapers.forEach(function(n, i) {{
                var lvl = Math.abs(n.level || 1);
                var radius = 240 + (lvl - 1) * 140;
                var angle = Math.PI / 2 + ((Math.PI * (i + 0.5)) / bCount);
                updates.push({{ id: n.id, x: Math.round(radius * Math.cos(angle)), y: Math.round(radius * Math.sin(angle)), physics: false }});
            }});

            var fCount = forwardPapers.length || 1;
            forwardPapers.forEach(function(n, j) {{
                var lvl = Math.abs(n.level || 1);
                var radius = 260 + (lvl - 1) * 150;
                var angle = -Math.PI / 2 + ((Math.PI * (j + 0.5)) / fCount);
                updates.push({{ id: n.id, x: Math.round(radius * Math.cos(angle)), y: Math.round(radius * Math.sin(angle)), physics: false }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 220);

        }} else if (mode === 'fanchart') {{
            // 10. QUẠT NAN PHẢ HỆ TỎA TRÒN 180 ĐỘ (ANCESTRY FAN CHART)
            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});
            var updates = [];
            var seeds = rawNodes.filter(function(n) {{ return (n.level === 0 || n.layer === 'seed'); }});
            var otherPapers = rawNodes.filter(function(n) {{ return !(n.level === 0 || n.layer === 'seed'); }});

            seeds.forEach(function(n) {{
                updates.push({{ id: n.id, x: 0, y: 180, physics: false }});
            }});

            otherPapers.forEach(function(n, i) {{
                var yr = n.year || 2020;
                var yrSpan = Math.max(1, maxYrVal - minYrVal);
                var radius = 220 + ((yr - minYrVal) / yrSpan) * 340;
                var angle = Math.PI + (i / Math.max(1, otherPapers.length - 1)) * Math.PI;
                updates.push({{ id: n.id, x: Math.round(radius * Math.cos(angle)), y: 180 + Math.round(radius * Math.sin(angle)), physics: false }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 220);

        }} else {{
            // 7. MẠNG LƯỚI ĐỘNG HỌC LƯỢNG TỬ (FORCE-DIRECTED QUANTUM)
            network.setOptions({{ layout: {{ hierarchical: false }} }});
            var updates = [];
            rawNodes.forEach(function(n) {{ updates.push({{ id: n.id, physics: true }}); }});
            nodes.update(updates);
            network.setOptions(forceOptions);
            setTimeout(fitView, 220);
        }}
    }}

    // Canvas Background Guides for Timeline & Radar & Fishbone
    network.on('beforeDrawing', function(ctx) {{
        if (currentLayoutMode === 'radar') {{
            ctx.save();
            ctx.setLineDash([6, 6]);
            ctx.lineWidth = 1.2;
            [180, 290, 400, 520].forEach(function(r, idx) {{
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.20)';
                ctx.beginPath();
                ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
                ctx.stroke();
            }});
            ctx.font = 'bold 11px JetBrains Mono, monospace';
            ctx.fillStyle = '#38BDF8';
            ctx.fillText('📡 RADAR RANGE 180px - 520px', 10, -530);
            ctx.restore();

        }} else if (currentLayoutMode === 'timeline') {{
            ctx.save();
            for (var y = minYrVal; y <= maxYrVal; y++) {{
                var xPos = (y - minYrVal) * 260 - ((maxYrVal - minYrVal) * 130);
                ctx.setLineDash([6, 6]);
                ctx.lineWidth = 1.0;
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.18)';
                ctx.beginPath();
                ctx.moveTo(xPos, -420);
                ctx.lineTo(xPos, 420);
                ctx.stroke();

                ctx.setLineDash([]);
                // Sleek translucent badge with rounded corners
                ctx.fillStyle = 'rgba(15, 23, 42, 0.90)';
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.65)';
                ctx.lineWidth = 1.2;

                if (ctx.roundRect) {{
                    ctx.beginPath();
                    ctx.roundRect(xPos - 36, -435, 72, 22, 6);
                    ctx.fill();
                    ctx.stroke();
                }} else {{
                    ctx.fillRect(xPos - 36, -435, 72, 22);
                    ctx.strokeRect(xPos - 36, -435, 72, 22);
                }}

                ctx.font = 'bold 11px Plus Jakarta Sans, sans-serif';
                ctx.fillStyle = '#38BDF8';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('📅 ' + y, xPos, -424);
            }}
            ctx.restore();

        }} else if (currentLayoutMode === 'fishbone') {{
            ctx.save();
            ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.moveTo(-650, 0);
            ctx.lineTo(650, 0);
            ctx.stroke();

            ctx.font = 'bold 12px Plus Jakarta Sans, sans-serif';
            ctx.fillStyle = 'rgba(56, 189, 248, 0.85)';
            ctx.fillText('🐟 TRỤC SỐNG LƯNG THỜI GIAN (CHRONO-BACKBONE)', -620, -12);
            ctx.fillText('🏛️ CỘI NGUỒN (R) ➔', -450, 45);
            ctx.fillText('🚀 KẾ THỪA (F) ➔', 250, -45);
            ctx.restore();
        }}
    }});

    var photonSpeedFactor = 1.0;
    var hoveredNodeId = null;
    var hoveredEdgeId = null;
    var isLegendDrawerOpen = false;

    // Điều khiển tốc độ photon & tia laser hover
    function setPhotonSpeed(val) {{
        photonSpeedFactor = parseFloat(val);
        var lbl = document.getElementById('photonSpeedVal');
        if (lbl) {{
            lbl.innerText = (photonSpeedFactor === 0 ? '0x' : photonSpeedFactor.toFixed(1) + 'x');
        }}
    }}

    // Bật/Tắt Drawer Ghi chú & Hướng dẫn từ Dock
    function toggleLegendDrawer() {{
        isLegendDrawerOpen = !isLegendDrawerOpen;
        var drawer = document.getElementById('dockLegendDrawer');
        var btn = document.getElementById('dockBtnLegend');
        if (drawer) {{
            drawer.style.display = isLegendDrawerOpen ? 'flex' : 'none';
        }}
        if (btn) {{
            if (isLegendDrawerOpen) btn.classList.add('active');
            else btn.classList.remove('active');
        }}
    }}

    // Smart Filter Inside Legend Drawer
    function filterGuideDrawer(query) {{
        var q = (query || '').trim().toLowerCase();
        var cards = document.querySelectorAll('.guide-searchable-item');
        var count = 0;
        cards.forEach(function(card) {{
            var text = card.innerText.toLowerCase();
            if (!q || text.indexOf(q) !== -1) {{
                card.style.display = 'flex';
                count++;
            }} else {{
                card.style.display = 'none';
            }}
        }});
        var emptyEl = document.getElementById('guideSearchEmpty');
        if (emptyEl) {{
            emptyEl.style.display = (count === 0 ? 'block' : 'none');
        }}
    }}

    // Smart HUD Hover Inspector ở vùng an toàn (Góc trên canvas)
    function updateHoverInspectorNode(nid) {{
        var pop = document.getElementById('layerFilterPopover');
        if (pop && pop.style.display === 'block') return;

        var p = metaDict[nid];
        if (!p) return;
        var insp = document.getElementById('graphHoverInspector');
        var edgeInsp = document.getElementById('graphEdgeInspector');
        if (edgeInsp) edgeInsp.classList.remove('visible');
        if (!insp) return;

        var typeEl = document.getElementById('hoverChipType');
        var yearEl = document.getElementById('hoverChipYear');
        var titleEl = document.getElementById('hoverInspectorTitle');
        var metaEl = document.getElementById('hoverInspectorMeta');
        var linksEl = document.getElementById('hoverInspectorLinks');
        var absEl = document.getElementById('hoverInspectorAbstract');

        if (p.level === 0 || p.layer === 'seed') {{
            if (typeEl) typeEl.innerText = '★ F0 BÀI GỐC (ANCHOR)';
        }} else if (p.level < 0 || p.layer === 'backward') {{
            if (typeEl) typeEl.innerText = '🏛️ CỘI NGUỒN (R' + Math.abs(p.level || 1) + ')';
        }} else {{
            if (typeEl) typeEl.innerText = '🚀 KẾ THỪA (F' + Math.abs(p.level || 1) + ')';
        }}

        if (yearEl) yearEl.innerText = p.year || 'n.d.';
        if (titleEl) titleEl.innerText = p.title || 'Untitled Paper';
        if (metaEl) metaEl.innerText = (p.authors || p.first_author || 'Author') + ' • ' + (p.venue || 'Journal') + ' • ' + (p.citation_count || 0) + ' trích dẫn';
        
        var outC = (p.outgoing_ids || []).length;
        var inC = (p.incoming_ids || []).length;
        
        var chkPinF0 = document.getElementById('chk_pin_f0') ? document.getElementById('chk_pin_f0').checked : true;
        var edgeFilterVal = document.getElementById('edgeFilter') ? document.getElementById('edgeFilter').value : 'all';

        var linkNote = '⚡ <b>Liên kết tổng thể:</b> ' + outC + ' tham chiếu (R) ➔ ' + inC + ' kế thừa (F).';
        if (outC === 0 && inC === 0) {{
            linkNote += '<br><span style="color:#FDE047;">⚠️ Ghi chú: Công trình độc lập trong tập mẫu này.</span>';
        }} else if (chkPinF0) {{
            linkNote += '<br><span style="color:#38BDF8; font-size:9.5px;">💡 F0 được ghim neo giữ trung tâm để đối chiếu quan hệ kế thừa trực tiếp.</span>';
        }}
        if (linksEl) linksEl.innerHTML = linkNote;

        if (absEl && p.abstract) {{
            var cleanAbs = p.abstract.replace(/<[^>]*>?/gm, '');
            var shortAbs = cleanAbs.length > 130 ? cleanAbs.substring(0, 130) + '...' : cleanAbs;
            absEl.innerHTML = '<b>Tóm tắt:</b> ' + shortAbs;
            absEl.style.display = 'block';
        }} else if (absEl) {{
            absEl.style.display = 'none';
        }}

        insp.classList.add('visible');
    }}

    // Smart Node Search (DOI, Authors, Year, Exact Title, Keywords, Abstract)
    function searchAndFocusNode(query) {{
        if (!query || !query.trim()) {{
            var resetUpdates = rawNodes.map(function(n) {{
                return {{ id: n.id, opacity: 1.0, shadow: {{ enabled: true, color: 'rgba(0,0,0,0.5)', size: 8, x:0, y:0 }} }};
            }});
            nodes.update(resetUpdates);
            hideHoverInspector();
            return;
        }}

        var q = query.trim().toLowerCase();
        var cleanQ = q.replace(/^https?:\\/\\/doi\\.org\\//i, '').replace(/^(doi:)/i, '').trim();

        var matchedIds = new Set();
        var primaryMatchId = null;

        rawNodes.forEach(function(n) {{
            var p = metaDict[n.id] || {{}};
            var title = (p.title || '').toLowerCase();
            var authors = (p.authors || '').toLowerCase();
            var firstAuth = (p.first_author || '').toLowerCase();
            var year = String(p.year || '');
            var doi = (p.doi || '').toLowerCase();
            var venue = (p.venue || '').toLowerCase();
            var abs = (p.abstract || '').toLowerCase();
            var layer = (p.layer || '').toLowerCase();
            var levelTag = (p.level === 0 ? 'f0' : (p.level < 0 ? 'r' + Math.abs(p.level) : 'f' + p.level)).toLowerCase();

            var match = false;
            if (doi && (doi.indexOf(cleanQ) !== -1 || cleanQ.indexOf(doi) !== -1)) match = true;
            else if (authors.indexOf(q) !== -1 || firstAuth.indexOf(q) !== -1) match = true;
            else if (year === q || (q.startsWith('>') && parseInt(year) > parseInt(q.slice(1))) || (q.startsWith('<') && parseInt(year) < parseInt(q.slice(1)))) match = true;
            else if (title.indexOf(q) !== -1) match = true;
            else if (venue.indexOf(q) !== -1) match = true;
            else if (levelTag === q || layer === q) match = true;
            else if (abs.indexOf(q) !== -1) match = true;

            if (match) {{
                matchedIds.add(n.id);
                if (!primaryMatchId) primaryMatchId = n.id;
            }}
        }});

        var updates = [];
        rawNodes.forEach(function(n) {{
            var isM = matchedIds.has(n.id);
            updates.push({{
                id: n.id,
                opacity: (matchedIds.size > 0 ? (isM ? 1.0 : 0.15) : 1.0),
                shadow: isM ? {{ enabled: true, color: 'var(--theme-accent)', size: 18, x:0, y:0 }} : {{ enabled: false }}
            }});
        }});
        nodes.update(updates);

        if (primaryMatchId) {{
            network.focus(primaryMatchId, {{
                scale: 1.35,
                animation: {{ duration: 400, easingFunction: 'easeInOutQuad' }}
            }});
            updateHoverInspectorNode(primaryMatchId);
            selectPaperFromTable(primaryMatchId);
        }}
    }}

    function updateHoverInspectorEdge(eid) {{
        var pop = document.getElementById('layerFilterPopover');
        if (pop && pop.style.display === 'block') return;

        var e = rawEdges.find(function(item) {{ return item.id === eid; }});
        if (!e) return;
        var sP = metaDict[e.from] || {{}};
        var dP = metaDict[e.to] || {{}};
        var edgeInsp = document.getElementById('graphEdgeInspector');
        var nodeInsp = document.getElementById('graphHoverInspector');
        if (nodeInsp) nodeInsp.classList.remove('visible');
        if (!edgeInsp) return;

        var sYr = parseInt(sP.year || 2020, 10);
        var dYr = parseInt(dP.year || 2020, 10);
        var gap = Math.abs(sYr - dYr);

        var typeBadge = document.getElementById('edgeTypeBadge');
        var bodyEl = document.getElementById('edgeEpistemicBody');

        var eType = e.edge_type || 'direct';
        var typeName = '🔷 Kế thừa 1 chiều trực tiếp';
        var dynamicDesc = 'Công trình tiếp thu khung lý thuyết và mở rộng phương pháp nghiên cứu.';
        
        if (eType === 'mutual') {{
            typeName = '🔶 Đối thoại học thuật 2 chiều (Reciprocal)';
            dynamicDesc = 'Hai nhóm nghiên cứu trích dẫn chéo tương hỗ, hình thành trường phái tranh luận chuyên sâu.';
        }} else if (eType === 'cross_bridge') {{
            typeName = '🔮 Bắc cầu xuyên tầng cội nguồn (Cross-Bridge)';
            dynamicDesc = 'Bước tiến mới neo trực tiếp vào nền tảng lý thuyết ban đầu mà không qua tầng trung gian.';
        }} else if (eType === 'intra_layer') {{
            typeName = '🟢 Đồng phát triển cùng phân tầng (Intra-Layer)';
            dynamicDesc = 'Các công trình trong cùng thế hệ nghiên cứu bổ trợ dữ liệu thực chứng cho nhau.';
        }}

        if (typeBadge) typeBadge.innerText = typeName;
        if (bodyEl) {{
            bodyEl.innerHTML = 
                '<div style="font-weight:400; color:#FDE047; margin-bottom:3px;">' +
                    '[' + (sP.first_author || 'Paper A') + ' (' + (sP.year || 'n.d.') + ')] ➔ [' + (dP.first_author || 'Paper B') + ' (' + (dP.year || 'n.d.') + ')]' +
                '</div>' +
                '<div style="color:#E2E8F0; margin-bottom:4px; font-size:10px;">' + dynamicDesc + '</div>' +
                '<div style="display:flex; justify-content:space-between; border-top:1px solid rgba(245,158,11,0.25); padding-top:4px; color:#A1A1AA; font-size:9.5px;">' +
                    '<span>⏳ Độ trễ tiếp thu: <b>' + (gap === 0 ? 'Cùng năm' : gap + ' năm') + '</b></span>' +
                    '<span>⚡ Trạng thái: <b>Laser Stream Active</b></span>' +
                '</div>';
        }}
        edgeInsp.classList.add('visible');
    }}

    function hideHoverInspector() {{
        var nodeInsp = document.getElementById('graphHoverInspector');
        var edgeInsp = document.getElementById('graphEdgeInspector');
        if (nodeInsp) nodeInsp.classList.remove('visible');
        if (edgeInsp) edgeInsp.classList.remove('visible');
    }}

    // Trợ năng Kéo Thả Tiện Lợi (Make Draggable Helper)
    function makeElementDraggable(elm) {{
        if (!elm) return;
        var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

        elm.onmousedown = function(e) {{
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'LABEL') return;
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
        }};

        function elementDrag(e) {{
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            elm.style.top = (elm.offsetTop - pos2) + "px";
            elm.style.left = (elm.offsetLeft - pos1) + "px";
            elm.style.bottom = 'auto';
            elm.style.right = 'auto';
        }}

        function closeDragElement() {{
            document.onmouseup = null;
            document.onmousemove = null;
        }}
    }}

    // Đăng ký sự kiện Hover chuẩn của Vis-Network
    network.on('hoverNode', function(params) {{
        hoveredNodeId = params.node;
        updateHoverInspectorNode(params.node);
    }});
    network.on('blurNode', function(params) {{
        hoveredNodeId = null;
        hideHoverInspector();
    }});
    network.on('hoverEdge', function(params) {{
        hoveredEdgeId = params.edge;
        updateHoverInspectorEdge(params.edge);
    }});
    network.on('blurEdge', function(params) {{
        hoveredEdgeId = null;
        hideHoverInspector();
    }});

    // Global Click Outside & Escape listener
    document.addEventListener('click', function(e) {{
        var pop = document.getElementById('layerFilterPopover');
        var btn = document.getElementById('layerFilterToggleBtn');
        var dockBtn = document.getElementById('dockBtnLayers');
        if (pop && pop.style.display === 'block') {{
            if (!pop.contains(e.target) && e.target !== btn && e.target !== dockBtn && !btn.contains(e.target)) {{
                pop.style.display = 'none';
                if (btn) btn.classList.remove('active');
            }}
        }}
    }});
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            var pop = document.getElementById('layerFilterPopover');
            var btn = document.getElementById('layerFilterToggleBtn');
            if (pop && pop.style.display === 'block') {{
                pop.style.display = 'none';
                if (btn) btn.classList.remove('active');
            }}
            hideHoverInspector();
        }}
    }});

    // Particles & Pulsing Halos & Instant Active Laser Beam Stream (afterDrawing)
    network.on('afterDrawing', function(ctx) {{
        var now = Date.now();
        var positions = network.getPositions();

        // 1. Halo Nhịp thở
        if (isPulsingOn) {{
            var pulse = (Math.sin(now / 550) + 1) / 2;
            rawNodes.forEach(function(n) {{
                var isSeed = (n.level === 0 || n.layer === 'seed');
                var isHighImpact = ((n.citations || 0) >= 200);

                if (isSeed || isHighImpact) {{
                    var pos = positions[n.id];
                    if (!pos) return;
                    var baseR = (n.size || 22);
                    var haloR = baseR + 8 + (pulse * (isSeed ? 16 : 10));

                    ctx.save();
                    var grad = ctx.createRadialGradient(pos.x, pos.y, baseR * 0.4, pos.x, pos.y, haloR);
                    if (isSeed) {{
                        grad.addColorStop(0, 'rgba(234, 67, 53, ' + (0.45 + pulse * 0.25) + ')');
                        grad.addColorStop(1, 'rgba(234, 67, 53, 0)');
                    }} else {{
                        grad.addColorStop(0, 'rgba(var(--theme-glow-rgb), ' + (0.45 + pulse * 0.25) + ')');
                        grad.addColorStop(1, 'rgba(var(--theme-glow-rgb), 0)');
                    }}
                    ctx.beginPath();
                    ctx.arc(pos.x, pos.y, haloR, 0, 2 * Math.PI, false);
                    ctx.fillStyle = grad;
                    ctx.fill();
                    ctx.restore();
                }}
            }});
        }}

        // 2. Dòng Hạt Photon Bình Thường (Có điều tốc)
        if (isParticlesOn) {{
            var tNow = (photonSpeedFactor > 0) ? (now / 1100 * photonSpeedFactor) : 0;
            rawEdges.forEach(function(e, idx) {{
                var p1 = positions[e.from];
                var p2 = positions[e.to];
                if (!p1 || !p2) return;

                var currentEdge = edges.get(e.id);
                if (currentEdge && currentEdge.hidden) return;

                var t = (photonSpeedFactor > 0) ? ((tNow + (idx * 0.19)) % 1.0) : ((idx * 0.19) % 1.0);
                var x = p1.x + (p2.x - p1.x) * t;
                var y = p1.y + (p2.y - p1.y) * t;

                ctx.save();
                ctx.beginPath();
                ctx.arc(x, y, 3.2, 0, 2 * Math.PI, false);
                ctx.fillStyle = 'var(--theme-accent)';
                ctx.shadowColor = 'var(--theme-glow)';
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.restore();
            }});
        }}

        // 3. HIỆU ỨNG TIA SÁNG LASER CHẠY LIÊN TỤC KHI HOVER / CHỌN (Instant Active Beam Highlight Stream)
        if (isLaserBeamOn && (hoveredNodeId || hoveredEdgeId)) {{
            var connectedEdges = [];
            if (hoveredNodeId) {{
                connectedEdges = rawEdges.filter(function(e) {{
                    return (e.from === hoveredNodeId || e.to === hoveredNodeId);
                }});
            }} else if (hoveredEdgeId) {{
                connectedEdges = rawEdges.filter(function(e) {{
                    return (e.id === hoveredEdgeId);
                }});
            }}

            var beamProgress = (photonSpeedFactor > 0) ? ((now / 650 * photonSpeedFactor) % 1.0) : 0.5;
            var beamProgress2 = (beamProgress + 0.5) % 1.0;

            connectedEdges.forEach(function(e) {{
                var p1 = positions[e.from];
                var p2 = positions[e.to];
                if (!p1 || !p2) return;

                ctx.save();
                ctx.strokeStyle = 'var(--theme-accent)';
                ctx.lineWidth = 3.8;
                ctx.shadowColor = 'var(--theme-glow)';
                ctx.shadowBlur = 14;
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();

                [beamProgress, beamProgress2].forEach(function(bt) {{
                    var bx = p1.x + (p2.x - p1.x) * bt;
                    var by = p1.y + (p2.y - p1.y) * bt;

                    ctx.beginPath();
                    ctx.arc(bx, by, 5.5, 0, 2 * Math.PI, false);
                    ctx.fillStyle = '#FFFFFF';
                    ctx.shadowColor = '#FDE047';
                    ctx.shadowBlur = 16;
                    ctx.fill();
                }});

                ctx.restore();
            }});
        }} else if (hoveredEdgeId) {{
            var targetEdge = rawEdges.find(function(e) {{ return e.id === hoveredEdgeId; }});
            if (targetEdge) {{
                var p1 = positions[targetEdge.from];
                var p2 = positions[targetEdge.to];
                if (p1 && p2) {{
                    var bProg = (photonSpeedFactor > 0) ? ((now / 600 * photonSpeedFactor) % 1.0) : 0.5;
                    ctx.save();
                    ctx.strokeStyle = '#F59E0B';
                    ctx.lineWidth = 4.2;
                    ctx.shadowColor = '#F59E0B';
                    ctx.shadowBlur = 16;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();

                    var bx = p1.x + (p2.x - p1.x) * bProg;
                    var by = p1.y + (p2.y - p1.y) * bProg;
                    ctx.beginPath();
                    ctx.arc(bx, by, 6.0, 0, 2 * Math.PI, false);
                    ctx.fillStyle = '#FFFFFF';
                    ctx.shadowColor = '#FFFFFF';
                    ctx.shadowBlur = 16;
                    ctx.fill();
                    ctx.restore();
                }}
            }}
        }}
    }});

    function dynamicAnimationLoop() {{
        if (isParticlesOn || isPulsingOn) network.redraw();
        requestAnimationFrame(dynamicAnimationLoop);
    }}
    requestAnimationFrame(dynamicAnimationLoop);

    // Auto-fit & Redraw on Mobile Viewport Resize / Orientation Change
    window.addEventListener('resize', function() {{
        if (network) {{
            network.redraw();
        }}
    }});
    window.addEventListener('orientationchange', function() {{
        setTimeout(function() {{
            if (network) {{
                network.redraw();
                network.fit({{ animation: {{ duration: 350, easingFunction: 'easeInOutQuad' }} }});
            }}
        }}, 250);
    }});

    // Auto-select primary seed on initial load & switch to timeline layout & Enable Draggable
    setTimeout(function() {{
        switchLayoutMode('timeline');
        if (rawNodes.length > 0) {{
            selectPaperFromTable(rawNodes[0].id);
        }}
        makeElementDraggable(document.getElementById('graphHoverInspector'));
        makeElementDraggable(document.getElementById('graphEdgeInspector'));
        makeElementDraggable(document.getElementById('layerFilterPopover'));
    }}, 400);
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

    def generate_standalone_fullscreen_html(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str]],
        height: str = "100vh",
        width: str = "100%"
    ) -> str:
        """
        Generate a dedicated viewport HTML with only Synapse Academic HUD & full canvas,
        completely hiding the bottom Related Papers & Selected Paper panels for maximum research focus.
        """
        return self.generate_network_html(
            nodes=nodes,
            edges=edges,
            height=height,
            width=width,
            standalone_fullscreen=True,
            hide_bottom_panels=True
        )
