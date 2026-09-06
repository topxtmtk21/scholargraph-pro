# 🔬 HỆ THỐNG ĐỘI NGŨ TRỢ LÝ NGHIÊN CỨU AI (1 DOI → 11 PHÚT 03 GIÂY)

Hệ thống Pipeline Nghiên cứu Học thuật Tự động hóa Toàn diện dựa trên Kiến trúc Đa Tác tử (Multi-Agent Architecture) theo mô hình **Zero-Hallucination**, **Human-in-the-Loop**, và **Structured Workflow**.

---

## 🌟 Tổng quan Kiến trúc & Luồng Xử lý

Hệ thống biến **1 mã DOI duy nhất** thành trọn bộ **8 sản phẩm nghiên cứu chuẩn mực** chỉ trong một quy trình thống nhất:

```
[Input: 1 Seed DOI]
       │
       ▼
┌──────────────┐ ──► Artifacts: network.html, refs.csv, refs.bib, refs.ris
│   CiteNet    │     (Truy vấn OpenAlex Graph API, mở rộng 2 thế hệ trích dẫn)
└──────────────┘
       │  [Bàn giao: Top 25 bài nòng cốt]
       ▼
┌──────────────┐ ──► Artifacts: evidence_table.csv, evidence_brief.md
│  SynthDesk   │     (Bóc tách cấu trúc 4 trường, kiểm tra Grounding Coverage ≥96%)
└──────────────┘
       │  [Bàn giao: Evidence Pool + Grounded Claims]
       ▼
┌──────────────┐ ──► Artifacts: introduction_draft.md, audit_report.json
│   IntroWri   │     (Chắp bút Introduction chuẩn Swales CARS & Automated Audit Engine)
└──────────────┘
       │
       ▼
[Trung tâm Xuất Dữ liệu: research_bundle.zip (Đóng gói trực tiếp trong RAM)]
```

---

## 👥 Đặc tả 3 Trợ lý Nghiên cứu AI

### 1. 🌐 CiteNet (Graph Expansion & Network Builder)
- **Nhiệm vụ**: Nhận 1 seed DOI, dò tìm và mở rộng mạng lưới trích dẫn 2 thế hệ qua **OpenAlex API** (Polite Pool).
- **Phân loại**: Tự động dán nhãn *Primary Study* (thực nghiệm) vs. *Secondary Evidence* (review/meta-analysis).
- **Sản phẩm**:
  - `network.html`: Đồ thị tương tác vật lý (PyVis), phân màu theo thế hệ (Hạt giống: Đỏ, Gen-1: Xanh lá, Gen-2: Xanh dương), kích thước nút theo citation count.
  - `refs.csv`: Bảng dữ liệu toàn bộ tài liệu thu thập.
  - `refs.bib` & `refs.ris`: Thư viện trích dẫn chuẩn hóa sẵn sàng nhập vào Zotero / Mendeley / EndNote.

### 2. 📊 SynthDesk (Evidence Extraction & Synthesis)
- **Nhiệm vụ**: Lọc 25 bài nòng cốt có DOI & Abstract, bóc tách cấu trúc 4 chiều học thuật:
  - *Research Problem* (Vấn đề / Mục tiêu nghiên cứu)
  - *Methodology* (Phương pháp / Thiết kế nghiên cứu)
  - *Key Finding* (Phát hiện định lượng / định tính chính)
  - *Limitation / Gap* (Giới hạn và khoảng trống học thuật)
- **Kiểm định neo ngữ cảnh (Grounding Verification)**: Đối soát chuỗi trực tiếp với câu văn trong abstract gốc, đảm bảo độ bao phủ ≥96%.
- **Sản phẩm**:
  - `evidence_table.csv`: Ma trận bằng chứng 25 bài × 4 trường dữ liệu.
  - `evidence_brief.md`: Văn bản tổng hợp luận chứng (~1.000 từ) gắn mã `[Author, Year | DOI]`.

