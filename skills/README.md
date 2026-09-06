# 📚 Tủ Sách Kỹ Năng Kỹ Thuật Công Nghệ Phần Mềm & Thiết Kế UI/UX
### Enterprise Resilient Software Architecture & Modern HUD Design System

Thư mục này chứa bộ cẩm nang kỹ thuật thực chiến (**Engineering & Design Skills**) được đúc kết từ quá trình nghiên cứu, thiết kế và phát triển các hệ thống phần mềm phức tạp. Bộ nguyên tắc này mang tính khái quát cao, được chuẩn hóa để có thể áp dụng cho **bất kỳ dự án phần mềm nào** (Web App, Mobile App, Desktop App, Data Dashboard, SaaS Platform, AI Copilot).

---

## 📂 Danh Mục Các Cẩm Nang Kỹ Thuật Chuẩn Hóa

### 1. 🛡️ [Zero-Regression Software Engineering & Resilient Architecture](file:///.agents/skills/zero-regression-engineering/SKILL.md)
- **Mục tiêu**: Đảm bảo quá trình nâng cấp, tối ưu hóa và mở rộng hệ thống **không bao giờ làm hỏng, cắt xén hay suy giảm các tính năng đã hoạt động ổn định trước đó**.
- **Các nguyên tắc cốt lõi**:
  - **Quy tắc Bổ sung không xâm lấn (Additive-Only Changes)**: Sử dụng tham số tùy chọn với giá trị mặc định, bảo toàn 100% chữ ký hàm cũ và trường dữ liệu cũ.
  - **Chiến lược Khóa phiên bản phòng thủ (Version Shielding)**: Branching, Tagging, và lập Release Notes snapshot trước mỗi giai đoạn nâng cấp lớn.
  - **Kiến trúc Đa tầng dự phòng 3 lớp (Multi-Tier Fallback)**: Live API $\to$ Local Smart Cache $\to$ Heuristic Static Parsing.
  - **An toàn chuỗi nội suy đa ngôn ngữ (Cross-Language Escaping)**: Kỹ thuật xử lý thoát ký `{`, `}` trong Python f-string, chống bẫy Streamlit Markdown Indented Code Block, và chuẩn W3C Blob URL khi mở cửa sổ mới.
  - **Ma trận Phân quyền đa tầng chi tiết (Granular RBAC Matrix)**: Phân định 4 cấp vai trò (`super_admin`, `admin`, `researcher`, `viewer`) và phân quyền chi tiết đến từng tính năng con của hệ thống (đặc biệt là phân hệ Mạng lưới trích dẫn khoa học).
  - **Cô lập Môi trường kép (Cloud vs Local Dual-Mode Isolation)**: Bản Cloud bảo mật tối cao (loại bỏ nút bypass/1-click, triệt tiêu lộ email nhà phát triển, generic error handling); Bản Local duy trì 100% độ mượt mà, tự động Super Admin, không cản trở.
  - **Hệ thống Kiểm thử tự động 5 trụ cột (5-Pillar Test Suite)**: Unit/Syntax $\to$ Core Business $\to$ UI/Contrast (WCAG AAA/AA) $\to$ E2E Integration $\to$ Multi-Device Viewport.
  - **Checklist vàng trước khi Commit**: Rà soát 7 bước nghiêm ngặt.

### 2. 🌌 [Modern Futuristic UI/UX & Glassmorphism HUD Design System](file:///.agents/skills/futuristic-hud-design-system/SKILL.md)
- **Mục tiêu**: Xây dựng trải nghiệm giao diện người dùng đỉnh cao, hiện đại (Futuristic HUD / Aero Glassmorphism) đạt chuẩn công thái học và tương thích $100\%$ mọi màn hình.
- **Các nguyên tắc cốt lõi**:
  - **Triết lý Quantum HUD & Aero Glassmorphism**: Nền không gian sâu kết hợp kính mờ phản quang và luồng hạt năng lượng $60\text{ FPS}$.
  - **Độ tương phản quốc tế WCAG AAA/AA**: Kế thừa đồng bộ qua hệ biến CSS Tokens, chống chìm màu trên nền tối.
  - **Nguyên tắc Không che khuất vùng quan sát (Zero-Occlusion Layout)**: Định vị Smart Inspector tại góc an toàn (Safe Anchors), khay chú thích dạng Slide-Out Drawer.
  - **Quy luật Tỷ lệ trực quan (Data-Driven Visual Scale)**: Tính toán kích thước đối tượng theo hàm Logarit số liệu thực tế (Price's Law).
  - **Ma trận Đa màn hình (Mobile, Tablet, Desktop, Ultra-Wide 4K)**: Bố cục thích ứng tự nhiên, tự động căn khớp khung nhìn khi xoay ngang/dọc thiết bị.
  - **Giao thức Chuyển hóa cảm ứng (Touch-First & Single-Tap Protocol)**: Chuyển toàn bộ tương tác Hover thành Single-Tap, đảm bảo kích thước chạm tối thiểu $\ge 44\text{px}$ (Fitts's Law).
  - **Chống tràn trang ngang & Cuộn quán tính mượt mà**: Chặn tràn viewport, kích hoạt momentum touch scrolling và bảo vệ Safe Area Insets.
  - **Bộ tìm kiếm đa tiêu chí thời gian thực (Real-Time Multi-Facet Search)**: Tìm kiếm linh hoạt theo ID, tác giả, năm, từ khóa, tạp chí kèm hiệu ứng làm mờ và focus mượt mà.

---

## 🚀 Cách Áp Dụng Cho Dự Án Mới
1. **Sao chép thư mục `.agents/skills/`** vào thư mục gốc của dự án mới.
2. **Thiết lập bộ Test Suites tương ứng** (`test_system_core.py`, `test_ui_contrast.py`, `test_viewport.py`).
3. **Áp dụng Bộ Checklist Vàng** trước mỗi lần phát hành mã nguồn.
