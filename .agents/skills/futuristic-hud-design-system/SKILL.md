---
name: futuristic-hud-design-system
description: Quy chuẩn thiết kế giao diện Futuristic Sci-Fi Glassmorphism HUD Dashboard và cẩm nang UI/UX chuyên sâu áp dụng cho mọi ứng dụng hiện đại: nguyên tắc không che khuất vùng quan sát, tương phản WCAG AAA/AA, chống tràn trang, cử chỉ chạm 1-tap, tìm kiếm đa tiêu chí thời gian thực và tự động căn khớp đa màn hình.
---

# 🌌 Modern Futuristic UI/UX & Glassmorphism HUD Design System

Cẩm nang kiến trúc giao diện người dùng chuyên sâu, đúc kết các quy chuẩn thiết kế UI/UX hiện đại, hệ thống CSS Variables thông minh, và các nguyên tắc công thái học tương tác (Ergonomics) áp dụng cho **bất kỳ ứng dụng web, ứng dụng di động, dashboard phân tích dữ liệu hay nền tảng SaaS phức tạp nào**.

---

## 💎 1. Triết Lý Thiết Kế: Chiều Sâu Lượng Tử & Giao Diện Kính Mờ (Quantum HUD & Aero Glassmorphism)

Giao diện chất lượng cao phải tạo được sự kinh ngạc (Wow factor) ngay từ cái nhìn đầu tiên và mang lại cảm giác mượt mà, chuyên nghiệp:
1. **Nền Không Gian Sâu (Deep Space Base)**: Sử dụng các tone màu siêu tối `#030712`, `#040914`, `#0B0F19` kết hợp với `radial-gradient(circle at 50% 20%, rgba(var(--glow-rgb), 0.08) 0%, transparent 70%)` tạo chiều sâu vô tận.
2. **Kính Mờ Phản Quang (Aero Glassmorphism)**:
   - `background: rgba(var(--panel-bg-rgb), 0.82);`
   - `backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);`
   - `border: 1px solid rgba(var(--glow-rgb), 0.32);`
   - `box-shadow: 0 0 24px rgba(var(--glow-rgb), 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.1);`
3. **Dạ Quang Neon & Luồng Năng Lượng 60 FPS (Neon Luminescence & Particle Streams)**:
   - Sử dụng dải màu neon công nghệ: Cyan `#00F2FE`, Emerald `#10B981`, Amber `#F59E0B`, Purple `#C084FC`, Sky `#38BDF8`.
   - Luồng hạt photon chuyển động $60\text{ FPS}$ mô phỏng dòng chảy dữ liệu.
   - Hào quang phát sáng nhịp thở (`pulse glow`) bao quanh các đối tượng hạt nhân.

---

