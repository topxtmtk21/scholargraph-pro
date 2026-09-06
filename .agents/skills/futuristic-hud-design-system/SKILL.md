---
name: futuristic-hud-design-system
description: Quy chuẩn và cẩm nang toàn diện để thiết kế giao diện Futuristic Sci-Fi Glassmorphism HUD Dashboard (Synapse Academic / Quantum Deck) đạt chuẩn quốc tế, tương phản WCAG AAA/AA, chống lỗi Streamlit Markdown, hỗ trợ đa màn hình Blob URL và tối ưu hóa 100% cho Online, Mobile, Tablet & Màn Hình Lớn Ultra-Wide.
---

# 🌌 Futuristic Sci-Fi Glassmorphism HUD UI/UX Design Skill

Cẩm nang đúc kết các nguyên tắc thiết kế, quy chuẩn CSS Tokens, kiến trúc giao diện tương lai (**Futuristic Sci-Fi Glassmorphism HUD Dashboard**) và các bài học kỹ thuật thực chiến giải quyết triệt để lỗi hiển thị trong các dự án phức tạp trên mọi kích thước màn hình từ Mobile, Tablet, Desktop tới Ultra-Wide 4K.

---

## 💎 1. Triết Lý Thiết Kế: Quantum HUD & Sci-Fi Aesthetics

Giao diện HUD (Heads-Up Display) tương lai kết hợp Glassmorphism tạo cảm giác như đang điều khiển một phi thuyền nghiên cứu lượng tử hiện đại:
1. **Nền Không Gian Sâu (Deep Space Base)**: Sử dụng các tone màu siêu tối `#030712`, `#040914`, `#0B0F19` kết hợp với `radial-gradient(circle at 50% 20%, rgba(var(--glow-rgb), 0.08) 0%, transparent 70%)` tạo chiều sâu vô tận.
2. **Kính Mờ Phản Quang (Aero Glassmorphism)**:
   - `background: rgba(var(--panel-bg-rgb), 0.82);`
   - `backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);`
   - `border: 1px solid rgba(var(--glow-rgb), 0.32);`
   - `box-shadow: 0 0 24px rgba(var(--glow-rgb), 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.1);`
3. **Hiệu Ứng Dạ Quang Neon (Neon Luminescence & Pulsing Glow)**:
   - Các điểm nhấn chính sử dụng dải màu neon: Cyan `#00F2FE`, Emerald `#10B981`, Amber `#F59E0B`, Purple `#C084FC`, Sky `#38BDF8`.
   - Đèn chỉ báo trạng thái (Pulse Dot) có animation nhịp thở (`keyframes blink`).
   - Luồng hạt photon chuyển động $60\text{ FPS}$ mô phỏng dòng chảy tri thức/dữ liệu.

---

## 🎨 2. Hệ Thống CSS Variables & Bảng Màu Tương Phản Đạt Chuẩn WCAG AAA/AA

Mọi thành phần giao diện không bao giờ hard-code mã màu tĩnh mà luôn kế thừa qua biến hệ thống:

```css
:root {
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
}

/* Quy tắc độ tương phản (Contrast Ratio Rule) */
/* Text thường: Tương phản ≥ 7.0:1 (WCAG AAA) hoặc ≥ 4.5:1 (WCAG AA) */
/* Nút bấm / Badge: Luôn có border phát sáng để không bị chìm vào nền */
```

---

## 🧩 3. Ba Thành Phần Giao Diện Cốt Lõi (Architecture Layout)

### A. Top Header HUD Bar (Thanh Định Danh Tối Tân)
Bao gồm:
1. **Brand Cluster**: Biểu tượng nguyên tử ⚛️ quay đều (`animation: atomSpin 18s linear infinite;`) + Tên dự án/hệ thống chữ in hoa tinh xảo.
2. **Breadcrumb Bar**: Định vị phân hệ với icon la bàn SVG và dấu gạch chéo `/`.
3. **Dynamic Meta Chips**:
   - `📁 PROJECT`: Tên đề tài/phiên làm việc hiện tại.
   - `👤 USER`: Tên và quyền hạn (Super Admin / Researcher).
   - `🟢 STATUS: ACTIVE`: Đèn LED Neon phát sáng nhịp thở.
   - `🕒 REALTIME CLOCK`: Đồng hồ điện tử chuẩn font monospace (`JetBrains Mono`).

