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
        backward_limit: int = 15,
        forward_limit: int = 25,
        max_depth: int = 2,
        gen1_limit: Optional[int] = None,
        gen2_limit: Optional[int] = None,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Execute CiteNet pipeline with Bidirectional Diamond Knowledge Graph.
        """
        # Hỗ trợ backward-compatibility nếu người dùng truyền gen1_limit / gen2_limit cũ
        if forward_limit is None and gen1_limit is not None:
            forward_limit = gen1_limit
            
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
            
            # Nhãn học thuật kèm trực tiếp số lượt trích dẫn & phân loại tầng
            if level == 0 or layer == "seed":
                short_label = f"★ {first_auth} ({year})\n[F0 • {cites} trích dẫn]"
            elif level < 0 or layer == "backward":
                r_tag = f"R{abs(level)}" if level != 0 else "R"
                if is_isolated:
                    short_label = f"⚡ {first_auth} ({year})\n[{r_tag} • {cites} tc • Độc lập]"
                else:
                    short_label = f"🏛️ {first_auth} ({year})\n[{r_tag} • {cites} trích dẫn]"
            else:
                f_tag = f"F{level}" if level != 0 else "F"
                if is_isolated:
                    short_label = f"⚡ {first_auth} ({year})\n[{f_tag} • {cites} tc • Độc lập]"
                else:
                    short_label = f"🚀 {first_auth} ({year})\n[{f_tag} • {cites} trích dẫn]"

            # Tính tọa độ timeline ban đầu
            try:
                yr_int = int(year)
            except Exception:
                yr_int = min_yr
            x_timeline = (yr_int - min_yr) * 240 - ((max_yr - min_yr) * 120)
            
            is_seed = (level == 0 or layer == "seed")
            node_item = {
                "id": node_id,
                "label": short_label,
                "value": cites + 1,
                "size": node_size,
                "color": colors,
                "borderWidth": 3.5 if is_seed else (2.6 if is_isolated else 1.8),
                "shapeProperties": {"borderDashes": [4, 4]} if is_isolated else {"borderDashes": False},
                "font": {
                    "size": 12 if is_seed else 11,
                    "color": "#F8FAFC",
                    "face": "Plus Jakarta Sans, sans-serif",
                    "strokeWidth": 3,
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
            border-radius: 16px;
            border: 1px solid #262B38;
            overflow: hidden;
            transition: background 0.3s ease;
        }}
        /* Chế độ 1: Deep Obsidian vũ trụ mặc định */
        #network-wrapper.bg-obsidian {{
            background: radial-gradient(circle at center, #151822 0%, #0B0C0E 100%);
        }}
        /* Chế độ 2: Không gian Lưới 3D tương phản công nghệ (Cyber 3D Grid) */
        #network-wrapper.bg-3d-grid {{
            background-color: #06080F;
            background-image: 
                linear-gradient(rgba(56, 189, 248, 0.14) 1.5px, transparent 1.5px),
                linear-gradient(90deg, rgba(56, 189, 248, 0.14) 1.5px, transparent 1.5px),
                radial-gradient(circle at 50% 50%, rgba(37, 99, 235, 0.25) 0%, rgba(6, 8, 15, 0.96) 80%);
            background-size: 38px 38px, 38px 38px, 100% 100%;
            box-shadow: inset 0 0 100px rgba(6, 182, 212, 0.2);
        }}
        /* Chế độ 3: Bản vẽ Kỹ thuật Blueprint */
        #network-wrapper.bg-blueprint {{
            background-color: #0A192F;
            background-image: 
                linear-gradient(rgba(100, 255, 218, 0.15) 1px, transparent 1px),
                linear-gradient(90deg, rgba(100, 255, 218, 0.15) 1px, transparent 1px),
                linear-gradient(rgba(100, 255, 218, 0.05) 5px, transparent 5px),
                linear-gradient(90deg, rgba(100, 255, 218, 0.05) 5px, transparent 5px);
            background-size: 20px 20px, 20px 20px, 100px 100px, 100px 100px;
        }}
        /* Chế độ 4: Bản thảo Giấy da Ngà sáng (Parchment Ivory) */
        #network-wrapper.bg-parchment {{
            background-color: #F8F5EC;
            background-image: radial-gradient(#D3C7A1 1.2px, transparent 1.2px);
            background-size: 24px 24px;
        }}
        /* Chế độ 5: Bắc Âu Glacier xám sáng sạch (Nordic Slate Light) */
        #network-wrapper.bg-nordic-light {{
            background-color: #F1F5F9;
            background-image: 
                linear-gradient(rgba(203, 213, 225, 0.6) 1px, transparent 1px),
                linear-gradient(90deg, rgba(203, 213, 225, 0.6) 1px, transparent 1px);
            background-size: 32px 32px;
        }}

        #network-container {{
            width: 100%;
            height: 100%;
        }}
        
        /* Floating Collapsible Control HUD Toolbar (Mặc định thu gọn) */
        .hud-controls-drawer {{
            position: absolute;
            top: 14px;
            left: 14px;
            z-index: 100;
            background: rgba(18, 20, 26, 0.95);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid #262B38;
            border-radius: 14px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
            max-width: calc(100% - 28px);
            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
        }}
        .hud-toggle-btn {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            background: transparent;
            border: none;
            color: #F8FAFC;
            font-family: inherit;
            font-size: 12px;
            font-weight: 800;
            padding: 8px 14px;
            cursor: pointer;
            outline: none;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .hud-toggle-btn:hover {{
            color: #38BDF8;
            background: rgba(56, 189, 248, 0.08);
        }}
        .hud-content-panel {{
            display: none;
            padding: 10px 14px 12px 14px;
            border-top: 1px solid rgba(255,255,255,0.08);
            flex-direction: column;
            gap: 8px;
        }}
        .hud-controls-drawer.is-open .hud-content-panel {{
            display: flex !important;
        }}
        .hud-btn-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            align-items: center;
        }}
        .hud-btn {{
            background: #181B24;
            border: 1px solid #262B38;
            color: #F8FAFC;
            padding: 6px 11px;
            border-radius: 8px;
            font-size: 12px;
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
            font-size: 12px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .hud-search-box:focus {{
            border-color: #38BDF8;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
        }}
        
        /* Chú thích bên trái - Mặc định ẩn triệt để 100% (Strictly Collapsed Left Legend) */
        .hud-legend-drawer {{
            position: absolute;
            bottom: 14px;
            left: 14px;
            z-index: 95;
            background: rgba(18, 20, 26, 0.94);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid #262B38;
            border-radius: 12px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.5);
            font-size: 11.5px;
            font-weight: 600;
            color: #F8FAFC;
            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            max-width: 340px;
        }}
        .legend-toggle-btn {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            background: transparent;
            border: none;
            color: #38BDF8;
            font-family: inherit;
            font-size: 11.5px;
            font-weight: 700;
            padding: 8px 12px;
            cursor: pointer;
            width: 100%;
            text-align: left;
            outline: none;
            transition: color 0.15s ease;
        }}
        .legend-toggle-btn:hover {{
            color: #FFFFFF;
            background: rgba(255,255,255,0.04);
        }}
        .legend-content-panel {{
            display: none;
            padding: 8px 12px 10px 12px;
            border-top: 1px solid rgba(255,255,255,0.08);
            flex-direction: column;
            gap: 6px;
        }}
        .hud-legend-drawer.is-open .legend-content-panel {{
            display: flex !important;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            line-height: 1.4;
        }}
        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
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
        .badge-r1 {{ background: rgba(124, 58, 237, 0.2); color: #C4B5FD; border: 1px solid rgba(124, 58, 237, 0.4); }}
        .badge-r2 {{ background: rgba(99, 102, 241, 0.2); color: #A5B4FC; border: 1px solid rgba(99, 102, 241, 0.4); }}
        .badge-f1 {{ background: rgba(2, 132, 199, 0.2); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4); }}
        .badge-f2 {{ background: rgba(5, 150, 105, 0.2); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4); }}
        .badge-f3 {{ background: rgba(217, 119, 6, 0.2); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.4); }}
        
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
            .hud-controls-drawer {{
                top: 8px;
                left: 8px;
                max-width: calc(100% - 16px);
            }}
            .hud-toggle-btn {{
                padding: 7px 12px;
                font-size: 11.5px;
            }}
            .hud-btn {{
                padding: 5px 9px;
                font-size: 11px;
            }}
        }}

        @media (max-width: 768px) {{
            .hud-controls-drawer {{
                top: 6px;
                left: 6px;
                right: 6px;
                max-width: calc(100% - 12px);
                border-radius: 12px;
            }}
            .hud-toggle-btn {{
                padding: 7px 12px;
                font-size: 11px;
                width: 100%;
            }}
            .hud-content-panel {{
                padding: 8px 10px 10px 10px;
                max-height: 52vh;
                overflow-y: auto;
                -webkit-overflow-scrolling: touch;
            }}
            .hud-btn {{
                padding: 5px 8px;
                font-size: 10.5px;
                flex: 1 1 auto;
                justify-content: center;
                min-height: 34px;
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
                max-height: 85vh !important;
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
            .action-link-btn {{
                min-height: 38px;
                padding: 8px 14px;
            }}
        }}
    </style>
</head>
<body>
<div id="network-wrapper" class="bg-obsidian">
    <!-- Floating Collapsible Control HUD Toolbar (Mặc định thu gọn) -->
    <div id="hud-controls-drawer" class="hud-controls-drawer">
        <button id="hudToggleBtn" class="hud-toggle-btn" onclick="toggleHudDrawer()" title="Bấm để mở/thu gọn thanh công cụ (Phóng to, thu nhỏ, căn giữa, bố cục, nền 3D)">
            <span style="display:inline-flex; align-items:center; gap:6px;">
                <span>🎛️</span>
                <span>BẢNG CÔNG CỤ & BỐ CỤC</span>
            </span>
            <span id="hudArrowIcon" style="font-size:12px; color:#38BDF8; font-weight:800;">▸</span>
        </button>
        
        <div id="hudContentPanel" class="hud-content-panel" style="display: none;">
            <!-- Search Box -->
            <input type="text" id="nodeSearch" class="hud-search-box" style="width: 100%; box-sizing: border-box;" placeholder="🔍 Tìm tác giả / bài báo..." oninput="searchAndFocusNode(this.value)">
            
            <!-- Hàng 1: Phóng to, Thu nhỏ, Căn giữa, Physics, Hạt sáng, Nhịp thở, Tua lịch sử, Truy vết, Toàn màn hình -->
            <div class="hud-btn-row">
                <button class="hud-btn" onclick="zoomIn()" title="Phóng to mạng lưới">🔍+ Phóng to</button>
                <button class="hud-btn" onclick="zoomOut()" title="Thu nhỏ mạng lưới">🔍- Thu nhỏ</button>
                <button class="hud-btn" onclick="fitView()" title="Căn giữa toàn cảnh">🎯 Căn giữa</button>
                <button class="hud-btn" id="physicsBtn" onclick="togglePhysics()" title="Bật/Tắt mô phỏng vật lý">⚡ Tự sắp xếp</button>
                <button class="hud-btn active" id="particlesBtn" onclick="toggleParticles()" title="Bật/Tắt luồng hạt photon chuyển động dọc theo mũi tên trích dẫn">✨ Hạt Sáng</button>
                <button class="hud-btn active" id="pulseBtn" onclick="togglePulseGlow()" title="Bật/Tắt vầng hào quang nhịp thở tỏa sáng quanh bài báo gốc & điểm bùng nổ">💓 Nhịp Thở</button>
                <button class="hud-btn" id="timeplayBtn" onclick="toggleTimelinePlayback()" title="Tua lại lịch sử hình thành & tiến hóa tri thức qua các năm">⏯️ Tua Lịch Sử</button>
                <button class="hud-btn" id="lineageBtn" onclick="toggleLineageMode()" title="Bật/Tắt chế độ phát sáng chuỗi phả hệ cội nguồn khi chọn bài báo">🧬 Truy Vết</button>
                <button class="hud-btn" onclick="toggleFullScreen()" title="Phóng to toàn màn hình">⛶ Toàn màn hình</button>
                <button class="hud-btn primary" onclick="popoutWindow()" title="Mở trong cửa sổ riêng để kéo sang màn hình phụ">🪟 Màn hình phụ</button>
            </div>
            
            <!-- Hàng 2: 5 Chế độ bố cục Scientometric -->
            <div class="hud-btn-row">
                <button class="hud-btn active" id="btnModeForce" onclick="switchLayoutMode('force')" title="1. Chuẩn VOSviewer: Cụm lực hút đồng trích dẫn">🕸️ Mạng Cụm</button>
                <button class="hud-btn" id="btnModeTimeline" onclick="switchLayoutMode('timeline')" title="2. Chuẩn HistCite: Dòng thời gian tiến hóa học thuật">⏳ Dòng Thời gian</button>
                <button class="hud-btn" id="btnModeConcentric" onclick="switchLayoutMode('concentric')" title="3. Chuẩn Kim Cương: Quỹ đạo Nền tảng (R) - Kế thừa (F)">💎 Kim Cương 2 Chiều</button>
                <button class="hud-btn" id="btnModeHierarchical" onclick="switchLayoutMode('hierarchical')" title="4. Chuẩn CiteSpace: Cây phả hệ phân tầng">🌳 Cây Phả hệ</button>
                <button class="hud-btn" id="btnModeQuartile" onclick="switchLayoutMode('quartile')" title="5. Chuẩn Clarivate: Phân làn Scopus Q1/Q2">📊 Phân làn Scopus</button>
            </div>
            
            <!-- Hàng 3: Chọn kiểu nền & Không gian 3D -->
            <div class="hud-btn-row" style="margin-top:2px;">
                <select id="bgSelector" class="hud-search-box" onchange="switchCanvasBg(this.value)" style="width:100%; cursor:pointer; font-weight:700; background:#181B24; border-color:#38BDF8; color:#38BDF8;" title="Chọn kiểu nền hiển thị & không gian 3D tương phản cao">
                    <option value="obsidian">🌌 Nền: Vũ trụ Obsidian (Mặc định)</option>
                    <option value="3d-grid">🧊 Nền: Không gian Lưới 3D (Cyber 3D)</option>
                    <option value="blueprint">📐 Nền: Bản vẽ Blueprint</option>
                    <option value="parchment">📜 Nền: Giấy da Ivory (Sáng)</option>
                    <option value="nordic-light">🏛️ Nền: Bắc Âu Slate (Sáng)</option>
                </select>
            </div>

            <!-- Hàng 4: Bộ lọc Phân tầng Kim Cương, Quyền truy cập & Phân loại Mũi tên -->
            <div class="hud-btn-row" style="margin-top:2px; display:grid; grid-template-columns: 1fr 1fr 1fr; gap:6px;">
                <select id="layerFilter" class="hud-search-box" onchange="applyGraphFilters()" style="width:100%; cursor:pointer; font-weight:600; background:#181B24; border-color:#262B38; color:#F8FAFC;" title="Lọc theo tầng tri thức">
                    <option value="all">🌐 Tầng: Tất cả (Diamond)</option>
                    <option value="seed">🔴 Chỉ Bài Gốc (F0)</option>
                    <option value="backward">🟣 Chỉ Nền Tảng (R1-R3)</option>
                    <option value="forward">🟢 Chỉ Kế Thừa (F1-F3)</option>
                </select>
                <select id="accessFilter" class="hud-search-box" onchange="applyGraphFilters()" style="width:100%; cursor:pointer; font-weight:600; background:#181B24; border-color:#262B38; color:#F8FAFC;" title="Lọc theo quyền truy cập">
                    <option value="all">🔓 Quyền: Tất cả bài báo</option>
                    <option value="oa">🔓 Chỉ Open Access (PDF)</option>
                    <option value="paywall">🔒 Chỉ Bài Paywall</option>
                </select>
                <select id="edgeFilter" class="hud-search-box" onchange="applyGraphFilters()" style="width:100%; cursor:pointer; font-weight:600; background:#181B24; border-color:#38BDF8; color:#38BDF8;" title="Lọc theo kiểu mũi tên dòng chảy tri thức">
                    <option value="all">🔗 Mũi tên: Tất cả (4 loại)</option>
                    <option value="direct">🔷 Chỉ Kế thừa 1 chiều</option>
                    <option value="mutual">🔶 Chỉ Đối thoại 2 chiều</option>
                    <option value="cross_bridge">🔮 Chỉ Bắc cầu xuyên tầng</option>
                    <option value="intra_layer">🟢 Chỉ Cùng phân tầng</option>
                </select>
            </div>

            <!-- Hàng 5: Thanh điều khiển Tua lại Lịch sử Tiến hóa (Timeline Evolution Playback Bar) -->
            <div id="timelinePlaybackBar" class="hud-btn-row" style="display:none; margin-top:4px; background:rgba(20,23,32,0.96); border:1px solid #38BDF8; border-radius:10px; padding:6px 12px; align-items:center; gap:8px;">
                <button id="playbackPlayBtn" class="hud-btn active" onclick="togglePlaybackPlay()" style="min-width:68px; font-weight:800;">▶️ Phát</button>
                <span style="font-size:11px; color:#38BDF8; font-weight:700; white-space:nowrap;">NĂM: <b id="playbackYearLabel" style="color:#FDE047; font-size:12.5px;">{max_yr}</b></span>
                <input type="range" id="playbackYearSlider" min="{min_yr}" max="{max_yr}" value="{max_yr}" step="1" oninput="onPlaybackSliderChange(this.value)" style="flex:1; cursor:pointer;">
                <button class="hud-btn" onclick="resetPlayback()" style="font-size:10.5px;">↺ Đặt lại</button>
            </div>
        </div>
    </div>

    <!-- Floating Hover Info Card -->
    <div id="floating-hover-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div id="hover-badge" style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em;"></div>
            <div id="hover-conn-badge" style="font-size:11px; font-weight:600;"></div>
        </div>
        <!-- Thông báo lý do bài báo đứng lẻ loi (chỉ hiện khi 0 liên kết) -->
        <div id="hover-orphan-notice" style="display:none; background:rgba(245, 158, 11, 0.16); border:1px solid rgba(245, 158, 11, 0.55); border-radius:8px; padding:7px 10px; margin-bottom:8px; font-size:11.5px; color:#FCD34D; line-height:1.45;">
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

    <!-- Chú thích Kim Cương Tri Thức & Phân Loại Mũi Tên (Left Collapsible Legend) -->
    <div id="hud-legend-wrapper" class="hud-legend-drawer">
        <button id="legendToggleBtn" class="legend-toggle-btn" onclick="toggleLegendDrawer()" title="Bấm để mở rộng / thu gọn chú giải">
            <span>📖 Chú thích Kim Cương & Mũi Tên Tri Thức</span>
            <span id="legendArrowIcon">▸</span>
        </button>
        <div id="legendContentPanel" class="legend-content-panel" style="display: none;">
            <div style="font-size:11px; font-weight:700; color:#38BDF8; margin-bottom:4px; text-transform:uppercase;">🏛️ Phân Tầng Nút Bài Báo (Nodes):</div>
            <div class="legend-item"><span class="legend-dot" style="background:#EA4335;"></span> <b>Bài báo gốc (F0):</b> Tâm điểm nghiên cứu (💓 Nhịp thở)</div>
            <div class="legend-item"><span class="legend-dot" style="background:#7C3AED;"></span> <b>Nền tảng (R1-R3):</b> Tham chiếu cội nguồn lý thuyết</div>
            <div class="legend-item"><span class="legend-dot" style="background:#0284C7;"></span> <b>Kế thừa (F1-F3):</b> Trích dẫn & phát triển tương lai</div>
            
            <div style="font-size:11px; font-weight:700; color:#F59E0B; margin:8px 0 4px 0; text-transform:uppercase; border-top:1px solid rgba(255,255,255,0.08); padding-top:6px;">🔗 Dòng Chảy & Mũi Tên Liên Kết (Edges):</div>
            <div class="legend-item"><span style="color:#38BDF8; font-weight:bold; font-size:13px;">—➔</span> <span style="color:#38BDF8; font-weight:700;">Kế thừa 1 chiều:</span> Dòng kế thừa trực tiếp</div>
            <div class="legend-item"><span style="color:#F59E0B; font-weight:bold; font-size:13px;">⟷</span> <span style="color:#F59E0B; font-weight:700;">Đối thoại 2 chiều:</span> Trích dẫn chéo tương hỗ</div>
            <div class="legend-item"><span style="color:#C084FC; font-weight:bold; font-size:13px;">┄➔</span> <span style="color:#C084FC; font-weight:700;">Bắc cầu xuyên tầng:</span> Kế thừa neo cội nguồn</div>
            <div class="legend-item"><span style="color:#34D399; font-weight:bold; font-size:13px;">┈➔</span> <span style="color:#34D399; font-weight:700;">Cùng phân tầng:</span> Liên kết nội bộ thế hệ</div>
            <div class="legend-item" style="color:#FDE047; font-size:10.5px; margin-top:2px;">✨ <b>Hạt photon sáng:</b> Dòng chuyển động tri thức (60 FPS)</div>
        </div>
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
    var isParticlesOn = true;
    var isPulsingOn = true;
    var isLineageTracingOn = false;
    var isTimelinePlaybackActive = false;
    var isPlaybackPlaying = false;
    var playbackTimer = null;
    var currentPlaybackYear = maxYrVal;
    var selectedLineageNodeId = null;
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

    // Toggle Particle Photon Animation
    function toggleParticles() {{
        isParticlesOn = !isParticlesOn;
        var btn = document.getElementById('particlesBtn');
        if (btn) {{
            btn.className = isParticlesOn ? 'hud-btn active' : 'hud-btn';
            btn.innerHTML = isParticlesOn ? '✨ Hạt Sáng: Bật' : '✨ Hạt Sáng: Tắt';
        }}
        network.redraw();
    }}

    // Toggle Pulsing Halo Glow (Nhịp thở quanh hạt nhân)
    function togglePulseGlow() {{
        isPulsingOn = !isPulsingOn;
        var btn = document.getElementById('pulseBtn');
        if (btn) {{
            btn.className = isPulsingOn ? 'hud-btn active' : 'hud-btn';
            btn.innerHTML = isPulsingOn ? '💓 Nhịp Thở: Bật' : '💓 Nhịp Thở: Tắt';
        }}
        network.redraw();
    }}

    // Toggle Timeline Playback Mode
    function toggleTimelinePlayback() {{
        isTimelinePlaybackActive = !isTimelinePlaybackActive;
        var bar = document.getElementById('timelinePlaybackBar');
        var btn = document.getElementById('timeplayBtn');
        if (isTimelinePlaybackActive) {{
            if (bar) bar.style.display = 'flex';
            if (btn) {{ btn.className = 'hud-btn active'; btn.innerHTML = '⏯️ Đang Tua Lịch Sử'; }}
            currentPlaybackYear = minYrVal;
            applyTimelinePlaybackYear(currentPlaybackYear);
            startPlaybackTimer();
        }} else {{
            if (bar) bar.style.display = 'none';
            if (btn) {{ btn.className = 'hud-btn'; btn.innerHTML = '⏯️ Tua Lịch Sử'; }}
            stopPlaybackTimer();
            resetPlayback();
        }}
    }}

    function startPlaybackTimer() {{
        isPlaybackPlaying = true;
        var playBtn = document.getElementById('playbackPlayBtn');
        if (playBtn) playBtn.innerHTML = '⏸️ Tạm Dừng';
        if (playbackTimer) clearInterval(playbackTimer);
        playbackTimer = setInterval(function() {{
            if (currentPlaybackYear >= maxYrVal) {{
                stopPlaybackTimer();
                return;
            }}
            currentPlaybackYear += 1;
            applyTimelinePlaybackYear(currentPlaybackYear);
        }}, 1400);
    }}

    function stopPlaybackTimer() {{
        isPlaybackPlaying = false;
        var playBtn = document.getElementById('playbackPlayBtn');
        if (playBtn) playBtn.innerHTML = '▶️ Phát Tiếp';
        if (playbackTimer) {{
            clearInterval(playbackTimer);
            playbackTimer = null;
        }}
    }}

    function togglePlaybackPlay() {{
        if (isPlaybackPlaying) {{
            stopPlaybackTimer();
        }} else {{
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
            nodeUpdates.push({{
                id: n.id,
                hidden: !isVisible,
                opacity: isVisible ? 1.0 : 0.0
            }});
        }});
        nodes.update(nodeUpdates);

        var edgeUpdates = [];
        rawEdges.forEach(function(e) {{
            var edgeVisible = visibleNodeIds.has(e.from) && visibleNodeIds.has(e.to);
            edgeUpdates.push({{
                id: e.id,
                hidden: !edgeVisible
            }});
        }});
        edges.update(edgeUpdates);
    }}

    function resetPlayback() {{
        currentPlaybackYear = maxYrVal;
        applyTimelinePlaybackYear(maxYrVal);
        stopPlaybackTimer();
    }}

    // Toggle Interactive Lineage Tracing Mode
    function toggleLineageMode() {{
        isLineageTracingOn = !isLineageTracingOn;
        var btn = document.getElementById('lineageBtn');
        if (btn) {{
            btn.className = isLineageTracingOn ? 'hud-btn active' : 'hud-btn';
            btn.innerHTML = isLineageTracingOn ? '🧬 Truy Vết: Bật' : '🧬 Truy Vết: Tắt';
        }}
        if (!isLineageTracingOn) {{
            resetLineageHighlight();
        }} else if (selectedLineageNodeId) {{
            traceAncestryAndDescendants(selectedLineageNodeId);
        }}
    }}

    // 5 International Scientometric Layouts Switcher
    function switchLayoutMode(mode) {{
        currentLayoutMode = mode;
        var btnForce = document.getElementById('btnModeForce');
        var btnTimeline = document.getElementById('btnModeTimeline');
        var btnConcentric = document.getElementById('btnModeConcentric');
        var btnHierarchical = document.getElementById('btnModeHierarchical');
        var btnQuartile = document.getElementById('btnModeQuartile');

        [btnForce, btnTimeline, btnConcentric, btnHierarchical, btnQuartile].forEach(function(b) {{
            if (b) b.className = 'hud-btn';
        }});

        if (mode === 'timeline') {{
            if (btnTimeline) btnTimeline.className = 'hud-btn active';

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

            network.setOptions({{ physics: {{ enabled: false }}, layout: {{ hierarchical: false }} }});

            var updates = [];
            var seeds = rawNodes.filter(function(n) {{ return (n.level === 0 || n.layer === 'seed'); }});
            var backwardPapers = rawNodes.filter(function(n) {{ return (n.level < 0 || n.layer === 'backward'); }});
            var forwardPapers = rawNodes.filter(function(n) {{ return (n.level > 0 || n.layer === 'forward'); }});

            // Seed đặt ở tâm
            seeds.forEach(function(n, i) {{
                updates.push({{ id: n.id, x: (i * 80) - ((seeds.length - 1) * 40), y: 0, physics: false }});
            }});

            // Nền tảng (Backward - R) đặt bên cánh TRÁI (cung tròn 90 độ đến 270 độ)
            var bCount = backwardPapers.length || 1;
            backwardPapers.forEach(function(n, i) {{
                var lvl = Math.abs(n.level || 1);
                var radius = 240 + (lvl - 1) * 140;
                var angle = Math.PI / 2 + ((Math.PI * (i + 0.5)) / bCount);
                updates.push({{
                    id: n.id,
                    x: Math.round(radius * Math.cos(angle)),
                    y: Math.round(radius * Math.sin(angle)),
                    physics: false
                }});
            }});

            // Kế thừa (Forward - F) đặt bên cánh PHẢI (cung tròn -90 độ đến 90 độ)
            var fCount = forwardPapers.length || 1;
            forwardPapers.forEach(function(n, j) {{
                var lvl = Math.abs(n.level || 1);
                var radius = 260 + (lvl - 1) * 150;
                var angle = -Math.PI / 2 + ((Math.PI * (j + 0.5)) / fCount);
                updates.push({{
                    id: n.id,
                    x: Math.round(radius * Math.cos(angle)),
                    y: Math.round(radius * Math.sin(angle)),
                    physics: false
                }});
            }});

            nodes.update(updates);
            setTimeout(function() {{ fitView(); }}, 200);

        }} else if (mode === 'hierarchical') {{
            if (btnHierarchical) btnHierarchical.className = 'hud-btn active';

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
                if (p.level === 0 || p.layer === 'seed') {{
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

    // Concentric Orbit Celestial Rings (beforeDrawing)
    network.on('beforeDrawing', function(ctx) {{
        if (currentLayoutMode === 'concentric') {{
            ctx.save();
            ctx.setLineDash([8, 8]);
            ctx.lineWidth = 1.5;

            // Vòng quỹ đạo Nền tảng (Backward - R)
            ctx.strokeStyle = 'rgba(124, 58, 237, 0.25)';
            ctx.beginPath();
            ctx.arc(0, 0, 240, Math.PI / 2, Math.PI * 1.5, false);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(0, 0, 380, Math.PI / 2, Math.PI * 1.5, false);
            ctx.stroke();

            // Vòng quỹ đạo Kế thừa (Forward - F)
            ctx.strokeStyle = 'rgba(2, 132, 199, 0.25)';
            ctx.beginPath();
            ctx.arc(0, 0, 260, -Math.PI / 2, Math.PI / 2, false);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(0, 0, 410, -Math.PI / 2, Math.PI / 2, false);
            ctx.stroke();

            // Nhãn định hướng không gian
            ctx.font = 'bold 12px Plus Jakarta Sans, sans-serif';
            ctx.fillStyle = 'rgba(196, 181, 253, 0.7)';
            ctx.fillText('🏛️ CỘI NGUỒN LÝ THUYẾT (R1-R3)', -340, -280);

            ctx.fillStyle = 'rgba(56, 189, 248, 0.7)';
            ctx.fillText('🚀 BƯỚC TIẾN KẾ THỪA (F1-F3)', 150, -300);

            ctx.restore();
        }}
    }});

    // Dynamic Graph & Edge Filters
    function applyGraphFilters() {{
        var layerVal = document.getElementById('layerFilter') ? document.getElementById('layerFilter').value : 'all';
        var accessVal = document.getElementById('accessFilter') ? document.getElementById('accessFilter').value : 'all';
        var edgeVal = document.getElementById('edgeFilter') ? document.getElementById('edgeFilter').value : 'all';

        var nodeUpdates = [];
        var visibleNodeIds = new Set();

        rawNodes.forEach(function(n) {{
            var p = metaDict[n.id] || {{}};
            var isSeed = (n.level === 0 || n.layer === 'seed');
            var isBackward = (n.level < 0 || n.layer === 'backward');
            var isForward = (n.level > 0 || n.layer === 'forward');
            var isOa = !!p.is_oa || !!p.pdf_url;

            var matchLayer = true;
            if (layerVal === 'seed') matchLayer = isSeed;
            else if (layerVal === 'backward') matchLayer = isBackward;
            else if (layerVal === 'forward') matchLayer = isForward;

            var matchAccess = true;
            if (accessVal === 'oa') matchAccess = isOa;
            else if (accessVal === 'paywall') matchAccess = !isOa;

            var isVisible = (matchLayer && matchAccess);
            if (isVisible) visibleNodeIds.add(n.id);
            nodeUpdates.push({{
                id: n.id,
                hidden: !isVisible
            }});
        }});
        nodes.update(nodeUpdates);

        var edgeUpdates = [];
        rawEdges.forEach(function(e) {{
            var matchType = (edgeVal === 'all' || e.edge_type === edgeVal);
            var nodesVisible = visibleNodeIds.has(e.from) && visibleNodeIds.has(e.to);
            edgeUpdates.push({{
                id: e.id,
                hidden: !(matchType && nodesVisible)
            }});
        }});
        edges.update(edgeUpdates);
    }}

    // Lineage Tracing (Ancestry & Descendants)
    function traceAncestryAndDescendants(targetNodeId) {{
        selectedLineageNodeId = targetNodeId;
        var lineageNodes = new Set([targetNodeId]);
        var lineageEdges = new Set();

        // 1. Trace Ancestors (Backward via incoming edges)
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

        // 2. Trace Descendants (Forward via outgoing edges)
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

        // Update Nodes: Dim unrelated nodes, Highlight lineage
        var nodeUpdates = [];
        rawNodes.forEach(function(n) {{
            var inLineage = lineageNodes.has(n.id);
            var isTarget = (n.id === targetNodeId);
            nodeUpdates.push({{
                id: n.id,
                opacity: inLineage ? 1.0 : 0.18,
                borderWidth: isTarget ? 4.5 : (inLineage ? 3.0 : 1.0)
            }});
        }});
        nodes.update(nodeUpdates);

        // Update Edges: Dim unrelated edges, Brighten lineage
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
            nodeUpdates.push({{
                id: n.id,
                opacity: 1.0,
                borderWidth: isSeed ? 3.5 : (n.is_isolated ? 2.6 : 1.8)
            }});
        }});
        nodes.update(nodeUpdates);

        var edgeUpdates = [];
        rawEdges.forEach(function(e) {{
            edgeUpdates.push({{
                id: e.id,
                color: e.color,
                width: e.width
            }});
        }});
        edges.update(edgeUpdates);
    }}

    // Particle Photon Animation & Pulsing Node Halos Loop (afterDrawing)
    network.on('afterDrawing', function(ctx) {{
        var now = Date.now();
        var positions = network.getPositions();

        // 1. Vẽ Vầng Hào Quang Nhịp Thở (Pulsing Halo) cho Bài Gốc & Điểm Bùng Nổ
        if (isPulsingOn) {{
            var pulse = (Math.sin(now / 550) + 1) / 2; // 0.0 -> 1.0
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
                        grad.addColorStop(0.65, 'rgba(234, 67, 53, ' + (0.15 + pulse * 0.1) + ')');
                        grad.addColorStop(1, 'rgba(234, 67, 53, 0)');
                    }} else {{
                        grad.addColorStop(0, 'rgba(245, 158, 11, ' + (0.35 + pulse * 0.2) + ')');
                        grad.addColorStop(0.65, 'rgba(245, 158, 11, ' + (0.12 + pulse * 0.08) + ')');
                        grad.addColorStop(1, 'rgba(245, 158, 11, 0)');
                    }}

                    ctx.beginPath();
                    ctx.arc(pos.x, pos.y, haloR, 0, 2 * Math.PI, false);
                    ctx.fillStyle = grad;
                    ctx.fill();
                    ctx.restore();
                }}
            }});
        }}

        // 2. Vẽ Dòng Hạt Sáng Chuyển Động (Particle Flow)
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
                var radius = (e.edge_type === 'mutual') ? 3.6 : ((e.edge_type === 'cross_bridge') ? 3.0 : 2.5);
                ctx.arc(x, y, radius, 0, 2 * Math.PI, false);

                var pColor = '#38BDF8';
                if (e.edge_type === 'mutual') pColor = '#F59E0B';
                else if (e.edge_type === 'cross_bridge') pColor = '#C084FC';
                else if (e.edge_type === 'intra_layer') pColor = '#34D399';

                ctx.fillStyle = pColor;
                ctx.shadowColor = pColor;
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.restore();
            }});
        }}
    }});

    // Continuous 60 FPS animation loop when particles or pulsing are on
    function dynamicAnimationLoop() {{
        if (isParticlesOn || isPulsingOn) {{
            network.redraw();
        }}
        requestAnimationFrame(dynamicAnimationLoop);
    }}
    requestAnimationFrame(dynamicAnimationLoop);

    // Hover Event
    network.on('hoverNode', function(params) {{
        var nodeId = params.node;
        var p = metaDict[nodeId];
        if (!p) return;
        var card = document.getElementById('floating-hover-card');
        
        var lvl = p.level !== undefined ? p.level : 0;
        var badgeColor = '#EA4335';
        var badgeLabel = '⭐ Bài báo gốc (F0 Tâm điểm)';
        if (lvl === -1) {{ badgeColor = '#7C3AED'; badgeLabel = '🏛️ Nền tảng tham chiếu (R1)'; }}
        else if (lvl === -2) {{ badgeColor = '#6366F1'; badgeLabel = '🏛️ Cội nguồn lý thuyết (R2)'; }}
        else if (lvl <= -3) {{ badgeColor = '#4338CA'; badgeLabel = '🏛️ Nền tảng sâu xa (R3)'; }}
        else if (lvl === 1) {{ badgeColor = '#0284C7'; badgeLabel = '🚀 Kế thừa trực tiếp (F1)'; }}
        else if (lvl === 2) {{ badgeColor = '#059669'; badgeLabel = '🚀 Bước tiến mở rộng (F2)'; }}
        else if (lvl >= 3) {{ badgeColor = '#D97706'; badgeLabel = '🚀 Chân trời mới (F3)'; }}
        
        document.getElementById('hover-badge').style.color = badgeColor;
        document.getElementById('hover-badge').innerText = badgeLabel;
        
        var connBadge = document.getElementById('hover-conn-badge');
        var orphanNotice = document.getElementById('hover-orphan-notice');
        var totalConn = p.total_connections || 0;
        
        if (totalConn === 0) {{
            connBadge.innerHTML = '<span style="color:#F59E0B; background:rgba(245,158,11,0.18); padding:2px 8px; border-radius:6px; border:1px solid rgba(245,158,11,0.4); font-weight:700;">⚠️ 0 LIÊN KẾT (ĐỨNG LẺ LOI)</span>';
            if (orphanNotice) {{
                orphanNotice.style.display = 'block';
                orphanNotice.innerHTML = '⚠️ <b>Bài báo đứng lẻ loi:</b><br/><span style="color:#E2E8F0;">Công trình thuộc cùng chủ đề nhưng không có trích dẫn chéo trong tập dữ liệu giới hạn này.</span>';
            }}
        }} else {{
            connBadge.innerHTML = '<span style="color:#38BDF8; background:rgba(56,189,248,0.12); padding:2px 8px; border-radius:6px; border:1px solid rgba(56,189,248,0.3);">🔗 ' + totalConn + ' liên kết • ' + p.citation_count + ' trích dẫn</span>';
            if (orphanNotice) {{
                orphanNotice.style.display = 'none';
            }}
        }}

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
            if (isLineageTracingOn) {{
                traceAncestryAndDescendants(nodeId);
            }}
        }} else {{
            if (isLineageTracingOn) {{
                resetLineageHighlight();
            }}
        }}
    }});

    function showPaperModal(nodeId) {{
        var p = metaDict[nodeId];
        if (!p) return;

        var modal = document.getElementById('paper-modal');
        
        var lvl = p.level !== undefined ? p.level : 0;
        var badgeHtml = '';
        if (lvl === 0 || p.layer === 'seed') {{
            badgeHtml = '<span class="modal-badge badge-seed">Bài báo gốc (F0 Tâm điểm)</span>';
        }} else if (lvl === -1) {{
            badgeHtml = '<span class="modal-badge badge-r1">Nền tảng tham chiếu (R1)</span>';
        }} else if (lvl === -2) {{
            badgeHtml = '<span class="modal-badge badge-r2">Cội nguồn lý thuyết (R2)</span>';
        }} else if (lvl <= -3) {{
            badgeHtml = '<span class="modal-badge badge-r2">Nền tảng sâu xa (R3)</span>';
        }} else if (lvl === 1) {{
            badgeHtml = '<span class="modal-badge badge-f1">Kế thừa trực tiếp (F1)</span>';
        }} else if (lvl === 2) {{
            badgeHtml = '<span class="modal-badge badge-f2">Bước tiến mở rộng (F2)</span>';
        }} else {{
            badgeHtml = '<span class="modal-badge badge-f3">Chân trời mới (F3)</span>';
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

        if (p.total_connections === 0) {{
            lineageHtml += '<div style="background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.4); border-radius:10px; padding:12px 14px; margin-top:4px; margin-bottom:10px;">' +
                '<div style="color:#FCD34D; font-weight:800; font-size:12px; margin-bottom:6px; display:flex; align-items:center; gap:6px;">' +
                '<span>⚠️</span> <span>LÝ DO BÀI BÁO ĐỨNG LẺ LOI (KHÔNG CÓ MŨI TÊN KẾT NỐI):</span></div>' +
                '<div style="color:#E2E8F0; font-size:12px; line-height:1.6;">' +
                '• <b>Giới hạn chuỗi trích dẫn:</b> Công trình này thuộc cùng chủ đề nhưng không trực tiếp trích dẫn bài báo gốc trong tập mẫu giới hạn này.<br/>' +
                '• <b>Giá trị học thuật:</b> Cung cấp bằng chứng thực nghiệm độc lập và góc nhìn khách quan cho tổng quan nghiên cứu.' +
                '</div></div>';
        }}

        if (outList.length > 0) {{
            lineageHtml += '<div style="font-size:11.5px; color:#C4B5FD; font-weight:700; margin-bottom:4px;">⬇️ TÀI LIỆU CÔNG TRÌNH NÀY TRÍCH DẪN / THAM CHIẾU NỀN TẢNG (' + outList.length + ' bài):</div>';
            outList.forEach(function(targetId) {{
                var targetP = metaDict[targetId];
                if (targetP) {{
                    lineageHtml += '<div class="lineage-chip" onclick="jumpToNode(\\'' + targetId + '\\')">↳ ' + targetP.first_author + ' (' + targetP.year + '): ' + targetP.title.substring(0, 52) + '...</div>';
                }}
            }});
        }}

        if (inList.length > 0) {{
            lineageHtml += '<div style="font-size:11.5px; color:#38BDF8; font-weight:700; margin:8px 0 4px 0;">⬆️ ĐƯỢC TRÍCH DẪN & KẾ THỪA BỞI CÁC BÀI (' + inList.length + ' bài):</div>';
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
        if (isLineageTracingOn) {{
            traceAncestryAndDescendants(nodeId);
        }}
    }}

    function closePaperModal() {{
        document.getElementById('paper-modal').style.display = 'none';
        if (isLineageTracingOn) {{
            resetLineageHighlight();
        }}
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
            if (isLineageTracingOn) {{
                traceAncestryAndDescendants(foundId);
            }}
        }}
    }}

    // Mở / Thu gọn thanh công cụ trên cùng
    function toggleHudDrawer() {{
        var drawer = document.getElementById('hud-controls-drawer');
        var panel = document.getElementById('hudContentPanel');
        var arrow = document.getElementById('hudArrowIcon');
        if (!panel) return;
        if (panel.style.display === 'none' || panel.style.display === '') {{
            panel.style.display = 'flex';
            if (drawer) drawer.classList.add('is-open');
            if (arrow) arrow.innerText = '▾';
        }} else {{
            panel.style.display = 'none';
            if (drawer) drawer.classList.remove('is-open');
            if (arrow) arrow.innerText = '▸';
        }}
    }}

    // Mở / Thu gọn chú thích bên trái
    function toggleLegendDrawer() {{
        var drawer = document.getElementById('hud-legend-wrapper');
        var panel = document.getElementById('legendContentPanel');
        var arrow = document.getElementById('legendArrowIcon');
        if (!panel) return;
        if (panel.style.display === 'none' || panel.style.display === '') {{
            panel.style.display = 'flex';
            if (drawer) drawer.classList.add('is-open');
            if (arrow) arrow.innerText = '▾';
        }} else {{
            panel.style.display = 'none';
            if (drawer) drawer.classList.remove('is-open');
            if (arrow) arrow.innerText = '▸';
        }}
    }}

    // Thay đổi kiểu nền & Chế độ không gian 3D tương phản cao
    function switchCanvasBg(bgName) {{
        var wrapper = document.getElementById('network-wrapper');
        if (!wrapper) return;
        wrapper.className = 'bg-' + bgName;

        var isLight = (bgName === 'parchment' || bgName === 'nordic-light');
        var fontColor = isLight ? '#0F172A' : '#F8FAFC';
        var strokeColor = isLight ? '#FFFFFF' : '#0B0C0E';
        var strokeWidth = isLight ? 4 : 3;
        var edgeColor = isLight ? 'rgba(71, 85, 105, 0.65)' : 'rgba(100, 116, 139, 0.45)';

        var updates = [];
        rawNodes.forEach(function(n) {{
            updates.push({{
                id: n.id,
                font: {{
                    size: (n.font && n.font.size) ? n.font.size : 11,
                    color: fontColor,
                    face: 'Plus Jakarta Sans, sans-serif',
                    strokeWidth: strokeWidth,
                    strokeColor: strokeColor
                }}
            }});
        }});
        nodes.update(updates);
        
        network.setOptions({{
            edges: {{
                color: {{ color: edgeColor, highlight: '#38BDF8', hover: '#60A5FA' }}
            }}
        }});
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