## 🎨 2. Hệ Thống CSS Variables & Tiêu Chuẩn Tương Phản Quốc Tế (WCAG AAA/AA)

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
/* Nút bấm / Badge: Luôn có border phát sáng để không bị chìm vào nền tối */
```

---

## 👁️ 3. Nguyên Tắc Không Che Khuất Vùng Quan Sát (Zero-Occlusion Layout Principle)

Trong các giao diện hiển thị đồ thị, bản đồ hoặc dữ liệu tương tác trực quan:
1. **Không Bao Giờ Đè Bảng Thông Tin Lên Đối Tượng Thao Tác (No Overlapping Tooltips)**:
   - Thay vì dùng popover/tooltip lơ lửng ngay tại vị trí con trỏ chuột (làm che khuất node xung quanh và các đường kết nối), hãy định vị **Smart Inspector** tại các **vùng an toàn cố định** (Safe Anchors): góc trên bên trái (cho Node) và góc trên bên phải (cho Mũi tên/Đường nối).
2. **Khay Chú Thích Trượt (Slide-Out Legend Drawer)**:
   - Các bảng hướng dẫn, định nghĩa thuật ngữ, quy ước mã màu được thu gọn vào thanh dock cạnh trái và chỉ trượt ra khi người dùng chủ động mở (`📖`), không bao giờ chiếm dụng không gian hiển thị chính.
3. **Phân Vùng Rõ Ràng Giữa Vùng Tổng Quan & Vùng Chi Tiết (Master-Detail Architecture)**:
   - Phần trên là không gian đồ thị tương tác $3D$/$2D$; phần dưới là bảng chi tiết dữ liệu (Data Grid/Matrix) có thể đóng/mở linh hoạt.

---

## ⚖️ 4. Quy Luật Tỷ Lệ Trực Quan & Phân Cấp Dữ Liệu (Visual Hierarchy & Relative Scale Law)

Mỗi đối tượng trên giao diện phải phản ánh chính xác trọng số dữ liệu của nó (Data-Driven Visual Scale):
1. **Kích Thước Đối Tượng Theo Hàm Logarit (Logarithmic Scaling Law)**:
   - Các đối tượng có số lượng tương tác lớn (ví dụ: Số lượt trích dẫn, Lượng truy cập) được tính kích cỡ theo hàm $S = S_{\text{base}} + k \cdot \log(V + 1)$.
   - Đối tượng trung tâm ($F_0$) luôn có kích cỡ lớn nhất và hiệu ứng hào quang phát sáng nhịp thở.
2. **Mã Hóa Màu Sắc Theo Ngữ Nghĩa Epistemic (Semantic Color Coding)**:
   - 🔷 **Xanh Sky (Nét liền)**: Luồng kế thừa 1 chiều trực tiếp.
   - 🔶 **Vàng Kim (2 đầu mũi tên)**: Mối quan hệ tương hỗ / đối thoại 2 chiều.
   - 🔮 **Tím Neon (Đứt nét)**: Liên kết bắc cầu xuyên tầng.
   - 🟢 **Ngọc Lục (Chấm nhỏ)**: Mối quan hệ nội bộ cùng phân tầng.

---

## 📱 5. Ma Trận Đa Màn Hình & Tự Động Khớp Thiết Bị (Multi-Screen Fluid Adaptive Matrix)

| Thiết Bị / Phân Khúc | Độ Rộng Viewport | Bố Cục Cột (Columns) | Chiều Cao Iframe/Canvas | Trải Nghiệm Điều Khiển |
| :--- | :--- | :--- | :--- | :--- |
| **Mobile (Điện thoại)** | $< 768\text{px}$ | 1 cột đơn ($100\%$ width) | $\min 520\text{px}$ hoặc $75\text{vh}$ | Header xếp dọc, dock thu nhỏ $36\text{px}$, chạm 1-tap, cuộn ngang bảng cảm ứng |
| **Tablet (Máy tính bảng)** | $768\text{px} - 1024\text{px}$ | 2 cột linh hoạt ($2\times 2$ grid) | $\min 600\text{px}$ hoặc $80\text{vh}$ | Header ngang tối giản, Inspector góc an toàn, hỗ trợ cử chỉ vuốt 2 ngón |
| **Desktop Chuẩn (Laptop/PC)**| $1025\text{px} - 1440\text{px}$| $3 - 4$ cột tiêu chuẩn | $\min 680\text{px}$ hoặc $82\text{vh}$ | Đầy đủ Slim Dock đứng, Drawer chú thích trượt ra, Hover tức thì |
| **Ultra-Wide & 4K** | $> 1440\text{px}$ ($2\text{K}/4\text{K}$) | Tối đa $1720\text{px}$ căn giữa | $\min 720\text{px} - 800\text{px}$ | Nền không gian sâu bao quanh, không bị kéo giãn méo tỷ lệ font chữ |

### Tự Động Căn Khớp Khi Xoay Màn Hình (Orientation Auto-Fitting)
- Bắt sự kiện `window.addEventListener('orientationchange')` và `resize` để tự động tính toán lại tỷ lệ zoom và gọi hàm `network.fit()` sau $250\text{ms}$.

---

## 👆 6. Giao Thức Chuyển Hóa Cảm Ứng (Touch-First & Single-Tap Protocol)

Trên màn hình cảm ứng di động/tablet (không có sự kiện rê chuột `hover`):
1. **Chạm 1-chạm vào Node**:
   - Bắt sự kiện `network.on('click')` và `network.on('selectNode')`.
   - Cập nhật `hoveredNodeId`, kích hoạt luồng sáng **Laser Beam Stream** phát sáng tức thì và mở **Smart Inspector** ở vị trí an toàn.
2. **Chạm 1-chạm vào Đường Nối/Mũi Tên**:
   - Mở bảng phân tích ngữ nghĩa (Epistemic Inspector) giải thích độ trễ thời gian và vai trò liên kết.
3. **Chạm vào Vùng Trống (Canvas Tap)**:
   - Tự động ẩn Inspector và khôi phục trạng thái mạng lưới toàn cảnh.
4. **Quy Chuẩn Vùng Chạm Tối Thiểu 44px (Fitts's Ergonomic Law)**:
   - Mọi nút bấm, tab điều hướng và thanh trượt phải có kích thước tối thiểu **$44\text{px} \times 44\text{px}$** kèm `touch-action: manipulation;` để triệt tiêu độ trễ $300\text{ms}$ trên WebKit/Blink.

---

## 🌊 7. Chống Tràn Trang Ngang & Cuộn Quán Tính (Zero Horizontal Overflow & Momentum Scrolling)

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

## 🔍 8. Tìm Kiếm Đa Tiêu Chí Thời Gian Thực (Real-Time Multi-Facet Search Engine)

1. **Bộ Tìm Kiếm Đối Tượng Đa Chiều (Smart Node Search)**:
   - Cho phép tìm kiếm kết hợp nhiều trường: Mã định danh (ID/DOI), Tác giả (viết tắt / đầy đủ), Năm/Khoảng năm (`2024`, `>2020`), Tiêu đề, Khái niệm, Tạp chí, Phân tầng.
   - Khi tìm thấy: Làm mờ đối tượng phụ trợ ($0.15$ opacity), bật viền phát sáng quanh kết quả và focus camera phóng to mượt mà $400\text{ms}$.
2. **Bộ Tìm Kiếm Nội Bộ Trong Khay Hướng Dẫn (Drawer Realtime Filter)**:
   - Lọc nhanh các thẻ định nghĩa thuật ngữ, quy ước màu và hướng dẫn sử dụng ngay khi người dùng gõ từ khóa vào ô tìm kiếm của Drawer.
3. **Diễn Giải Ngữ Cảnh Khi Lọc Dữ Liệu (Filter Context Awareness)**:
   - Khi một đối tượng hiển thị cô lập do bộ lọc (Filter Active), giao diện phải giải thích rõ ràng lý do liên kết bị ẩn để người dùng không bị hiểu lầm là lỗi dữ liệu.

---

## 🧭 9. Quy Chuẩn Thanh Công Cụ 1 Dòng Tinh Gọn & Popover Tự Đóng (Single-Row Toolbar & Click-Outside Popovers)

Khi một giao diện trực quan hóa dữ liệu có hơn 10 nút bấm điều khiển:
1. **Tuyệt đối không để `flex-wrap: wrap` tràn thành 2 hàng** làm che khuất đồ thị hoặc khung hiển thị chính.
2. **Kiến trúc phân nhóm điều khiển**:
   - **Thanh chính (Primary Bar)**: Chỉ giữ lại các thao tác cốt lõi nhất: `👁️ Focus Mode`, `🔍 Tìm kiếm`, `📑 Lọc tầng ▾`, `⚡ Phân loại ▾`, `🕸️ Bố cục ▾`, `⚡ Tốc độ (Slider)`, `🔍+`, `🔍-`, `⛶ Toàn màn hình`.
   - **Khay Popover Tùy Biến (`✨ Hiệu ứng ▾`)**: Gom toàn bộ các toggle hiệu ứng phụ (Hạt photon, Tia laser, Hào quang nhịp thở, Mũi tên động, Đổi chế độ nhãn, Tua năm, Truy vết phả hệ) vào một Popover dạng kính mờ gọn gàng.
3. **Cơ chế tự đóng khi nhấp ngoài (Click-Outside Auto-Dismiss)**:
   - Luôn lắng nghe sự kiện `document.addEventListener('click', ...)` để tự động đóng Popover khi người dùng nhấp chuột vào bất kỳ vị trí nào khác trên canvas.

---

## 📜 10. Triệt Tiêu Thanh Cuộn Lồng Cục Bộ (Zero Nested Inner Scrollbars in Master-Detail Decks)

1. **Hiện tượng lỗi**: Khi khung hiển thị chi tiết (Bottom Deck) đã có chiều cao rộng rãi (ví dụ: $750\text{px}$), nhưng các phần tử con (như Tóm tắt, Nhánh đồng trích dẫn) lại bị gán cứng `max-height: 85px; overflow-y: auto;`, dẫn đến việc xuất hiện các thanh cuộn con xấu xí và chật chội trong khi khoảng trống bên ngoài bị lãng phí.
2. **Quy tắc Vàng**:
   - Gỡ bỏ hoàn toàn `max-height` và `overflow-y: auto` trên các khối nội dung con (`#selAbstract`, `#selLineageList`, `.detail-abstract-pane`, `.detail-cocitation-pane`).
   - Thiết lập `max-height: none; overflow-y: visible;` để văn bản tóm tắt và cây phả hệ mở rộng mượt mà, hòa nhập tự nhiên vào tổng thể khung hiển thị.

