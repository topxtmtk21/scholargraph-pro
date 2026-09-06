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
        width: str = "100%"
    ) -> str:
        """
        Construct interactive HTML graph with commercial Obsidian styling, international bibliometric node sizing,
        dynamic zoom controls, and a Dual-Mode (Force-directed vs Chronological Timeline evolution) layout.
        Color coding follows the Bidirectional Diamond Knowledge Graph standard:
        - 🔴 F0 (Seed): Ruby Red (#EA4335)
        - 🟣 R1-R3 (Backward Theoretical Roots): Royal Purple (#7C3AED), Indigo (#6366F1), Deep Indigo (#4338CA)
        - 🟢 F1-F3 (Forward Frontier Advances): Sky Cyan (#0284C7), Emerald (#059669), Amber (#D97706)
        """
        # Bảng màu Kim Cương Tri Thức Đa Tầng (Diamond Knowledge Graph Palette)
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
                "title": "⚠️ BÀI BÁO ĐỘC LẬP: Không có liên kết trích dẫn trực tiếp trong tập mẫu này" if is_isolated else ""
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
                    edge_color = {"color": "rgba(245, 158, 11, 0.85)", "highlight": "#F59E0B", "hover": "#FDE047"}
                    edge_width = 2.6
                    edge_dashes = False
                    arrows = {"to": {"enabled": True, "scaleFactor": 0.95}, "from": {"enabled": True, "scaleFactor": 0.95}}
                    edge_title = f"🔶 ĐỐI THOẠI HỌC THUẬT 2 CHIỀU:\n[{s_auth} ({s_yr})] ⟷ [{d_auth} ({d_yr})]\n(Hai nhóm nghiên cứu trích dẫn chéo lẫn nhau)"
                elif is_cross_bridge:
                    edge_type = "cross_bridge"
                    edge_color = {"color": "rgba(192, 132, 252, 0.88)", "highlight": "#C084FC", "hover": "#E879F9"}
                    edge_width = 2.2
                    edge_dashes = [6, 4]
                    arrows = {"to": {"enabled": True, "scaleFactor": 0.95}}
                    edge_title = f"🔮 BẮC CẦU XUYÊN TẦNG CỘI NGUỒN:\n[{s_auth} ({s_yr})] ➔ [{d_auth} ({d_yr})]\n(Công trình kế thừa neo trực tiếp vào cội nguồn lý thuyết)"
                elif is_intra:
                    edge_type = "intra_layer"
                    edge_color = {"color": "rgba(52, 211, 153, 0.80)", "highlight": "#34D399", "hover": "#6EE7B7"}
                    edge_width = 1.6
                    edge_dashes = [3, 3]
                    arrows = {"to": {"enabled": True, "scaleFactor": 0.85}}
                    edge_title = f"🟢 LIÊN KẾT NỘI BỘ CÙNG PHÂN TẦNG:\n[{s_auth} ({s_yr})] ➔ [{d_auth} ({d_yr})]\n(Đồng phát triển trong cùng thế hệ nghiên cứu)"
                else:
                    edge_type = "direct"
                    edge_color = {"color": "rgba(56, 189, 248, 0.70)", "highlight": "#38BDF8", "hover": "#60A5FA"}
                    edge_width = 1.8
                    edge_dashes = False
                    arrows = {"to": {"enabled": True, "scaleFactor": 0.90}}
                    edge_title = f"🔷 KẾ THỪA 1 CHIỀU TRỰC TIẾP:\n[{s_auth} ({s_yr})] ➔ [{d_auth} ({d_yr})]\n(Dòng kế thừa tiêu chuẩn từ cội nguồn hoặc bài gốc)"

                vis_edges.append({
                    "id": f"e_{src}_{dst}",
                    "from": src,
                    "to": dst,
                    "edge_type": edge_type,
                    "color": edge_color,
                    "arrows": arrows,
                    "width": edge_width,
                    "dashes": edge_dashes,
                    "title": edge_title,
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
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <style type="text/css">
        :root {{
            --theme-glow: #00F2FE;
            --theme-glow-rgb: 0, 242, 254;
            --theme-bg-base: #040914;
            --theme-panel-bg: rgba(6, 14, 28, 0.82);
            --theme-panel-border: rgba(0, 242, 254, 0.32);
            --theme-accent: #00F2FE;
            --theme-accent-hover: #38BDF8;
            --theme-text-main: #F8FAFC;
            --theme-text-dim: #94A3B8;
            --theme-badge-bg: rgba(0, 242, 254, 0.14);
        }}

        /* 5 THEMES KẾ THỪA ĐỒNG BỘ */
        body.theme-synapse-cyan {{
            --theme-glow: #00F2FE;
            --theme-glow-rgb: 0, 242, 254;
            --theme-bg-base: #040914;
            --theme-panel-bg: rgba(6, 14, 28, 0.84);
            --theme-panel-border: rgba(0, 242, 254, 0.35);
            --theme-accent: #00F2FE;
            --theme-accent-hover: #38BDF8;
            --theme-text-main: #F8FAFC;
            --theme-text-dim: #94A3B8;
            --theme-badge-bg: rgba(0, 242, 254, 0.14);
        }}
        body.theme-nebula-violet {{
            --theme-glow: #C084FC;
            --theme-glow-rgb: 192, 132, 252;
            --theme-bg-base: #090514;
            --theme-panel-bg: rgba(18, 10, 34, 0.86);
            --theme-panel-border: rgba(192, 132, 252, 0.35);
            --theme-accent: #C084FC;
            --theme-accent-hover: #E879F9;
            --theme-text-main: #FAF5FF;
            --theme-text-dim: #A8A29E;
            --theme-badge-bg: rgba(192, 132, 252, 0.16);
        }}
        body.theme-emerald-matrix {{
            --theme-glow: #10B981;
            --theme-glow-rgb: 16, 185, 129;
            --theme-bg-base: #030F0C;
            --theme-panel-bg: rgba(6, 26, 20, 0.86);
            --theme-panel-border: rgba(16, 185, 129, 0.35);
            --theme-accent: #10B981;
            --theme-accent-hover: #34D399;
            --theme-text-main: #ECFDF5;
            --theme-text-dim: #9CA3AF;
            --theme-badge-bg: rgba(16, 185, 129, 0.16);
        }}
        body.theme-solar-amber {{
            --theme-glow: #F59E0B;
            --theme-glow-rgb: 245, 158, 11;
            --theme-bg-base: #100A04;
            --theme-panel-bg: rgba(28, 18, 8, 0.86);
            --theme-panel-border: rgba(245, 158, 11, 0.38);
            --theme-accent: #F59E0B;
            --theme-accent-hover: #FCD34D;
            --theme-text-main: #FFFBEB;
            --theme-text-dim: #A1A1AA;
            --theme-badge-bg: rgba(245, 158, 11, 0.16);
        }}
        body.theme-nordic-light {{
            --theme-glow: #0284C7;
            --theme-glow-rgb: 2, 132, 199;
            --theme-bg-base: #F0F4F8;
            --theme-panel-bg: rgba(255, 255, 255, 0.90);
            --theme-panel-border: rgba(2, 132, 199, 0.35);
            --theme-accent: #0284C7;
            --theme-accent-hover: #0369A1;
            --theme-text-main: #0F172A;
            --theme-text-dim: #475569;
            --theme-badge-bg: rgba(2, 132, 199, 0.12);
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
            overflow: hidden;
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
            height: 100%;
            padding: 10px;
            gap: 10px;
            background: radial-gradient(circle at 50% 20%, rgba(var(--theme-glow-rgb), 0.08) 0%, transparent 70%);
        }}

        /* 1. TOP HEADER HUD BAR */
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
            box-shadow: 0 0 20px rgba(var(--theme-glow-rgb), 0.12);
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
            gap: 16px;
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
            min-height: 0;
            position: relative;
        }}

        /* SLIM VERTICAL DOCK BAR */
        .synapse-vertical-dock {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 12px 6px;
            background: var(--theme-panel-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--theme-panel-border);
            border-radius: 14px;
            box-shadow: 0 0 20px rgba(var(--theme-glow-rgb), 0.10);
            width: 48px;
            flex-shrink: 0;
        }}
        .dock-btn-group {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 100%;
            align-items: center;
        }}
        .dock-icon-btn {{
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: transparent;
            border: 1px solid transparent;
            color: var(--theme-text-dim);
            font-size: 16px;
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
            box-shadow: 0 0 12px rgba(var(--theme-glow-rgb), 0.25);
            transform: scale(1.08);
        }}
        .dock-icon-btn.active {{
            color: var(--theme-text-main);
            border-color: var(--theme-accent);
            background: var(--theme-badge-bg);
            box-shadow: 0 0 14px rgba(var(--theme-glow-rgb), 0.35);
        }}

        /* GRAPH CANVAS WRAPPER */
        .synapse-graph-container {{
            position: relative;
            flex: 1;
            height: 100%;
            background: var(--theme-panel-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--theme-panel-border);
            border-radius: 16px;
            box-shadow: 0 0 30px rgba(var(--theme-glow-rgb), 0.12);
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
            font-size: 16px;
            font-weight: 800;
            letter-spacing: 0.04em;
            color: var(--theme-text-main);
            text-shadow: 0 0 10px rgba(var(--theme-glow-rgb), 0.4);
        }}
        .graph-subtitle {{
            font-size: 11.5px;
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
            backdrop-filter: blur(14px);
            padding: 4px 8px;
            border-radius: 12px;
            border: 1px solid var(--theme-panel-border);
        }}
        .hud-mini-btn {{
            background: var(--theme-panel-bg);
            border: 1px solid var(--theme-panel-border);
            color: var(--theme-text-main);
            padding: 5px 9px;
            border-radius: 8px;
            font-size: 11.5px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.18s ease;
            white-space: nowrap;
        }}
        .hud-mini-btn:hover {{
            border-color: var(--theme-accent);
            color: #FFFFFF;
            box-shadow: 0 0 10px rgba(var(--theme-glow-rgb), 0.3);
            transform: translateY(-1px);
        }}
        .hud-mini-btn.active {{
            background: var(--theme-accent);
            border-color: var(--theme-accent);
            color: #040914;
            font-weight: 800;
            box-shadow: 0 0 12px var(--theme-glow);
        }}

        /* CHÚ THÍCH NHANH GÓC DƯỚI TRÁI CANVAS */
        .graph-bottom-legend {{
            position: absolute;
            bottom: 12px;
            left: 16px;
            z-index: 50;
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(var(--theme-glow-rgb), 0.06);
            backdrop-filter: blur(12px);
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid var(--theme-panel-border);
            font-size: 11px;
            font-weight: 600;
        }}
        .legend-indicator {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .ind-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}

        /* 3. BOTTOM EXPANDABLE PANELS DECK (RELATED PAPERS + SELECTED DETAILS) */
        .synapse-bottom-deck {{
            display: grid;
            grid-template-columns: 1fr 1.25fr;
            gap: 10px;
            height: 220px;
            min-height: 180px;
            max-height: 38vh;
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
            box-shadow: 0 0 20px rgba(var(--theme-glow-rgb), 0.10);
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

        /* RESPONSIVE ON MOBILE */
        @media (max-width: 900px) {{
            .synapse-bottom-deck {{
                grid-template-columns: 1fr;
                height: auto;
                max-height: 48vh;
            }}
            .synapse-header-bar {{
                padding: 6px 12px;
            }}
            .header-meta-cluster {{
                display: none;
            }}
            .details-grid {{
                grid-template-columns: 1fr;
            }}
            .synapse-vertical-dock {{
                display: none;
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
                <span>👤 USER:</span>
                <b>Scholar Pro</b>
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
        <!-- SLIM VERTICAL DOCK -->
        <nav class="synapse-vertical-dock">
            <div class="dock-btn-group">
                <button class="dock-icon-btn active" id="dockBtnForce" onclick="switchLayoutMode('force')" title="1. Mạng Cụm (VOSviewer)">🕸️</button>
                <button class="dock-icon-btn" id="dockBtnTimeline" onclick="switchLayoutMode('timeline')" title="2. Dòng Thời Gian (HistCite)">⏳</button>
                <button class="dock-icon-btn" id="dockBtnConcentric" onclick="switchLayoutMode('concentric')" title="3. Kim Cương 2 Chiều (Diamond)">💎</button>
                <button class="dock-icon-btn" id="dockBtnHierarchical" onclick="switchLayoutMode('hierarchical')" title="4. Cây Phả Hệ (CiteSpace)">🌳</button>
                <button class="dock-icon-btn" id="dockBtnQuartile" onclick="switchLayoutMode('quartile')" title="5. Phân Làn Scopus Q1/Q2">📊</button>
            </div>
            
            <div class="dock-btn-group">
                <button class="dock-icon-btn active" id="dockBtnTrace" onclick="toggleLineageMode()" title="🧬 Bật/Tắt Truy Vết Phả Hệ">🧬</button>
                <button class="dock-icon-btn" onclick="cycleThemes()" title="🎨 Chuyển đổi 5 Mẫu Theme Kính Dạ Quang">🎨</button>
                <button class="dock-icon-btn" onclick="fitView()" title="🎯 Căn giữa toàn cảnh">🎯</button>
            </div>
        </nav>

        <!-- GRAPH CANVAS -->
        <div class="synapse-graph-container">
            <div class="graph-overlay-header">
                <div class="graph-title">Global Citation Knowledge Network</div>
                <div class="graph-subtitle">Project: {short_project_name}</div>
            </div>

            <!-- TOP RIGHT MINI CONTROLS -->
            <div class="graph-top-tools">
                <input type="text" id="nodeSearchInput" placeholder="🔍 Tìm kiếm bài báo..." oninput="searchAndFocusNode(this.value)" style="background:rgba(0,0,0,0.4); border:1px solid var(--theme-panel-border); color:#FFFFFF; border-radius:6px; padding:4px 8px; font-size:11px; outline:none; width:130px;">
                
                <select id="edgeFilter" onchange="applyGraphFilters()" style="background:var(--theme-panel-bg); border:1px solid var(--theme-panel-border); color:var(--theme-text-main); border-radius:8px; padding:4px 7px; font-size:11px; font-weight:600; outline:none; cursor:pointer;" title="Lọc loại liên kết mũi tên">
                    <option value="all">⚡ Tất cả mũi tên</option>
                    <option value="direct">🔷 Kế thừa 1 chiều</option>
                    <option value="mutual">🔶 Đối thoại 2 chiều</option>
                    <option value="cross_bridge">🔮 Bắc cầu xuyên tầng</option>
                    <option value="intra_layer">🟢 Cùng phân tầng</option>
                </select>

                <select id="layerFilter" onchange="applyGraphFilters()" style="background:var(--theme-panel-bg); border:1px solid var(--theme-panel-border); color:var(--theme-text-main); border-radius:8px; padding:4px 7px; font-size:11px; font-weight:600; outline:none; cursor:pointer;" title="Lọc phân tầng tri thức">
                    <option value="all">🌐 Toàn bộ tầng</option>
                    <option value="seed">★ F0 Bài gốc</option>
                    <option value="backward">🏛️ R1-R3 Cội nguồn</option>
                    <option value="forward">🚀 F1-F3 Kế thừa</option>
                </select>

                <button class="hud-mini-btn active" id="lineageBtn" onclick="toggleLineageMode()" title="Bật/Tắt chế độ truy vết phả hệ">🧬 Truy Vết</button>
                <button class="hud-mini-btn active" id="labelModeBtn" onclick="cycleLabelMode()" title="Chuyển kiểu nhãn">🏷️ Nhãn</button>
                <button class="hud-mini-btn active" id="pulseBtn" onclick="togglePulseGlow()" title="Bật/Tắt Nhịp thở">💓 Nhịp Thở</button>
                <button class="hud-mini-btn active" id="particlesBtn" onclick="toggleParticles()" title="Bật/Tắt Dòng Photon">✨ Photon</button>
                <button class="hud-mini-btn" id="timeplayBtn" onclick="toggleTimelinePlayback()" title="Tua Lịch Sử">⏯️ Tua</button>
                <button class="hud-mini-btn" onclick="zoomIn()" title="Phóng to">🔍+</button>
                <button class="hud-mini-btn" onclick="zoomOut()" title="Thu nhỏ">🔍-</button>
                <button class="hud-mini-btn" onclick="toggleFullScreen()" title="Toàn màn hình">⛶</button>
            </div>

            <!-- BOTTOM LEFT FAST LEGEND -->
            <div class="graph-bottom-legend">
                <div class="legend-indicator"><span class="ind-dot" style="background:#EA4335; box-shadow:0 0 6px #EA4335;"></span> <span>F0 Tâm điểm</span></div>
                <div class="legend-indicator"><span class="ind-dot" style="background:#7C3AED; box-shadow:0 0 6px #7C3AED;"></span> <span>Nền tảng (R1-R3)</span></div>
                <div class="legend-indicator"><span class="ind-dot" style="background:#0284C7; box-shadow:0 0 6px #0284C7;"></span> <span>Kế thừa (F1-F3)</span></div>
                <div class="legend-indicator" style="color:var(--theme-accent);">✨ <span>60 FPS Photon Stream</span></div>
            </div>

            <!-- TIMELINE PLAYBACK BAR (NỔI KHI BẬT) -->
            <div id="timelinePlaybackBar" style="display:none; position:absolute; bottom:14px; right:16px; z-index:70; background:var(--theme-panel-bg); border:1.5px solid var(--theme-accent); border-radius:12px; padding:6px 12px; align-items:center; gap:8px; box-shadow:0 0 16px rgba(var(--theme-glow-rgb), 0.3);">
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
    var container = document.getElementById('network-container');
    var data = {{ nodes: nodes, edges: edges }};

    var isPhysicsOn = true;
    var isParticlesOn = true;
    var isPulsingOn = true;
    var isLineageTracingOn = false;
    var isTimelinePlaybackActive = false;
    var isPlaybackPlaying = false;
    var playbackTimer = null;
    var playbackIntervalMs = 1200;
    var currentPlaybackYear = maxYrVal;
    var selectedLineageNodeId = null;
    var currentLayoutMode = 'force';
    var currentLabelMode = 'short';
    var currentThemeIndex = 0;
    var themesList = ['theme-synapse-cyan', 'theme-nebula-violet', 'theme-emerald-matrix', 'theme-solar-amber', 'theme-nordic-light'];

    var forceOptions = {{
        nodes: {{
            shadow: {{
                enabled: true,
                color: 'rgba(0,0,0,0.5)',
                size: 8,
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
        // Highlight row
        var allRows = document.querySelectorAll('.related-row');
        allRows.forEach(function(r) {{ r.classList.remove('selected'); }});
        var activeRow = document.getElementById('rel_row_' + nodeId);
        if (activeRow) {{
            activeRow.classList.add('selected');
            activeRow.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
        }}

        // Focus in Network
        network.selectNodes([nodeId]);
        network.focus(nodeId, {{
            scale: 1.35,
            animation: {{ duration: 350, easingFunction: 'easeInOutQuad' }}
        }});

        // Update Right Pane (Selected Details)
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

    // Cycle 5 Hologram Themes
    function cycleThemes() {{
        currentThemeIndex = (currentThemeIndex + 1) % themesList.length;
        var nextTheme = themesList[currentThemeIndex];
        document.body.className = nextTheme;
    }}

    // Network Click Event
    network.on('click', function(params) {{
        if (params.nodes.length > 0) {{
            var nodeId = params.nodes[0];
            selectPaperFromTable(nodeId);
        }} else {{
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
        var elem = document.documentElement;
        if (!document.fullscreenElement) {{
            if (elem.requestFullscreen) elem.requestFullscreen();
        }} else {{
            if (document.exitFullscreen) document.exitFullscreen();
        }}
    }}

    // Toggle Particle Photons & Pulsing Glow
    function toggleParticles() {{
        isParticlesOn = !isParticlesOn;
        var btn = document.getElementById('particlesBtn');
        if (btn) btn.className = isParticlesOn ? 'hud-mini-btn active' : 'hud-mini-btn';
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

    // Dynamic Graph Filtering (Edge & Layer Filters)
    function applyGraphFilters() {{
        var edgeEl = document.getElementById('edgeFilter');
        var layerEl = document.getElementById('layerFilter');
        var edgeVal = edgeEl ? edgeEl.value : 'all';
        var layerVal = layerEl ? layerEl.value : 'all';

        var visibleNodeIds = new Set();
        var nodeUpdates = [];

        rawNodes.forEach(function(n) {{
            var matchLayer = true;
            if (layerVal === 'seed') matchLayer = (n.level === 0 || n.layer === 'seed');
            else if (layerVal === 'backward') matchLayer = (n.level < 0 || n.layer === 'backward');
            else if (layerVal === 'forward') matchLayer = (n.level > 0 || n.layer === 'forward');

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

    // Switch Layout Modes
    function switchLayoutMode(mode) {{
        currentLayoutMode = mode;
        ['dockBtnForce', 'dockBtnTimeline', 'dockBtnConcentric', 'dockBtnHierarchical', 'dockBtnQuartile'].forEach(function(id) {{
            var b = document.getElementById(id);
            if (b) b.classList.remove('active');
        }});

        if (mode === 'timeline') {{
            var db = document.getElementById('dockBtnTimeline');
            if (db) db.classList.add('active');
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
                var yOffset = (indexInYear - (totalInYear - 1) / 2) * 95;
                updates.push({{ id: n.id, x: n.x_timeline, y: yOffset, physics: false }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 200);

        }} else if (mode === 'concentric') {{
            var db = document.getElementById('dockBtnConcentric');
            if (db) db.classList.add('active');
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
            setTimeout(fitView, 200);

        }} else if (mode === 'hierarchical') {{
            var db = document.getElementById('dockBtnHierarchical');
            if (db) db.classList.add('active');
            var updates = [];
            rawNodes.forEach(function(n) {{ updates.push({{ id: n.id, physics: true }}); }});
            nodes.update(updates);

            network.setOptions({{
                layout: {{ hierarchical: {{ enabled: true, direction: 'UD', sortMethod: 'directed', levelSeparation: 150, nodeSpacing: 180 }} }},
                physics: {{ hierarchicalRepulsion: {{ nodeDistance: 170 }}, solver: 'hierarchicalRepulsion' }}
            }});
            setTimeout(fitView, 350);

        }} else if (mode === 'quartile') {{
            var db = document.getElementById('dockBtnQuartile');
            if (db) db.classList.add('active');
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
                    var yOffset = (idx - (list.length - 1) / 2) * 95;
                    updates.push({{ id: id, x: laneX[k], y: yOffset, physics: false }});
                }});
            }});
            nodes.update(updates);
            setTimeout(fitView, 200);

        }} else {{
            var db = document.getElementById('dockBtnForce');
            if (db) db.classList.add('active');
            network.setOptions({{ layout: {{ hierarchical: false }} }});
            var updates = [];
            rawNodes.forEach(function(n) {{ updates.push({{ id: n.id, physics: true }}); }});
            nodes.update(updates);
            network.setOptions(forceOptions);
            setTimeout(fitView, 200);
        }}
    }}

    // Concentric & Timeline Guides
    network.on('beforeDrawing', function(ctx) {{
        if (currentLayoutMode === 'concentric') {{
            ctx.save();
            ctx.setLineDash([8, 8]);
            ctx.lineWidth = 1.5;
            ctx.strokeStyle = 'rgba(124, 58, 237, 0.25)';
            ctx.beginPath();
            ctx.arc(0, 0, 240, Math.PI / 2, Math.PI * 1.5, false);
            ctx.stroke();

            ctx.strokeStyle = 'rgba(2, 132, 199, 0.25)';
            ctx.beginPath();
            ctx.arc(0, 0, 260, -Math.PI / 2, Math.PI / 2, false);
            ctx.stroke();

            ctx.font = 'bold 12px Plus Jakarta Sans, sans-serif';
            ctx.fillStyle = 'rgba(196, 181, 253, 0.7)';
            ctx.fillText('🏛️ CỘI NGUỒN LÝ THUYẾT (R)', -340, -280);
            ctx.fillStyle = 'rgba(56, 189, 248, 0.7)';
            ctx.fillText('🚀 BƯỚC TIẾN KẾ THỪA (F)', 150, -300);
            ctx.restore();
        }} else if (currentLayoutMode === 'timeline') {{
            ctx.save();
            for (var y = minYrVal; y <= maxYrVal; y++) {{
                var xPos = (y - minYrVal) * 260 - ((maxYrVal - minYrVal) * 130);
                ctx.setLineDash([6, 6]);
                ctx.lineWidth = 1.0;
                ctx.strokeStyle = 'rgba(0, 242, 254, 0.18)';
                ctx.beginPath();
                ctx.moveTo(xPos, -420);
                ctx.lineTo(xPos, 420);
                ctx.stroke();

                ctx.setLineDash([]);
                ctx.fillStyle = 'rgba(6, 14, 28, 0.85)';
                ctx.fillRect(xPos - 44, -435, 88, 24);
                ctx.strokeStyle = '#00F2FE';
                ctx.strokeRect(xPos - 44, -435, 88, 24);

                ctx.font = 'bold 11px JetBrains Mono, monospace';
                ctx.fillStyle = '#FDE047';
                ctx.textAlign = 'center';
                ctx.fillText('📅 ' + y, xPos, -419);
            }}
            ctx.restore();
        }}
    }});

    // Particles & Pulsing Halos (afterDrawing)
    network.on('afterDrawing', function(ctx) {{
        var now = Date.now();
        var positions = network.getPositions();

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
                        grad.addColorStop(0, 'rgba(0, 242, 254, ' + (0.45 + pulse * 0.25) + ')');
                        grad.addColorStop(1, 'rgba(0, 242, 254, 0)');
                    }}
                    ctx.beginPath();
                    ctx.arc(pos.x, pos.y, haloR, 0, 2 * Math.PI, false);
                    ctx.fillStyle = grad;
                    ctx.fill();
                    ctx.restore();
                }}
            }});
        }}

        if (isParticlesOn) {{
            var tNow = now / 1100;
            rawEdges.forEach(function(e, idx) {{
                var p1 = positions[e.from];
                var p2 = positions[e.to];
                if (!p1 || !p2) return;

                var currentEdge = edges.get(e.id);
                if (currentEdge && currentEdge.hidden) return;

                var t = (tNow + (idx * 0.19)) % 1.0;
                var x = p1.x + (p2.x - p1.x) * t;
                var y = p1.y + (p2.y - p1.y) * t;

                ctx.save();
                ctx.beginPath();
                ctx.arc(x, y, 3.2, 0, 2 * Math.PI, false);
                ctx.fillStyle = '#00F2FE';
                ctx.shadowColor = '#00F2FE';
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.restore();
            }});
        }}
    }});

    function dynamicAnimationLoop() {{
        if (isParticlesOn || isPulsingOn) network.redraw();
        requestAnimationFrame(dynamicAnimationLoop);
    }}
    requestAnimationFrame(dynamicAnimationLoop);

    function searchAndFocusNode(q) {{
        if (!q || q.trim() === '') return;
        var query = q.toLowerCase().trim();
        var foundId = null;
        rawNodes.forEach(function(n) {{
            var lbl = (n.label_full || n.label || '').toLowerCase();
            if (lbl.indexOf(query) !== -1) foundId = n.id;
        }});
        if (foundId) selectPaperFromTable(foundId);
    }}

    // Auto-select primary seed on initial load
    setTimeout(function() {{
        if (rawNodes.length > 0) {{
            selectPaperFromTable(rawNodes[0].id);
        }}
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