### B. Slim Vertical Dock Bar (Thanh Công Cụ Nhanh Đứng)
- Thanh dock hẹp ($48\text{px}$) đặt sát cạnh trái canvas/nội dung.
- Các nút biểu tượng bo góc ($10\text{px}$), kính mờ, có tooltip khi rê chuột.
- Chuyển layout nhanh, bật/tắt hiệu ứng truy vết, mở Drawer chú thích `📖`, mở Màn hình phụ `↗️`, căn giữa toàn cảnh `🎯`.

### C. HUD Panel Cyber Cards (Thẻ Thông Tin Khối Kính)
- Thẻ card chia 2 phần: Header nền pha loãng phát sáng + Body cuộn mượt mà (`overflow-y: auto`).
- Bo góc $12\text{px} - 14\text{px}$, viền phát sáng nhẹ, hover có hiệu ứng nhấc lên $1\text{px}$ (`transform: translateY(-1px)`).

---

## ⚠️ 4. Quy Tắc Vàng Xử Lý Streamlit & Web Rendering (Anti-Bugs)

### 🚨 Cạm bẫy 1: Lỗi Markdown Parser hiển thị mã HTML thô
- **Nguyên nhân**: Trong Streamlit `st.markdown(..., unsafe_allow_html=True)`, nếu chuỗi HTML nhiều dòng có **thụt lề 4 dấu cách (4 spaces indentation)** sau một dòng trống, bộ phân tích cú pháp Markdown sẽ coi đó là **Indented Code Block (`<pre><code>`)** và in nguyên xi thẻ HTML ra màn hình.
- **Quy tắc khắc phục**:
  ```python
  # ❌ SAI: Thụt lề 4 dấu cách bên trong f-string
  st.markdown(f"""
  <div>
      <div class="header">  <!-- 4 spaces gây lỗi! -->
          ...
      </div>
  </div>
  """, unsafe_allow_html=True)

  # ✅ ĐÚNG: Nối chuỗi liền mạch hoặc viết sát lề 0 spaces
  header_html = (
      '<div class="synapse-header-bar">'
      '<div class="brand-logo-cluster">...</div>'
      '</div>'
  )
  st.markdown(header_html, unsafe_allow_html=True)
  ```

### 🚨 Cạm bẫy 2: Lỗi Data URI bị trình duyệt chặn khi mở Màn Hình Phụ (Cửa Sổ Mới)
- **Nguyên nhân**: Trình duyệt hiện đại (Chrome, Edge, Safari) mặc định chặn điều hướng cấp cao tới `data:text/html` (`Not allowed to navigate top frame to data URL`).
- **Quy tắc khắc phục**: Sử dụng chuẩn **W3C Blob Object URL** kết hợp với JavaScript `window.open`:
  ```javascript
  // ✅ Giải pháp chuẩn 100% cross-browser
  var binary = atob(base64Html);
  var bytes = new Uint8Array(binary.length);
  for (var i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
  }
  var blob = new Blob([bytes], { type: 'text/html;charset=utf-8' });
  var blobUrl = URL.createObjectURL(blob);
  var win = window.open(blobUrl, '_blank');
  
  // Fallback an toàn nếu dính popup blocker
  if (!win || win.closed || typeof win.closed === 'undefined') {
      var fallbackWin = window.open('', '_blank');
      if (fallbackWin) {
          fallbackWin.document.open();
          fallbackWin.document.write(new TextDecoder().decode(bytes));
          fallbackWin.document.close();
      }
  }
  ```

