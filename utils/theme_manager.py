"""Academic Theme Manager - 10 Chế độ Giao diện Học thuật Cao cấp
Đảm bảo độ tương phản tuyệt đối (WCAG AAA/AA), không bị lẫn màu chữ, nền hoặc menu.
Hỗ trợ cả chế độ tối (Dark Mode) và chế độ sáng tinh khôi (Light Mode).
Tác giả & Kỹ sư trưởng AI: TRẦN DUY (Lead AI Research Engineer)
"""
from typing import Dict, Any, List

THEMES: Dict[str, Dict[str, Any]] = {
    "obsidian_dark": {
        "id": "obsidian_dark",
        "name": "Obsidian Dark (Mặc định)",
        "type": "dark",
        "tagline": "Đêm học thuật sâu thẳm • Độ tập trung tối đa",
        "desc": "Tông đen đá vỏ chai Obsidian phối cùng xám Slate và điểm nhấn Electric Cyan & Emerald.",
        "colors": {
            "bg_main": "#0B0C0E",
            "bg_surface": "#12141A",
            "bg_surface_elevated": "#181B24",
            "bg_surface_card": "#1E222D",
            "border_subtle": "#262B38",
            "border_hover": "#38BDF8",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "text_muted": "#64748B",
            "primary_accent": "#38BDF8",
            "primary_gradient": "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
            "accent_glow": "rgba(56, 189, 248, 0.25)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(37, 99, 235, 0.28) 0%, rgba(56, 189, 248, 0.14) 100%)",
            "sidebar_hover_bg": "#1F2536",
            "badge_green_bg": "rgba(16, 185, 129, 0.15)",
            "badge_green_text": "#34D399",
            "badge_green_border": "rgba(16, 185, 129, 0.4)",
            "badge_blue_bg": "rgba(56, 189, 248, 0.15)",
            "badge_blue_text": "#38BDF8",
            "badge_blue_border": "rgba(56, 189, 248, 0.4)",
            "badge_rose_bg": "rgba(244, 63, 94, 0.15)",
            "badge_rose_text": "#FB7185",
            "badge_rose_border": "rgba(244, 63, 94, 0.4)",
            "plotly_bg": "#12141A",
            "plotly_grid": "#262B38",
            "plotly_font": "#F8FAFC"
        }
    },
    "oxford_blue": {
        "id": "oxford_blue",
        "name": "Oxford Royal Blue",
        "type": "dark",
        "tagline": "Học thuật Hoàng gia Oxford • Uyên bác & Trầm ổn",
        "desc": "Sắc xanh Navy đại dương sâu thẳm kết hợp ánh vàng Gold Amber hoàng gia và Ice Blue sang trọng.",
        "colors": {
            "bg_main": "#070D1E",
            "bg_surface": "#0D1833",
            "bg_surface_elevated": "#132347",
            "bg_surface_card": "#182C59",
            "border_subtle": "#1E3A75",
            "border_hover": "#60A5FA",
            "text_primary": "#F0F6FF",
            "text_secondary": "#93C5FD",
            "text_muted": "#6089BF",
            "primary_accent": "#60A5FA",
            "primary_gradient": "linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%)",
            "accent_glow": "rgba(96, 165, 250, 0.28)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(29, 78, 216, 0.35) 0%, rgba(96, 165, 250, 0.18) 100%)",
            "sidebar_hover_bg": "#182C59",
            "badge_green_bg": "rgba(52, 211, 153, 0.15)",
            "badge_green_text": "#34D399",
            "badge_green_border": "rgba(52, 211, 153, 0.4)",
            "badge_blue_bg": "rgba(96, 165, 250, 0.18)",
            "badge_blue_text": "#93C5FD",
            "badge_blue_border": "rgba(96, 165, 250, 0.45)",
            "badge_rose_bg": "rgba(251, 113, 133, 0.15)",
            "badge_rose_text": "#FDA4AF",
            "badge_rose_border": "rgba(251, 113, 133, 0.4)",
            "plotly_bg": "#0D1833",
            "plotly_grid": "#1E3A75",
            "plotly_font": "#F0F6FF"
        }
    },
    "cambridge_emerald": {
        "id": "cambridge_emerald",
        "name": "Cambridge Emerald",
        "type": "dark",
        "tagline": "Viện Hàn lâm Cambridge • Tri thức & Sinh thái học",
        "desc": "Tông xanh ngọc lục bảo rừng sâu huyền bí kết hợp ánh Mint rực rỡ và vàng đồng cổ điển.",
        "colors": {
            "bg_main": "#06130E",
            "bg_surface": "#0C1F18",
            "bg_surface_elevated": "#122E24",
            "bg_surface_card": "#183D30",
            "border_subtle": "#1F4F3F",
            "border_hover": "#34D399",
            "text_primary": "#ECFDF5",
            "text_secondary": "#A7F3D0",
            "text_muted": "#5E9E82",
            "primary_accent": "#34D399",
            "primary_gradient": "linear-gradient(135deg, #059669 0%, #047857 100%)",
            "accent_glow": "rgba(52, 211, 153, 0.28)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(5, 150, 105, 0.35) 0%, rgba(52, 211, 153, 0.18) 100%)",
            "sidebar_hover_bg": "#183D30",
            "badge_green_bg": "rgba(52, 211, 153, 0.2)",
            "badge_green_text": "#6EE7B7",
            "badge_green_border": "rgba(52, 211, 153, 0.5)",
            "badge_blue_bg": "rgba(56, 189, 248, 0.15)",
            "badge_blue_text": "#7DD3FC",
            "badge_blue_border": "rgba(56, 189, 248, 0.4)",
            "badge_rose_bg": "rgba(244, 63, 94, 0.15)",
            "badge_rose_text": "#FB7185",
            "badge_rose_border": "rgba(244, 63, 94, 0.4)",
            "plotly_bg": "#0C1F18",
            "plotly_grid": "#1F4F3F",
            "plotly_font": "#ECFDF5"
        }
    },
    "harvard_crimson": {
        "id": "harvard_crimson",
        "name": "Harvard Crimson",
        "type": "dark",
        "tagline": "Đại học Harvard • Quyền lực & Tinh hoa xuất chúng",
        "desc": "Sắc đỏ rượu Crimson danh giá hòa quyện cùng xám than ấm áp và ánh Rose rực rỡ.",
        "colors": {
            "bg_main": "#12070A",
            "bg_surface": "#1F0C12",
            "bg_surface_elevated": "#2E131C",
            "bg_surface_card": "#3D1A26",
            "border_subtle": "#542233",
            "border_hover": "#FB7185",
            "text_primary": "#FFF1F2",
            "text_secondary": "#FECDD3",
            "text_muted": "#A86979",
            "primary_accent": "#FB7185",
            "primary_gradient": "linear-gradient(135deg, #E11D48 0%, #BE123C 100%)",
            "accent_glow": "rgba(251, 113, 133, 0.28)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(225, 29, 72, 0.35) 0%, rgba(251, 113, 133, 0.18) 100%)",
            "sidebar_hover_bg": "#3D1A26",
            "badge_green_bg": "rgba(52, 211, 153, 0.15)",
            "badge_green_text": "#34D399",
            "badge_green_border": "rgba(52, 211, 153, 0.4)",
            "badge_blue_bg": "rgba(56, 189, 248, 0.15)",
            "badge_blue_text": "#38BDF8",
            "badge_blue_border": "rgba(56, 189, 248, 0.4)",
            "badge_rose_bg": "rgba(251, 113, 133, 0.22)",
            "badge_rose_text": "#FDA4AF",
            "badge_rose_border": "rgba(251, 113, 133, 0.5)",
            "plotly_bg": "#1F0C12",
            "plotly_grid": "#542233",
            "plotly_font": "#FFF1F2"
        }
    },
    "mit_titanium": {
        "id": "mit_titanium",
        "name": "MIT Tech Titanium",
        "type": "dark",
        "tagline": "Viện Công nghệ MIT • Tương lai & Kỹ thuật số",
        "desc": "Tông xám Titanium hiện đại kết hợp sắc Neon Cyan lạnh và ánh tím lượng tử Quantum Violet.",
        "colors": {
            "bg_main": "#0D0F14",
            "bg_surface": "#141720",
            "bg_surface_elevated": "#1C212E",
            "bg_surface_card": "#242B3B",
            "border_subtle": "#2F384C",
            "border_hover": "#06B6D4",
            "text_primary": "#F8FAFC",
            "text_secondary": "#CBD5E1",
            "text_muted": "#7B8FA8",
            "primary_accent": "#06B6D4",
            "primary_gradient": "linear-gradient(135deg, #0891B2 0%, #0E7490 100%)",
            "accent_glow": "rgba(6, 182, 212, 0.28)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(8, 145, 178, 0.35) 0%, rgba(6, 182, 212, 0.18) 100%)",
            "sidebar_hover_bg": "#242B3B",
            "badge_green_bg": "rgba(52, 211, 153, 0.15)",
            "badge_green_text": "#34D399",
            "badge_green_border": "rgba(52, 211, 153, 0.4)",
            "badge_blue_bg": "rgba(6, 182, 212, 0.18)",
            "badge_blue_text": "#67E8F9",
            "badge_blue_border": "rgba(6, 182, 212, 0.45)",
            "badge_rose_bg": "rgba(244, 63, 94, 0.15)",
            "badge_rose_text": "#FB7185",
            "badge_rose_border": "rgba(244, 63, 94, 0.4)",
            "plotly_bg": "#141720",
            "plotly_grid": "#2F384C",
            "plotly_font": "#F8FAFC"
        }
    },
    "stanford_amber": {
        "id": "stanford_amber",
        "name": "Stanford Solar Amber",
        "type": "dark",
        "tagline": "Thung lũng Silicon • Khởi nghiệp & Năng lượng",
        "desc": "Tông than đen ấm áp Charcoal kết hợp ánh vàng hổ phách Amber rực rỡ và sắc cam năng động.",
        "colors": {
            "bg_main": "#120E0A",
            "bg_surface": "#1C1711",
            "bg_surface_elevated": "#29211A",
            "bg_surface_card": "#362C22",
            "border_subtle": "#4A3D2F",
            "border_hover": "#F59E0B",
            "text_primary": "#FFFBEB",
            "text_secondary": "#FDE68A",
            "text_muted": "#A18968",
            "primary_accent": "#F59E0B",
            "primary_gradient": "linear-gradient(135deg, #D97706 0%, #B45309 100%)",
            "accent_glow": "rgba(245, 158, 11, 0.28)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(217, 119, 6, 0.35) 0%, rgba(245, 158, 11, 0.18) 100%)",
            "sidebar_hover_bg": "#362C22",
            "badge_green_bg": "rgba(52, 211, 153, 0.15)",
            "badge_green_text": "#34D399",
            "badge_green_border": "rgba(52, 211, 153, 0.4)",
            "badge_blue_bg": "rgba(245, 158, 11, 0.18)",
            "badge_blue_text": "#FBBF24",
            "badge_blue_border": "rgba(245, 158, 11, 0.45)",
            "badge_rose_bg": "rgba(244, 63, 94, 0.15)",
            "badge_rose_text": "#FB7185",
            "badge_rose_border": "rgba(244, 63, 94, 0.4)",
            "plotly_bg": "#1C1711",
            "plotly_grid": "#4A3D2F",
            "plotly_font": "#FFFBEB"
        }
    },
    "nordic_glacier": {
        "id": "nordic_glacier",
        "name": "Nordic Glacier (Sáng / Light)",
        "type": "light",
        "tagline": "Bắc Âu Tối giản • Sương tuyết thanh khiết",
        "desc": "Tông trắng tuyết Snow White kết hợp màu xám phiến đá Ice Slate và chữ than đen cực kỳ sắc nét.",
        "colors": {
            "bg_main": "#F8FAFC",
            "bg_surface": "#FFFFFF",
            "bg_surface_elevated": "#F1F5F9",
            "bg_surface_card": "#E2E8F0",
            "border_subtle": "#CBD5E1",
            "border_hover": "#0284C7",
            "text_primary": "#0F172A",
            "text_secondary": "#334155",
            "text_muted": "#475569",
            "primary_accent": "#0284C7",
            "primary_gradient": "linear-gradient(135deg, #0284C7 0%, #0369A1 100%)",
            "accent_glow": "rgba(2, 132, 199, 0.2)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(2, 132, 199, 0.18) 0%, rgba(2, 132, 199, 0.08) 100%)",
            "sidebar_hover_bg": "#F1F5F9",
            "badge_green_bg": "#DCFCE7",
            "badge_green_text": "#15803D",
            "badge_green_border": "#86EFAC",
            "badge_blue_bg": "#E0F2FE",
            "badge_blue_text": "#0369A1",
            "badge_blue_border": "#7DD3FC",
            "badge_rose_bg": "#FFE4E6",
            "badge_rose_text": "#BE123C",
            "badge_rose_border": "#FDA4AF",
            "plotly_bg": "#FFFFFF",
            "plotly_grid": "#E2E8F0",
            "plotly_font": "#0F172A"
        }
    },
    "parchment_light": {
        "id": "parchment_light",
        "name": "Parchment Ivory (Sáng / Light)",
        "type": "light",
        "tagline": "Bản thảo Giấy da cổ điển • Thư viện Hoàng gia",
        "desc": "Tông giấy da ngà mịn ấm áp Ivory phối cùng chữ màu mực Espresso đen đậm và nhấn Navy sâu.",
        "colors": {
            "bg_main": "#FBF9F4",
            "bg_surface": "#FFFFFF",
            "bg_surface_elevated": "#F4EFE6",
            "bg_surface_card": "#EAE3D2",
            "border_subtle": "#D5CCA6",
            "border_hover": "#1E3A8A",
            "text_primary": "#1C1917",
            "text_secondary": "#44403C",
            "text_muted": "#57534E",
            "primary_accent": "#1E3A8A",
            "primary_gradient": "linear-gradient(135deg, #1E3A8A 0%, #172554 100%)",
            "accent_glow": "rgba(30, 58, 138, 0.2)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(30, 58, 138, 0.16) 0%, rgba(30, 58, 138, 0.06) 100%)",
            "sidebar_hover_bg": "#F4EFE6",
            "badge_green_bg": "#DCFCE7",
            "badge_green_text": "#166534",
            "badge_green_border": "#86EFAC",
            "badge_blue_bg": "#E0E7FF",
            "badge_blue_text": "#1E3A8A",
            "badge_blue_border": "#A5B4FC",
            "badge_rose_bg": "#FFE4E6",
            "badge_rose_text": "#9F1239",
            "badge_rose_border": "#FDA4AF",
            "plotly_bg": "#FFFFFF",
            "plotly_grid": "#EAE3D2",
            "plotly_font": "#1C1917"
        }
    },
    "cyberpunk_2077": {
        "id": "cyberpunk_2077",
        "name": "Cyberpunk Academic 2077",
        "type": "dark",
        "tagline": "Mạng Nơ-ron Tương lai • Neon Tương phản cao",
        "desc": "Tông đen sâu thẳm Pure Void kết hợp Neon Magenta rực rỡ, Cyber Cyan và sắc tím phát quang.",
        "colors": {
            "bg_main": "#05050A",
            "bg_surface": "#0C0C16",
            "bg_surface_elevated": "#141424",
            "bg_surface_card": "#1E1E36",
            "border_subtle": "#2E2E52",
            "border_hover": "#00F0FF",
            "text_primary": "#FFFFFF",
            "text_secondary": "#E0E7FF",
            "text_muted": "#818CF8",
            "primary_accent": "#00F0FF",
            "primary_gradient": "linear-gradient(135deg, #F43F5E 0%, #8B5CF6 100%)",
            "accent_glow": "rgba(0, 240, 255, 0.35)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(244, 63, 94, 0.35) 0%, rgba(139, 92, 246, 0.2) 100%)",
            "sidebar_hover_bg": "#1E1E36",
            "badge_green_bg": "rgba(16, 185, 129, 0.2)",
            "badge_green_text": "#34D399",
            "badge_green_border": "rgba(16, 185, 129, 0.5)",
            "badge_blue_bg": "rgba(0, 240, 255, 0.18)",
            "badge_blue_text": "#00F0FF",
            "badge_blue_border": "rgba(0, 240, 255, 0.5)",
            "badge_rose_bg": "rgba(244, 63, 94, 0.22)",
            "badge_rose_text": "#FB7185",
            "badge_rose_border": "rgba(244, 63, 94, 0.5)",
            "plotly_bg": "#0C0C16",
            "plotly_grid": "#2E2E52",
            "plotly_font": "#FFFFFF"
        }
    },
    "tokyo_sakura": {
        "id": "tokyo_sakura",
        "name": "Tokyo Sakura Midnight",
        "type": "dark",
        "tagline": "Đêm Hoa Anh Đào • Tĩnh tại & Thơ mộng",
        "desc": "Tông tím chàm đêm huyền ảo Midnight Indigo kết hợp sắc hồng hoa anh đào dịu mát Sakura Rose.",
        "colors": {
            "bg_main": "#0E0C16",
            "bg_surface": "#161324",
            "bg_surface_elevated": "#201C33",
            "bg_surface_card": "#2B2645",
            "border_subtle": "#3D375E",
            "border_hover": "#F472B6",
            "text_primary": "#FDF2F8",
            "text_secondary": "#FBCFE8",
            "text_muted": "#A78BFA",
            "primary_accent": "#F472B6",
            "primary_gradient": "linear-gradient(135deg, #DB2777 0%, #9333EA 100%)",
            "accent_glow": "rgba(244, 114, 182, 0.28)",
            "sidebar_active_bg": "linear-gradient(90deg, rgba(219, 39, 119, 0.35) 0%, rgba(147, 51, 234, 0.18) 100%)",
            "sidebar_hover_bg": "#2B2645",
            "badge_green_bg": "rgba(52, 211, 153, 0.15)",
            "badge_green_text": "#34D399",
            "badge_green_border": "rgba(52, 211, 153, 0.4)",
            "badge_blue_bg": "rgba(192, 132, 252, 0.18)",
            "badge_blue_text": "#C084FC",
            "badge_blue_border": "rgba(192, 132, 252, 0.45)",
            "badge_rose_bg": "rgba(244, 114, 182, 0.2)",
            "badge_rose_text": "#F472B6",
            "badge_rose_border": "rgba(244, 114, 182, 0.5)",
            "plotly_bg": "#161324",
            "plotly_grid": "#3D375E",
            "plotly_font": "#FDF2F8"
        }
    }
}

