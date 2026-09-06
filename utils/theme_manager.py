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
            "glow_rgb": "0, 242, 254",
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
            "glow_rgb": "2, 132, 199",
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
            "glow_rgb": "16, 185, 129",
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
            "glow_rgb": "225, 29, 72",
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
            "glow_rgb": "6, 182, 212",
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
            "glow_rgb": "245, 158, 11",
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
            "glow_rgb": "2, 132, 199",
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
            "glow_rgb": "217, 119, 6",
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
            "glow_rgb": "0, 240, 255",
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
            "glow_rgb": "192, 132, 252",
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
    glow_rgb = c.get("glow_rgb", "0, 242, 254")
    
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');
    
    :root {{
        --theme-glow: {c["primary_accent"]};
        --theme-glow-rgb: {glow_rgb};
        --theme-bg-base: {c["bg_main"]};
        --theme-panel-bg: {c["bg_surface"]}E6;
        --theme-panel-border: rgba({glow_rgb}, 0.32);
        --theme-accent: {c["primary_accent"]};
        --theme-accent-hover: {c["border_hover"]};
        --theme-text-main: {c["text_primary"]};
        --theme-text-dim: {c["text_secondary"]};
        --theme-badge-bg: rgba({glow_rgb}, 0.14);

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
        --accent-glow: rgba({glow_rgb}, 0.28);
        
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
        background-image: radial-gradient(circle at 50% 10%, rgba({glow_rgb}, 0.06) 0%, transparent 60%) !important;
        background-attachment: fixed !important;
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
        font-weight: 800 !important;
        letter-spacing: -0.015em !important;
    }}
    h1 {{ font-size: 23px !important; margin-bottom: 8px !important; }}
    h2 {{ font-size: 18.5px !important; margin-bottom: 6px !important; }}
    h3 {{ font-size: 15.5px !important; margin-bottom: 4px !important; }}
    
    /* 1. KHUNG SIDEBAR GLASSMORPHISM SCI-FI */
    section[data-testid="stSidebar"] {{
        background: {c["bg_surface"]}E6 !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border-right: 1px solid rgba({glow_rgb}, 0.28) !important;
        box-shadow: 0 0 30px rgba({glow_rgb}, 0.08) !important;
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
        border: 1px solid rgba({glow_rgb}, 0.3) !important;
        border-radius: 8px !important;
        color: {c["primary_accent"]} !important;
        transition: all 0.2s ease !important;
    }}
    
    button[data-testid="stSidebarCollapseButton"]:hover {{
        background: {c["primary_accent"]} !important;
        color: #040914 !important;
        border-color: {c["primary_accent"]} !important;
        box-shadow: 0 0 12px rgba({glow_rgb}, 0.4) !important;
    }}

    /* Nút mũi tên mở lại Sidebar (khi Sidebar đã thu gọn) */
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
        box-shadow: 0 0 16px rgba({glow_rgb}, 0.35) !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }}
    
    div[data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover {{
        background: {c["primary_accent"]} !important;
        color: #040914 !important;
        transform: scale(1.08) !important;
        box-shadow: 0 0 20px var(--theme-glow) !important;
    }}
    
    /* Không gian làm việc chính */
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
        padding-top: 1.2rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 1.8rem !important;
        padding-right: 1.8rem !important;
        box-sizing: border-box !important;
    }}
    
    .sidebar-brand-box {{
        padding: 14px 16px;
        background: {c["bg_surface_elevated"]};
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba({glow_rgb}, 0.32);
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 0 18px rgba({glow_rgb}, 0.12);
    }}
    
    .sidebar-brand-title {{
        font-size: 15px;
        font-weight: 800;
        color: {c["text_primary"]};
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}
    
    .sidebar-brand-sub {{
        font-size: 11px;
        color: {c["primary_accent"]};
        font-weight: 700;
        margin-top: 4px;
        letter-spacing: 0.08em;
    }}

    .developer-pill {{
        display: inline-block;
        font-size: 10.5px;
        font-weight: 700;
        background: rgba({glow_rgb}, 0.14);
        color: {c["primary_accent"]};
        border: 1px solid rgba({glow_rgb}, 0.35);
        padding: 2px 8px;
        border-radius: 6px;
        margin-top: 6px;
        box-shadow: 0 0 8px rgba({glow_rgb}, 0.12);
    }}
    
    .menu-header-badge {{
        font-size: 10.5px;
        font-weight: 800;
        color: {c["text_muted"]};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 14px 0 6px 4px;
    }}

    /* Menu Chọn Màn Hình Làm Việc Bọc Khối Cao Cấp (HUD Chips) */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
        background: {c["bg_main"]} !important;
        border: 1px solid rgba({glow_rgb}, 0.22) !important;
        border-radius: 14px !important;
        padding: 6px !important;
        box-shadow: inset 0 0 12px rgba({glow_rgb}, 0.05) !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
        display: flex !important;
        align-items: center !important;
        background: {c["bg_surface_elevated"]} !important;
        border: 1px solid rgba({glow_rgb}, 0.18) !important;
        border-radius: 10px !important;
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
        border-color: {c["primary_accent"]} !important;
        box-shadow: 0 0 12px rgba({glow_rgb}, 0.22) !important;
        transform: translateX(2px) !important;
    }}
    
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
        background: {c["sidebar_active_bg"]} !important;
        border-color: {c["primary_accent"]} !important;
        border-left: 4px solid {c["primary_accent"]} !important;
        box-shadow: 0 0 16px rgba({glow_rgb}, 0.28) !important;
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
        font-weight: 800 !important;
    }}

    /* 2. GLOBAL HUD HEADER BAR (THƯƠNG HIỆU LƯỢNG TỬ ĐỒNG BỘ) */
    .app-top-toolbar, .synapse-header-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 18px;
        background: {c["bg_surface"]}E6;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba({glow_rgb}, 0.32);
        border-radius: 14px;
        margin-bottom: 16px;
        box-shadow: 0 0 24px rgba({glow_rgb}, 0.12);
        gap: 12px;
        flex-wrap: wrap;
        box-sizing: border-box;
        max-width: 100%;
    }}
    
    .brand-logo-cluster {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .brand-atom-icon {{
        font-size: 20px;
        color: {c["primary_accent"]};
        text-shadow: 0 0 12px var(--theme-glow);
        animation: atomSpin 18s linear infinite;
        display: inline-block;
    }}
    @keyframes atomSpin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    .brand-title {{
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: {c["text_primary"]};
        text-transform: uppercase;
    }}
    .brand-subtitle {{
        font-size: 10px;
        color: {c["primary_accent"]};
        font-weight: 700;
        letter-spacing: 0.12em;
    }}

    .header-meta-cluster {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }}
    .meta-chip {{
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba({glow_rgb}, 0.12);
        border: 1px solid rgba({glow_rgb}, 0.32);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11.5px;
        font-weight: 600;
        color: {c["text_primary"]};
        box-shadow: 0 0 8px rgba({glow_rgb}, 0.08);
        white-space: nowrap;
    }}
    .pulse-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 8px #10B981;
        animation: blink 1.6s infinite ease-in-out;
        display: inline-block;
    }}
    @keyframes blink {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.4; transform: scale(0.85); }}
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
        font-weight: 800;
        text-shadow: 0 0 8px rgba({glow_rgb}, 0.35);
    }}

    /* 3. THẺ BOX, BANNER & CONTAINER GLASSMORPHISM */
    .hero-banner-box, .manual-hero-banner {{
        background: {c["bg_surface"]}E6;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba({glow_rgb}, 0.35);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 18px;
        box-shadow: 0 0 30px rgba({glow_rgb}, 0.12);
        position: relative;
        overflow: hidden;
    }}
    .hero-banner-title, .manual-app-title {{
        font-size: 20px;
        font-weight: 900;
        color: {c["text_primary"]};
        letter-spacing: -0.01em;
        margin-bottom: 6px;
        text-shadow: 0 0 12px rgba({glow_rgb}, 0.35);
    }}
    .hero-banner-desc {{
        color: {c["text_secondary"]};
        font-size: 13.5px;
        line-height: 1.6;
        max-width: 900px;
    }}

    .frame-box, .tab-content-card, .evidence-card, .apa-ref-card {{
        background: {c["bg_surface"]}E6;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba({glow_rgb}, 0.28);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 0 20px rgba({glow_rgb}, 0.08);
        transition: all 0.2s ease;
    }}
    .frame-box:hover, .tab-content-card:hover, .evidence-card:hover, .apa-ref-card:hover {{
        border-color: {c["primary_accent"]};
        box-shadow: 0 0 24px rgba({glow_rgb}, 0.18);
        transform: translateY(-1px);
    }}

    /* 4. METRIC KPI CARDS SCI-FI */
    .metric-card-full {{
        background: {c["bg_surface"]}E6;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba({glow_rgb}, 0.32);
        border-radius: 14px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        box-shadow: 0 0 20px rgba({glow_rgb}, 0.10);
        transition: all 0.2s ease;
    }}
    .metric-card-full:hover {{
        border-color: {c["primary_accent"]};
        box-shadow: 0 0 25px rgba({glow_rgb}, 0.22);
        transform: translateY(-2px);
    }}
    .metric-title {{
        font-size: 11px;
        font-weight: 800;
        color: {c["primary_accent"]};
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    .metric-value {{
        font-size: 24px;
        font-weight: 900;
        color: {c["text_primary"]};
        line-height: 1.15;
        margin: 4px 0;
        letter-spacing: -0.02em;
        text-shadow: 0 0 10px rgba({glow_rgb}, 0.3);
    }}
    .metric-sub {{
        font-size: 11px;
        color: {c["text_muted"]};
    }}

    /* 5. FORM CONTROLS & TERMINAL INPUTS */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {{
        background-color: {c["bg_surface_elevated"]} !important;
        color: {c["text_primary"]} !important;
        border: 1px solid rgba({glow_rgb}, 0.3) !important;
        border-radius: 10px !important;
        font-size: 13.5px !important;
        transition: all 0.2s ease !important;
    }}
    .stTextArea textarea:focus, .stTextInput input:focus {{
        border-color: {c["primary_accent"]} !important;
        box-shadow: 0 0 16px rgba({glow_rgb}, 0.4) !important;
        outline: none !important;
    }}

    .stButton button {{
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        height: 46px !important;
        border: 1px solid rgba({glow_rgb}, 0.32) !important;
        background: {c["bg_surface_elevated"]} !important;
        color: {c["text_primary"]} !important;
        transition: all 0.2s ease !important;
    }}
    .stButton button:hover {{
        background-color: {c["sidebar_hover_bg"]} !important;
        border-color: {c["primary_accent"]} !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 16px rgba({glow_rgb}, 0.35) !important;
        transform: translateY(-1px) !important;
    }}
    
    .stButton button[kind="primary"] {{
        background: {c["primary_gradient"]} !important;
        border: 1px solid {c["primary_accent"]} !important;
        color: #FFFFFF !important;
        font-size: 13.5px !important;
        font-weight: 800 !important;
        box-shadow: 0 0 20px rgba({glow_rgb}, 0.45) !important;
    }}

    .stDownloadButton button {{
        border-radius: 10px !important;
        font-size: 12.5px !important;
        font-weight: 700 !important;
        padding: 6px 14px !important;
        border: 1px solid rgba({glow_rgb}, 0.32) !important;
        background: {c["bg_surface_elevated"]} !important;
        color: {c["text_primary"]} !important;
        transition: all 0.2s ease !important;
    }}
    .stDownloadButton button:hover {{
        border-color: {c["primary_accent"]} !important;
        box-shadow: 0 0 14px rgba({glow_rgb}, 0.3) !important;
    }}

    /* 6. STREAMLIT EXPANDERS & TABS */
    div[data-testid="stExpander"] {{
        background: {c["bg_surface"]}E6 !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba({glow_rgb}, 0.28) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 16px rgba({glow_rgb}, 0.08) !important;
    }}
    div[data-testid="stExpander"] summary {{
        color: {c["text_primary"]} !important;
        font-weight: 700 !important;
    }}

    div[data-baseweb="tab-list"] {{
        background-color: {c["bg_surface"]} !important;
        border: 1px solid rgba({glow_rgb}, 0.28) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
        box-shadow: 0 0 16px rgba({glow_rgb}, 0.08) !important;
    }}
    div[data-baseweb="tab"] {{
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 12.5px !important;
        color: {c["text_secondary"]} !important;
        transition: all 0.18s ease !important;
    }}
    div[data-baseweb="tab"][aria-selected="true"] {{
        background: rgba({glow_rgb}, 0.18) !important;
        color: {c["primary_accent"]} !important;
        border: 1px solid rgba({glow_rgb}, 0.4) !important;
        box-shadow: 0 0 12px rgba({glow_rgb}, 0.25) !important;
    }}

    /* 7. CUSTOM SCI-FI BADGES */
    .custom-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 8px;
        box-shadow: 0 0 8px rgba(0,0,0,0.15);
    }}
    .custom-badge.badge-blue {{
        background: rgba(0, 242, 254, 0.14);
        color: #38BDF8;
        border: 1px solid rgba(0, 242, 254, 0.4);
    }}
    .custom-badge.badge-green {{
        background: rgba(16, 185, 129, 0.14);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }}
    .custom-badge.badge-rose {{
        background: rgba(244, 63, 94, 0.14);
        color: #FB7185;
        border: 1px solid rgba(244, 63, 94, 0.4);
    }}
    .custom-badge.badge-diamond-seed {{
        background: rgba(234, 67, 53, 0.22);
        color: #FF8A80;
        border: 1px solid rgba(234, 67, 53, 0.5);
        box-shadow: 0 0 10px rgba(234, 67, 53, 0.3);
    }}
    .custom-badge.badge-diamond-root {{
        background: rgba(124, 58, 237, 0.22);
        color: #C4B5FD;
        border: 1px solid rgba(124, 58, 237, 0.5);
        box-shadow: 0 0 10px rgba(124, 58, 237, 0.3);
    }}
    .custom-badge.badge-diamond-frontier {{
        background: rgba(2, 132, 199, 0.22);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.5);
        box-shadow: 0 0 10px rgba(2, 132, 199, 0.3);
    }}

    .quick-nav-card {{
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 8px;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px rgba({glow_rgb}, 0.16);
        transition: all 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.22);
    }}
    .quick-nav-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 0 28px rgba({glow_rgb}, 0.32);
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
    .quick-nav-card .qnav-title {{
        font-size: 14px;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .quick-nav-card .qnav-desc {{
        font-size: 11.5px;
        color: rgba(255, 255, 255, 0.92) !important;
        line-height: 1.4;
        margin: 0;
        font-weight: 500;
    }}
</style>
"""