### 3. ✍️ IntroWri (Grounded Manuscript Drafter)
- **Nhiệm vụ**: Chắp bút phần Đặt vấn đề (Introduction) theo mô hình kinh điển **John Swales CARS (Creating a Research Space)**:
  - *Move 1*: Establishing a territory (Bối cảnh và tầm quan trọng học thuật).
  - *Move 2*: Establishing a niche (Khoảng trống / mâu thuẫn trong y văn).
  - *Move 3*: Occupying the niche (Mục tiêu và đóng góp mới của nghiên cứu).
- **Bộ máy kiểm toán tự động (Automated Audit Engine)**:
  - Phân tích cú pháp regex kiểm toán trích dẫn.
  - Ràng buộc khép kín: Chỉ dùng tài liệu trong evidence pool, bắt buộc ≥8 grounded claims và ≥6 tài liệu tham chiếu.
- **Sản phẩm**:
  - `introduction_draft.md`: Bản thảo Introduction mạch lạc, học thuật.
  - `audit_report.json`: Báo cáo chỉ số kiểm toán định lượng.

---

## ⏱️ Bảng Phân bổ Thời gian (Benchmark 11 phút 03 giây)

| Giai đoạn | Trợ lý | Tác vụ trọng tâm | Thời gian | Đầu ra sinh ra |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | **CiteNet** | Gọi API OpenAlex, duyệt 2 thế hệ trích dẫn, tính toán đồ thị PyVis | 01m 15s | `network.html`, `refs.csv`, `refs.bib`, `refs.ris` |
| **P2** | **SynthDesk** | Xếp hạng 25 bài, trích xuất cấu trúc 4 trường học thuật | 05m 30s | 50-100 evidence cells, Grounding Coverage ≥96% |
| **P3** | **SynthDesk** | Biên soạn và neo trích dẫn cho bản tóm lược Evidence Brief | 01m 45s | `evidence_brief.md` (~1.026 từ) |
| **P4** | **IntroWri** | Chắp bút Introduction theo CARS Model trên cơ sở evidence pool | 01m 45s | `introduction_draft.md` |
| **P5** | **IntroWri** | Chạy bộ máy regex audit, kiểm toán claims và đóng gói ZIP | 00m 48s | `audit_report.json`, `research_bundle.zip` |
| **TỔNG** | **Hệ thống** | **Toàn bộ pipeline từ 1 DOI → 8 Sản phẩm nghiên cứu** | **11m 03s** | **8 artifacts nghiên cứu** |

---

## 🚀 Hướng dẫn Cài đặt & Vận hành

### 1. Vận hành Cục bộ (Local Environment)

```bash
# 1. Di chuyển vào thư mục dự án
cd "d:/AUTO WORK/11_So do tri thuc hoc thuat"

# 2. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 3. Chạy ứng dụng Streamlit
streamlit run app.py
```

Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ: `http://localhost:8501`.

### 2. Cấu hình API Key (Tùy chọn)

Hệ thống tích hợp sẵn **Local Deterministic Academic Engine** cho phép chạy thử nghiệm ngay lập tức không cần API key. Nếu muốn sử dụng các mô hình LLM đám mây:

1. Sao chép file mẫu:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Điền khóa `GEMINI_API_KEY` (lấy tại Google AI Studio) hoặc `OPENAI_API_KEY` trong `.streamlit/secrets.toml`.

### 3. Vận hành trên Streamlit Cloud

1. Đẩy mã nguồn lên kho lưu trữ GitHub.
2. Đăng nhập [Streamlit Community Cloud](https://share.streamlit.io).
3. Chọn repo và chỉ định Main file path là `app.py`.
4. Trong mục **App Settings -> Secrets**, điền các khóa API tương ứng.

---

## 📖 Cẩm nang Hướng dẫn Chi tiết Toàn diện
Xem hướng dẫn chi tiết từng bước, cấu hình phần cứng, cài đặt môi trường và đánh giá khả năng triển khai công khai tại:
👉 **[HUONG_DAN_CAI_DAT_VA_SU_DUNG.md](file:///d:/AUTO%20WORK/11_So%20do%20tri%20thuc%20hoc%20thuat/HUONG_DAN_CAI_DAT_VA_SU_DUNG.md)**

---
*Tác giả & Kiến trúc sư hệ thống: **TRẦN DUY (Lead AI Research Engineer)***