def get_theme_list() -> List[Dict[str, Any]]:
    """Trả về danh sách 10 theme để hiển thị lựa chọn."""
    return list(THEMES.values())

def get_theme(theme_id: str) -> Dict[str, Any]:
    """Lấy cấu hình chi tiết của theme theo id, mặc định obsidian_dark."""
    return THEMES.get(theme_id, THEMES["obsidian_dark"])

def generate_theme_css(theme_id: str) -> str:
    """Tạo CSS tùy biến động theo theme đã chọn, bảo đảm độ tương phản tối đa và không lẫn màu."""
    t = get_theme(theme_id)
    c = t["colors"]
    is_light = (t["type"] == "light")
    
    input_bg = c["bg_surface_elevated"]
    input_text = c["text_primary"]
    input_border = c["border_subtle"]
    
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    
    :root {{
        --bg-main: {c["bg_main"]};
        --bg-surface: {c["bg_surface"]};
        --bg-surface-elevated: {c["bg_surface_elevated"]};
        --bg-surface-card: {c["bg_surface_card"]};
        --border-subtle: {c["border_subtle"]};
        --border-hover: {c["border_hover"]};
        
        --text-primary: {c["text_primary"]};
        --text-secondary: {c["text_secondary"]};
        --text-muted: {c["text_muted"]};
        
        --primary-accent: {c["primary_accent"]};
        --primary-gradient: {c["primary_gradient"]};
        --accent-glow: {c["accent_glow"]};
        
        --badge-green-bg: {c["badge_green_bg"]};
        --badge-green-text: {c["badge_green_text"]};
        --badge-green-border: {c["badge_green_border"]};
        
        --badge-blue-bg: {c["badge_blue_bg"]};
        --badge-blue-text: {c["badge_blue_text"]};
        --badge-blue-border: {c["badge_blue_border"]};
        
        --badge-rose-bg: {c["badge_rose_bg"]};
        --badge-rose-text: {c["badge_rose_text"]};
        --badge-rose-border: {c["badge_rose_border"]};
    }}
    
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: {c["text_primary"]} !important;
        background-color: {c["bg_main"]} !important;
        -webkit-font-smoothing: antialiased;
    }}
    
    .stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown div, .stMarkdown label {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: {c["text_primary"]} !important;
    }}
    
    .stMarkdown p {{
        font-size: 14px;
        line-height: 1.65;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: {c["text_primary"]} !important;
        font-weight: 700 !important;
        letter-spacing: -0.015em !important;
    }}
    h1 {{ font-size: 22px !important; margin-bottom: 8px !important; }}
    h2 {{ font-size: 18px !important; margin-bottom: 6px !important; }}
    h3 {{ font-size: 15px !important; margin-bottom: 4px !important; }}
    
    /* Khung Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {c["bg_surface"]} !important;
        border-right: 1px solid {c["border_subtle"]} !important;
        transition: all 0.25s ease-in-out !important;
    }}
    
    section[data-testid="stSidebar"][aria-expanded="true"] {{
        width: 350px !important;
        min-width: 320px !important;
        max-width: 380px !important;
    }}

    /* Nút mũi tên đóng Sidebar (khi Sidebar đang mở) */
    button[data-testid="stSidebarCollapseButton"] {{
        background: {c["bg_surface_elevated"]} !important;
        border: 1px solid {c["border_subtle"]} !important;
        border-radius: 8px !important;
        color: {c["text_primary"]} !important;
        transition: all 0.2s ease !important;
    }}
    
    button[data-testid="stSidebarCollapseButton"]:hover {{
        background: {c["primary_accent"]} !important;
        color: #FFFFFF !important;
        border-color: {c["primary_accent"]} !important;
    }}

    /* Nút mũi tên mở lại Sidebar (khi Sidebar đã thu gọn) - Luôn hiển thị nổi bật ở góc trên bên trái */
    div[data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {{
        display: block !important;
        visibility: visible !important;
        pointer-events: auto !important;
        z-index: 999999 !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
    }}
    
    div[data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {{
        background: {c["bg_surface_elevated"]} !important;
        border: 1.5px solid {c["primary_accent"]} !important;
        border-radius: 10px !important;
        color: {c["primary_accent"]} !important;
        padding: 6px 10px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35) !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }}
    
    div[data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover {{
        background: {c["primary_accent"]} !important;
        color: #FFFFFF !important;
        transform: scale(1.08) !important;
    }}
    
    /* Không gian làm việc chính: Căn giữa hoàn hảo, co giãn đối xứng cả khi mở & ẩn Sidebar */
    .main, [data-testid="stAppViewContainer"] > .main {{
        width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
    }}
    
    .main .block-container,
    div[data-testid="stAppViewBlockContainer"],
    [data-testid="block-container"] {{
        width: 100% !important;
        max-width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        box-sizing: border-box !important;
    }}
    
    .sidebar-brand-box {{
        padding: 14px 16px;
        background: {c["bg_surface_elevated"]};
        border: 1px solid {c["border_subtle"]};
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }}
    
    .sidebar-brand-title {{
        font-size: 15px;
        font-weight: 800;
        color: {c["text_primary"]};
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: 0.02em;
    }}
    
    .sidebar-brand-sub {{
        font-size: 11.5px;
        color: {c["text_secondary"]};
        margin-top: 4px;
        line-height: 1.45;
    }}

    .developer-pill {{
        display: inline-block;
        font-size: 10.5px;
        font-weight: 700;
        background: {c["badge_blue_bg"]};
        color: {c["primary_accent"]};
        border: 1px solid {c["badge_blue_border"]};
        padding: 2px 8px;
        border-radius: 6px;
        margin-top: 6px;
    }}
    
    .menu-header-badge {{
        font-size: 10.5px;
        font-weight: 800;
        color: {c["text_muted"]};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 14px 0 6px 4px;
    }}

    /* Menu Chọn Màn Hình Làm Việc Bọc Khối Cao Cấp (Flat Mono Style) */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: column !important;
        gap: 5px !important;
        background: {c["bg_main"]} !important;
        border: 1px solid {c["border_subtle"]} !important;
        border-radius: 12px !important;
        padding: 6px !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
        display: flex !important;
        align-items: center !important;
        background: {c["bg_surface_elevated"]} !important;
        border: 1px solid {c["border_subtle"]} !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin-bottom: 0 !important;
        cursor: pointer !important;
        transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child {{
        display: none !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
        background: {c["sidebar_hover_bg"]} !important;
        border-color: {c["border_hover"]} !important;
        transform: translateX(2px) !important;
    }}
    
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
        background: {c["sidebar_active_bg"]} !important;
        border-color: {c["border_hover"]} !important;
        border-left: 3.5px solid {c["border_hover"]} !important;
    }}
    
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {{
        font-size: 12.5px !important;
        font-weight: 600 !important;
        color: {c["text_primary"]} !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {{
        color: {c["text_primary"]} !important;
        font-weight: 700 !important;
    }}

    /* Hàng Điều Khiển Cân Xứng 52px */
    .symmetrical-action-card {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 52px;
        height: 52px;
        padding: 0 14px;
        background: {c["bg_surface_elevated"]};
        border: 1px solid {c["border_subtle"]};
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        box-sizing: border-box;
        overflow: hidden;
        gap: 10px;
        transition: all 0.2s ease;
    }}
    .symmetrical-action-card.ready {{
        border-color: {c["badge_green_border"]};
        background: {c["badge_green_bg"]};
    }}
    .symmetrical-action-card.empty {{
        border-color: {c["badge_rose_border"]};
        background: {c["badge_rose_bg"]};
    }}

    /* Nút điều hướng nhanh đa sắc màu tương phản cao (High-Contrast Quick Navigation Cards) */
    .quick-nav-card {{
        padding: 14px 16px;
        border-radius: 12px;
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        box-shadow: 0 4px 14px rgba(0,0,0,0.22);
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 8px;
        min-height: 98px;
    }}
    .quick-nav-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.35);
    }}
    .qnav-net {{
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        border: 1.5px solid #38BDF8 !important;
    }}
    .qnav-apa {{
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        border: 1.5px solid #34D399 !important;
    }}
    .qnav-cars {{
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        border: 1.5px solid #A78BFA !important;
    }}
    .qnav-pack {{
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
        border: 1.5px solid #FBBF24 !important;
    }}

    .status-text-title {{
        font-size: 12px;
        font-weight: 700;
        line-height: 1.25;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        letter-spacing: 0.02em;
        color: {c["text_primary"]};
    }}
    .status-text-sub {{
        font-size: 11px;
        color: {c["text_secondary"]};
        line-height: 1.2;
        margin: 2px 0 0 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .doi-tag-badge {{
        flex-shrink: 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 8px;
        white-space: nowrap;
        text-align: center;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }}
    .doi-tag-badge.ready {{
        background: {c["badge_green_bg"]};
        border: 1px solid {c["badge_green_border"]};
        color: {c["badge_green_text"]};
    }}
    .doi-tag-badge.empty {{
        background: {c["badge_rose_bg"]};
        border: 1px solid {c["badge_rose_border"]};
        color: {c["badge_rose_text"]};
    }}

    /* Thanh điều hướng trên cùng (Top Header Toolbar - Tên phần mềm cố định bên phải) */
    .app-top-toolbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 16px;
        background: {c["bg_surface"]};
        border: 1px solid {c["border_subtle"]};
        border-radius: 12px;
        margin-bottom: 18px;
        box-shadow: 0 2px 14px rgba(0,0,0,0.06);
        gap: 12px;
        flex-wrap: wrap;
        box-sizing: border-box;
        max-width: 100%;
    }}
    
    .toolbar-left {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        flex: 1 1 auto;
        min-width: 240px;
    }}
    
    .toolbar-breadcrumb {{
        font-size: 13px;
        font-weight: 700;
        color: {c["text_primary"]};
        display: inline-flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
    }}
    .crumb-root {{
        color: {c["text_secondary"]};
        font-weight: 500;
    }}
    .crumb-slash {{
        color: {c["text_muted"]};
        font-weight: 400;
    }}
    .crumb-active {{
        color: {c["primary_accent"]};
        font-weight: 700;
    }}
    
    .status-chip-group {{
        display: inline-flex;
        gap: 6px;
        align-items: center;
        flex-wrap: wrap;
    }}
    
    .status-chip {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 12px;
        border: 1px solid transparent;
        white-space: nowrap;
    }}
    .status-chip.blue {{
        background: {c["badge_blue_bg"]};
        color: {c["badge_blue_text"]};
        border-color: {c["badge_blue_border"]};
    }}
    .status-chip.green {{
        background: {c["badge_green_bg"]};
        color: {c["badge_green_text"]};
        border-color: {c["badge_green_border"]};
    }}
    .status-chip.rose {{
        background: {c["badge_rose_bg"]};
        color: {c["badge_rose_text"]};
        border-color: {c["badge_rose_border"]};
    }}

    .toolbar-right-brand {{
        display: flex;
        align-items: center;
        gap: 8px;
        flex-shrink: 0;
        margin-left: auto;
    }}
    
    .top-brand-badge {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: {c["bg_surface_elevated"]};
        border: 1px solid {c["border_subtle"]};
        padding: 4px 10px;
        border-radius: 18px;
    }}
    
    .brand-pulse-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: {c["primary_accent"]};
        box-shadow: 0 0 8px {c["primary_accent"]};
        display: inline-block;
    }}
    
    .top-brand-text {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 12.5px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {c["text_primary"]};
    }}
    
    .top-brand-ver {{
        font-size: 10px;
        font-weight: 700;
        color: {c["primary_accent"]};
        background: {c["badge_blue_bg"]};
        border: 1px solid {c["badge_blue_border"]};
        padding: 1px 5px;
        border-radius: 4px;
    }}

    .top-brand-author {{
        font-size: 11px;
        font-weight: 600;
        color: {c["text_muted"]};
        white-space: nowrap;
    }}

    /* Banner quảng bá phần mềm */
    .hero-banner-box {{
        background: {c["bg_surface"]};
        border: 1px solid {c["border_subtle"]};
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 2px 14px rgba(0,0,0,0.06);
        position: relative;
        overflow: hidden;
    }}
    .hero-banner-title {{
        font-size: 18px;
        font-weight: 800;
        color: {c["text_primary"]};
        letter-spacing: -0.01em;
        margin-bottom: 6px;
    }}
    .hero-banner-desc {{
        color: {c["text_secondary"]};
        font-size: 13.5px;
        line-height: 1.6;
        max-width: 900px;
    }}
    .hero-banner-meta {{
        display: flex;
        gap: 10px;
        align-items: center;
        margin-top: 12px;
        flex-wrap: wrap;
    }}

    /* Hiệu ứng Tên chương trình Viết hoa Phát sáng Ấn tượng (SCHOLARGRAPH PRO HERO) */
    .manual-hero-banner {{
        background: {c["bg_surface"]};
        border: 1px solid {c["border_hover"]};
        border-radius: 16px;
        padding: 24px 20px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        position: relative;
        overflow: hidden;
    }}
    .manual-app-title {{
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        font-size: 30px;
        font-weight: 900;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {c["text_primary"]};
        margin: 6px 0 8px 0;
    }}
    .manual-app-subtitle {{
        font-size: 13px;
        font-weight: 700;
        color: {c["primary_accent"]};
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    
    .manual-step-card {{
        background: {c["bg_surface"]};
        border: 1px solid {c["border_subtle"]};
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        transition: all 0.18s ease;
    }}
    .manual-step-card:hover {{
        border-color: {c["border_hover"]};
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }}
    .manual-step-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: {c["badge_blue_bg"]};
        color: {c["primary_accent"]};
        border: 1px solid {c["badge_blue_border"]};
        font-weight: 800;
        font-size: 12px;
        flex-shrink: 0;
    }}

    /* Khung Box Nội dung */
    .frame-box, .tab-content-card {{
        background: {c["bg_surface"]};
        border: 1px solid {c["border_subtle"]};
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }}

    .evidence-card {{
        background: {c["bg_surface_elevated"]};
        border: 1px solid {c["border_subtle"]};
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: all 0.18s ease;
    }}
    .evidence-card:hover {{
        border-color: {c["border_hover"]};
        transform: translateY(-1px);
    }}

    /* Thẻ Điều Hướng Nhanh (Quick Navigation Cards) - Rực rỡ, Đổ màu nền, Chữ siêu tương phản */
    .quick-nav-card {{
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 8px;
        color: #FFFFFF !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18);
        transition: all 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.22);
    }}
    .quick-nav-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.28);
    }}
    .quick-nav-card .qnav-title {{
        font-size: 14px;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
        letter-spacing: -0.01em;
        text-shadow: 0 1px 2px rgba(0,0,0,0.4);
    }}
    .quick-nav-card .qnav-desc {{
        font-size: 11.5px;
        color: rgba(255, 255, 255, 0.92) !important;
        line-height: 1.4;
        margin: 0;
        font-weight: 500;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }}
    .quick-nav-card.qnav-net {{
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
        border-left: 5px solid #38BDF8;
    }}
    .quick-nav-card.qnav-apa {{
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        border-left: 5px solid #34D399;
    }}
    .quick-nav-card.qnav-cars {{
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        border-left: 5px solid #A78BFA;
    }}
    .quick-nav-card.qnav-pack {{
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
        border-left: 5px solid #FBBF24;
    }}

    /* Thẻ Số Liệu (Metric Cards) */
    .metric-card-full {{
        background: {c["bg_surface"]};
        border: 1px solid {c["border_subtle"]};
        border-radius: 12px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }}
    .metric-title {{
        font-size: 11px;
        font-weight: 700;
        color: {c["text_secondary"]};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-value {{
        font-size: 22px;
        font-weight: 800;
        color: {c["text_primary"]};
        line-height: 1.15;
        margin: 3px 0;
        letter-spacing: -0.02em;
    }}
    .metric-sub {{
        font-size: 11px;
        color: {c["text_muted"]};
    }}

    /* Form Controls */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {input_border} !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }}
    .stTextArea textarea:focus, .stTextInput input:focus {{
        border-color: {c["border_hover"]} !important;
        box-shadow: 0 0 0 2px {c["accent_glow"]} !important;
    }}

    .stButton button {{
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        height: 48px !important;
        border: 1px solid {c["border_subtle"]} !important;
        background-color: {c["bg_surface_elevated"]} !important;
        color: {c["text_primary"]} !important;
        transition: all 0.18s ease-in-out !important;
    }}
    .stButton button:hover {{
        background-color: {c["sidebar_hover_bg"]} !important;
        border-color: {c["border_hover"]} !important;
        color: {c["text_primary"]} !important;
    }}
    
    .stButton button[kind="primary"] {{
        background: {c["primary_gradient"]} !important;
        border: 1px solid {c["border_hover"]} !important;
        color: #FFFFFF !important;
        font-size: 13.5px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px {c["accent_glow"]} !important;
    }}

    .stDownloadButton button {{
        border-radius: 8px !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        padding: 6px 12px !important;
        border: 1px solid {c["border_subtle"]} !important;
        background-color: {c["bg_surface_elevated"]} !important;
        color: {c["text_primary"]} !important;
    }}

    /* Streamlit Expanders */
    div[data-testid="stExpander"] {{
        background-color: {c["bg_surface"]} !important;
        border: 1px solid {c["border_subtle"]} !important;
        border-radius: 10px !important;
        color: {c["text_primary"]} !important;
    }}
    div[data-testid="stExpander"] summary {{
        color: {c["text_primary"]} !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stExpander"] div[role="region"] {{
        color: {c["text_primary"]} !important;
        background-color: {c["bg_surface"]} !important;
    }}

    /* Streamlit Tabs Styling */
    div[data-baseweb="tab-list"] {{
        background-color: {c["bg_surface"]} !important;
        border: 1px solid {c["border_subtle"]} !important;
        border-radius: 10px !important;
        padding: 3px !important;
        gap: 3px !important;
    }}
    /* Custom Badges for Diamond Knowledge Graph */
    .custom-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .custom-badge.badge-blue {
        background: {c["badge_blue_bg"]};
        color: {c["badge_blue_text"]};
        border: 1px solid {c["badge_blue_border"]};
    }
    .custom-badge.badge-green {
        background: {c["badge_green_bg"]};
        color: {c["badge_green_text"]};
        border: 1px solid {c["badge_green_border"]};
    }
    .custom-badge.badge-rose {
        background: {c["badge_rose_bg"]};
        color: {c["badge_rose_text"]};
        border: 1px solid {c["badge_rose_border"]};
    }
    .custom-badge.badge-amber {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .custom-badge.badge-purple {
        background: rgba(168, 85, 247, 0.15);
        color: #A855F7;
        border: 1px solid rgba(168, 85, 247, 0.4);
    }
    .custom-badge.badge-diamond-seed {
        background: rgba(234, 67, 53, 0.2);
        color: #F28B82;
        border: 1px solid rgba(234, 67, 53, 0.45);
    }
    .custom-badge.badge-diamond-root {
        background: rgba(124, 58, 237, 0.2);
        color: #C4B5FD;
        border: 1px solid rgba(124, 58, 237, 0.45);
    }
    .custom-badge.badge-diamond-frontier {
        background: rgba(2, 132, 199, 0.2);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.45);
    }

    /* =========================================================================
       TỐI ƯU HÓA ĐẶC BIỆT CHO THIẾT BỊ DI ĐỘNG & MÁY TÍNH BẢNG (MOBILE & TABLET UX)
       ========================================================================= */
    /* Máy tính bảng & Màn hình vừa (Tablet: 769px - 1024px) */
    @media (min-width: 769px) and (max-width: 1024px) {
        .block-container, [data-testid="block-container"] {
            padding: 1.2rem 1rem 3rem 1rem !important;
            max-width: 100% !important;
        }
        .app-top-toolbar {
            padding: 10px 14px !important;
            gap: 10px !important;
        }
        [data-testid="column"] {
            min-width: 48% !important;
            flex: 1 1 48% !important;
            margin-bottom: 8px !important;
        }
        .manual-app-title {
            font-size: 24px !important;
        }
    }

    @media (max-width: 992px) {
        .app-top-toolbar {
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 10px !important;
            padding: 10px 12px !important;
        }
        .toolbar-left {
            width: 100% !important;
            justify-content: space-between !important;
        }
        .toolbar-right-brand {
            width: 100% !important;
            justify-content: space-between !important;
            border-top: 1px dashed {c["border_subtle"]} !important;
            padding-top: 8px !important;
            margin-left: 0 !important;
        }
        .manual-app-title {
            font-size: 22px !important;
            letter-spacing: 0.06em !important;
        }
    }

    /* Điện thoại di động (Smartphones & Small Tablets: <= 768px) */
    @media (max-width: 768px) {
        /* Bố cục vùng đệm toàn trang trên điện thoại */
        .main .block-container,
        div[data-testid="stAppViewBlockContainer"],
        .block-container, [data-testid="block-container"] {
            padding: 0.75rem 0.5rem 2.8rem 0.5rem !important;
            width: 100% !important;
            max-width: 100% !important;
        }

        /* Sidebar tối ưu cho màn hình cảm ứng di động */
        section[data-testid="stSidebar"][aria-expanded="true"] {
            width: 88vw !important;
            min-width: unset !important;
            max-width: 340px !important;
            box-shadow: 0 0 40px rgba(0,0,0,0.88) !important;
        }

        /* Thẻ chỉ số Metric: Tự động xếp vừa vặn thay vì bị bẹp */
        [data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 8px !important;
        }

        /* Bảng tổng hợp APA 7: Chuyển lưới 2 cột sang 1 cột linh hoạt trên màn hình hẹp */
        div[style*="grid-template-columns: 1fr 1fr"],
        div[style*="grid-template-columns: repeat(2, 1fr)"],
        div[style*="grid-template-columns: repeat(3, 1fr)"],
        div[style*="grid-template-columns: repeat(4, 1fr)"] {
            grid-template-columns: 1fr !important;
            gap: 8px !important;
        }

        /* Hàng điều khiển nút bấm & thanh trạng thái */
        .symmetrical-action-card {
            height: auto !important;
            min-height: 48px !important;
            padding: 8px 12px !important;
            flex-wrap: wrap !important;
        }

        /* Bảng dữ liệu & Dataframe cuộn ngang mượt mà */
        div[data-testid="stTable"], div[data-testid="stDataFrame"], .stDataFrame {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            max-width: 100% !important;
        }
        table {
            min-width: 100% !important;
            font-size: 11.5px !important;
        }

        /* Hộp thoại Dialog & Popup trên Mobile */
        div[role="dialog"] {
            width: 96vw !important;
            max-width: 96vw !important;
            padding: 12px !important;
            border-radius: 16px !important;
        }

        /* Khối mã lệnh / trích dẫn cuộn mượt */
        pre, code {
            font-size: 11.5px !important;
            white-space: pre-wrap !important;
            word-break: break-word !important;
        }

        /* Thanh Tabs di chuyển ngang mượt mà trên cảm ứng */
        div[data-baseweb="tab-list"] {
            overflow-x: auto !important;
            overflow-y: hidden !important;
            flex-wrap: nowrap !important;
            white-space: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
            padding: 4px 4px !important;
            gap: 4px !important;
        }
        div[data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }
        div[data-baseweb="tab"] {
            flex-shrink: 0 !important;
            font-size: 11.5px !important;
            padding: 7px 10px !important;
            min-height: 38px !important;
        }

        /* Chữ và ô nhập liệu tối ưu không bị tự động phóng to trên iOS Safari */
        .stTextArea textarea, .stTextInput input, .stSelectbox select {
            font-size: 14px !important;
        }

        /* Nút bấm cảm ứng to rõ, chống bấm nhầm (Touch Target >= 44px) */
        .stButton button {
            min-height: 44px !important;
            font-size: 13px !important;
            width: 100% !important;
            -webkit-tap-highlight-color: transparent !important;
        }}

        /* Tiêu đề linh hoạt theo kích thước màn hình */
        h1 {{ font-size: 19px !important; }}
        h2 {{ font-size: 16px !important; }}
        h3 {{ font-size: 14px !important; }}

        /* Khung Hero Banner thu nhỏ vừa vặn */
        .hero-banner-box {{
            padding: 14px 16px !important;
        }}
        .hero-banner-title {{
            font-size: 15.5px !important;
        }}
        .hero-banner-desc {{
            font-size: 12.5px !important;
        }}
    }}
</style>
"""