---

## 📱 11. Suy Giảm Mượt Mà Cảm Ứng vs Rê Chuột (Hover-to-Inline Touch Graceful Degradation)

1. **Vấn đề trên màn hình cảm ứng (Mobile/Tablet)**: Trên thiết bị di động, thao tác chuột `:hover` không tồn tại, khiến các thẻ giải nghĩa bay (`.topo-tooltip-box`) không thể kích hoạt hoặc bị hiển thị sai lệch/tràn màn hình.
2. **Giải pháp Responsive tự động chuyển đổi**:
   ```css
   /* Desktop: Hover hiện Tooltip bay */
   @media (min-width: 769px) {
       .topo-tooltip-box {
           position: absolute;
           visibility: hidden;
           opacity: 0;
           bottom: 108%;
           left: 50%;
           transform: translateX(-50%) translateY(8px);
           transition: all 0.2s ease-out;
       }
       .topo-badge-item:hover .topo-tooltip-box {
           visibility: visible;
           opacity: 1;
           transform: translateX(-50%) translateY(0);
       }
   }
   /* Mobile/Tablet: Tự động chuyển thành khối thẻ mở rộng trực tiếp (Inline Card) */
   @media (max-width: 768px) {
       .topo-hover-container {
           grid-template-columns: 1fr;
           gap: 10px;
       }
       .topo-tooltip-box {
           position: static;
           visibility: visible;
           opacity: 1;
           transform: none;
           width: 100%;
           box-sizing: border-box;
           margin-top: 8px;
           pointer-events: auto;
       }
   }
   ```