---

## 📱 5. Ma Trận Đa Màn Hình Toàn Diện (Multi-Screen Responsive Matrix)

Hệ thống được thiết kế theo nguyên tắc thích ứng tự nhiên (Fluid Adaptive Design) hỗ trợ 4 phân khúc màn hình:

| Thiết Bị / Phân Khúc | Độ Rộng Viewport | Bố Cục Cột (Columns) | Chiều Cao Iframe/Canvas | Trải Nghiệm Điều Khiển |
| :--- | :--- | :--- | :--- | :--- |
| **Mobile (Điện thoại)** | $< 768\text{px}$ | 1 cột đơn ($100\%$ width) | $\min 520\text{px}$ hoặc $75\text{vh}$ | Header xếp dọc, dock thu nhỏ $38\text{px}$, chạm 1-tap, cuộn ngang bảng cảm ứng |
| **Tablet (Máy tính bảng)** | $768\text{px} - 1024\text{px}$ | 2 cột linh hoạt ($2\times 2$ grid) | $\min 600\text{px}$ hoặc $80\text{vh}$ | Header ngang tối giản, Inspector góc an toàn, hỗ trợ cử chỉ vuốt 2 ngón |
| **Desktop Chuẩn (Laptop/PC)**| $1025\text{px} - 1440\text{px}$| $3 - 4$ cột tiêu chuẩn | $\min 680\text{px}$ hoặc $82\text{vh}$ | Đầy đủ Slim Dock đứng, Drawer chú thích trượt ra, Hover tức thì |
| **Ultra-Wide & 4K** | $> 1440\text{px}$ ($2\text{K}/4\text{K}$) | Tối đa $1720\text{px}$ căn giữa | $\min 720\text{px} - 800\text{px}$ | Nền không gian sâu bao quanh, không bị kéo giãn méo tỷ lệ font chữ |

---

## 👆 6. Giao Thức Cảm Ứng Chạm (Touch Gestures & Single-Tap Protocol)

Trên thiết bị di động và máy tính bảng, không có sự kiện rê chuột (`hover`/`mousemove`). Cần áp dụng giao thức chuyển hóa thông minh:
1. **Chạm 1 chạm vào Node (Node Single-Tap)**:
   - Bắt sự kiện `network.on('click')` và `network.on('selectNode')`.
   - Cập nhật `hoveredNodeId = params.nodes[0]`.
   - Kích hoạt luồng sáng **Laser Beam Stream** phát sáng tức thì nối giữa node được chọn và các bài báo liên kết.
   - Hiển thị **Smart HUD Hover Inspector** ở vị trí an toàn (góc trên màn hình) với đầy đủ Tác giả, Năm, Tạp chí, và Tóm tắt AI.
2. **Chạm 1 chạm vào Cạnh Mũi Tên (Edge Single-Tap)**:
   - Bắt sự kiện `network.on('selectEdge')`.
   - Cập nhật `hoveredEdgeId = params.edges[0]`.
   - Hiển thị **Edge Epistemic Inspector** (màu hổ phách Amber, font Roboto Light $10.5\text{px}$) giải thích độ trễ tiếp thu tri thức.
3. **Chạm vào Vùng Trống (Canvas Background Tap)**:
   - Khi `params.nodes.length === 0 && params.edges.length === 0`, tự động ẩn toàn bộ Inspector và khôi phục trạng thái mạng lưới bình thường.

---

## 🎯 7. Quy Chuẩn Vùng Chạm Tối Thiểu 44px (Fitts's Ergonomic Law)

- Mọi phần tử tương tác (Buttons, Quick Nav Chips, Sidebar Toggles, Theme Switcher, Sliders) trên Mobile phải có kích thước tối thiểu **$44\text{px} \times 44\text{px}$** để đảm bảo ngón tay cái thao tác dễ dàng không bị bấm trượt.
- Bổ sung `touch-action: manipulation;` để triệt tiêu độ trễ $300\text{ms}$ chạm kép mặc định trên trình duyệt di động WebKit/Blink.
- Khóa kích thước font `input, select, textarea` tối thiểu $14\text{px} - 16\text{px}$ để tránh iOS Safari tự động phóng to giao diện (auto-zoom) khi focus.

