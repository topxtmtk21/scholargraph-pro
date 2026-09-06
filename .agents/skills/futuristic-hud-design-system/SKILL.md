---
name: futuristic-hud-design-system
description: Quy chuẩn và cẩm nang toàn diện để thiết kế giao diện Futuristic Sci-Fi Glassmorphism HUD Dashboard (Synapse Academic / Quantum Deck) đạt chuẩn quốc tế, tương phản WCAG AAA/AA, chống lỗi Streamlit Markdown, hỗ trợ đa màn hình Blob URL và tối ưu hóa 100% cho Online & Mobile.
---

# 🌌 Futuristic Sci-Fi Glassmorphism HUD UI/UX Design Skill

Cẩm nang đúc kết các nguyên tắc thiết kế, quy chuẩn CSS Tokens, kiến trúc giao diện tương lai (**Futuristic Sci-Fi Glassmorphism HUD Dashboard**) và các bài học kỹ thuật thực chiến giải quyết triệt để lỗi hiển thị trong các dự án phức tạp.

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
- Các nút biểu tượng tròn/vuông bo góc ($10\text{px}$), kính mờ, có tooltip khi rê chuột.
- Chuyển layout nhanh, bật/tắt hiệu ứng truy vết, căn giữa toàn cảnh.

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

## 📱 5. Quy Chuẩn Tối Ưu Hóa Online Mobile & Responsive

1. **Media Query Ngưỡng $900\text{px}$**:
   - Khi độ rộng màn hình $< 900\text{px}$: Tự động chuyển các grid đa cột thành 1 cột (`grid-template-columns: 1fr;`).
   - Ẩn bớt các chip meta rườm rà trên Header (`.header-meta-cluster { display: none; }`).
   - Chuyển Vertical Dock sang dạng trượt ngang hoặc ẩn vào menu rút gọn.
2. **Kích thước vùng chạm (Touch Target)**:
   - Mọi nút bấm trên di động phải có kích thước tối thiểu $40\text{px} \times 40\text{px}$ để chạm ngón tay không bị trượt.
3. **Thanh Điều Hướng Nhanh (Mobile Quick Navigation Ribbon)**:
   - Bố trí dải nút chuyển nhanh phân hệ dạng Ribbon cảm ứng cố định ở trên đầu để người dùng điện thoại không phải mở sidebar liên tục.