---

## 🔲 12. Thiết Kế Menu Chuẩn Khung 4 Cạnh & Chữ Tương Phản Cao (4-Sided Perimeter Boxed Menu)

1. **Bo màu toàn bộ 4 cạnh (Perimeter Border)**:
   - Tránh dùng viền 1 cạnh bất đối xứng (`border-left`) gây cảm giác lệch mép.
   - Luôn sử dụng viền 4 cạnh hoàn chỉnh: `border: 1.5px solid <Theme Color>; border-radius: 10px;`.
2. **Màu nền phân định sâu & Hiệu ứng Gradient khi chọn**:
   - Từng ô menu có màu nền tối sâu thẳm theo sắc tố riêng (`#0B192C`, `#08211B`, `#241A06`, v.v.).
   - Khi chọn (`:has(input:checked)`), chuyển sang dải màu Gradient phát sáng: `linear-gradient(135deg, rgba(accent_rgb, 0.35) 0%, #bg_dark 100%)`.
3. **Độ tương phản chữ tuyệt đối**:
   - Chữ tiêu đề: `color: #FFFFFF !important; font-weight: 700 / 800; font-size: 13px;`
   - Đổ bóng chữ: `text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);` đảm bảo chữ luôn nổi bật và không bao giờ bị chìm/trộn lẫn vào bất kỳ màu nền nào.
4. **Căn đều chiều ngang 100% (Equal Width Rule)**:
   - Thiết lập `width: 100% !important; box-sizing: border-box !important;` cho toàn bộ các ô radio/menu để các khối chữ nhật luôn có bề ngang bằng nhau tuyệt đối.

---

## 📦 13. Hộp Gom Tải Hàng Loạt & Nén ZIP Tức Thời (Batch Asset Aggregator & Instant ZIP Downloader)

Trong các màn hình quản lý tài liệu, soạn thảo hay trích dẫn:
1. Luôn cung cấp một **Hộp gom nhanh tài liệu có bản toàn văn (Open Access / PDF)** ngay đầu danh mục.
2. Tích hợp nút kiểm nhanh **"✓ Chọn tất cả"** kết hợp với danh sách lọc đa mục (`st.multiselect`).
3. Cung cấp nút hành động 1-click **`📦 NÉN & TẢI XUỐNG TẤT CẢ TÀI LIỆU ĐÃ CHỌN (.ZIP)`** thực hiện tải ngầm và đóng gói tệp nén ZIP trong bộ nhớ, cho phép người dùng tải về máy toàn bộ tài liệu nghiên cứu trong một lần bấm duy nhất.