---

## 🌊 8. Chống Tràn Trang Ngang & Cuộn Quán Tính (Zero Horizontal Overflow & Momentum Scrolling)

1. **Khóa tràn trang cấp độ gốc (Root Viewport Containment)**:
   ```css
   .main .block-container {
       max-width: 100% !important;
       overflow-x: hidden !important;
       padding-bottom: calc(40px + env(safe-area-inset-bottom, 0px)) !important;
   }
   ```
2. **Cuộn quán tính siêu mượt cho các bảng ma trận (Smooth Touch Scroll)**:
   ```css
   .table-responsive, [data-testid="stTable"], [data-testid="stDataFrame"] {
       overflow-x: auto !important;
       -webkit-overflow-scrolling: touch !important;
       overscroll-behavior-x: contain !important;
   }
   ```
3. **Bảo Vệ Tai Thỏ & Thanh Điều Hướng Ảo (Safe Area Insets)**:
   - Luôn sử dụng `env(safe-area-inset-bottom)` và `env(safe-area-inset-top)` để các nút hành động dưới đáy không bị che lấp bởi Home Bar trên iPhone/iPad.

---

## 🔍 9. Tìm Kiếm Đa Tiêu Chí Đồ Thị & Cẩm Nang Thuật Ngữ Thông Minh (Multi-Facet Search)

1. **Bộ Tìm Kiếm Node Đồ Thị (Smart Node Search Engine)**:
   - Hỗ trợ phân giải đa tiêu chí: DOI chuẩn (`10.xxxx` hoặc link đầy đủ), Tên tác giả (viết tắt `Nguyen, V. A.` hoặc họ/tên đầy đủ), Năm xuất bản (`2024`, `>2020`, `<2015`), Tiêu đề/Từ khóa, Tạp chí/Venue và Tóm tắt (Abstract).
   - Tự động làm mờ các node không liên quan ($0.15$ opacity), bật vòng hào quang phát sáng quanh kết quả tìm thấy và focus camera phóng to mượt mà $400\text{ms}$.
2. **Bộ Tìm Kiếm Nội Bộ Trong Khay Hướng Dẫn (Legend Drawer Search)**:
   - Lọc thời gian thực các thẻ định nghĩa thuật ngữ ($F_0, R_1-R_3, F_1-F_3$, 4 loại mũi tên, nguyên tắc kích thước Price's Law, điều tốc photon) khi người dùng gõ từ khóa.
3. **Diễn Giải Ngữ Nghĩa Khi Lọc Phân Tầng (Filter Context Explanation)**:
   - Khi người dùng lọc nhanh (ví dụ: chỉ xem $F_1-F_3$), hệ thống tự động giải thích trong Smart Inspector lý do vì sao một số node không có mũi tên hiển thị (do liên kết với $F_0$ hoặc tầng $R$ đang bị ẩn bởi bộ lọc).

---

## 🔄 10. Tự Động Căn Khớp Khung Nhìn (Orientation & Viewport Auto-Fitting)

1. **Khớp hướng thiết bị (Orientation Fit)**:
   - Bắt sự kiện `window.addEventListener('orientationchange')` và `resize` để tự động tính toán lại kích thước mạng lưới và gọi `network.fit()` sau $250\text{ms}$.
2. **Chế độ Màn hình phụ $100\text{vh}$ Toàn Năng (Full Device Dedicated Viewport)**:
   - Khi mở cửa sổ mới hoặc chế độ toàn màn hình (`⛶`), iframe tự động mở rộng $100\text{vw} \times 100\text{vh}$ không viền thừa, tối ưu hóa $100\%$ diện tích tương tác cho màn hình di động và tablet.
