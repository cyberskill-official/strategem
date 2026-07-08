# Tam Thuc Strategem

**Phiên bản:** 1.0 (MVP Development Ready)  
**Ngày:** 2026-07-08

---

## 1. Giới thiệu

**Tam Thuc Strategem** là nền tảng hỗ trợ tư vấn chiến lược dựa trên di sản Tam Thức (Kỳ Môn Độn Giáp, Lục Nhâm, Thái Ất Thần Số), kết hợp tính toán chính xác theo cổ pháp với AI diễn giải hiện đại.

Mục tiêu là giúp cá nhân và doanh nghiệp ra quyết định tốt hơn về **thời điểm (timing)**, **phương hướng**, và **đánh giá cục diện**.

---

## 2. Tình trạng hiện tại

- **Tài liệu:** Đã hoàn thiện **51 PDFs** chi tiết kỹ thuật + implementation guide + 13 hình ảnh mockup/wireframe.
- **Backlog:** Đã có `BACKLOG.md` với các task được phân loại rõ ràng (P0/P1/P2).
- **Hướng dẫn cho Agent:** Đã có `AGENTS.md` để AI coding agent có thể tự hoạt động.
- **Trạng thái code:** Chưa bắt đầu implement (sẵn sàng cho giai đoạn phát triển).

---

## 3. Cấu trúc tài liệu

Tất cả tài liệu chi tiết nằm trong thư mục `docs/` (hoặc root artifacts).

**Các file quan trọng cần đọc:**

| File | Mục đích |
|------|----------|
| `00_Master_Index_and_Completion_Checklist.pdf` | Index tổng hợp toàn bộ tài liệu |
| `BACKLOG.md` | Danh sách task chi tiết để phát triển |
| `AGENTS.md` | Hướng dẫn cho AI Agent tự động phát triển |
| `45_Overall_Technical_Architecture_and_Data_Flow.pdf` | Kiến trúc tổng quan |
| `28_QiMen_Engine_Full_Implementation_Detail.pdf` | Chi tiết implement Kỳ Môn (ưu tiên cao nhất) |
| `51_Detailed_Wireframes_for_All_Major_Screens.pdf` | Wireframe chi tiết các màn hình |
| Các file mockup hình ảnh | Visual reference cho UI |

---

## 4. Cách làm việc với Agent

1. Agent sẽ đọc `AGENTS.md` trước tiên.
2. Agent sẽ tuân thủ quy trình trong `BACKLOG.md`.
3. Mọi implementation phải tuân thủ các file PDF tương ứng.
4. Human có thể review output của Agent qua pull request hoặc demo.

---

## 5. Công nghệ đề xuất (MVP)

- **Backend:** Python + FastAPI
- **Frontend:** Next.js 14+ + Tailwind + shadcn/ui
- **Database:** PostgreSQL + Vector DB (Chroma/Pinecone)
- **Cache:** Redis
- **LLM:** OpenAI / Claude / Local model
- **Deployment:** Docker + Kubernetes (hoặc Platform as a Service cho MVP)

---

## 6. Hướng phát triển tiếp theo (ưu tiên)

1. **Setup Project & Database** (1-2 tuần)
2. **Implement Qi Men Engine** (ưu tiên cao nhất, 3-5 tuần)
3. **Xây dựng Rule Engine + RAG**
4. **Interactive Chart Component**
5. **End-to-end MVP flow** (Timing Optimizer)
6. **Beta Launch + Expert Review**

---

## 7. Lưu ý quan trọng

- **Chất lượng cổ pháp là cốt lõi.** Không được hy sinh độ chính xác của calculation engines.
- **Luôn có disclaimer** trong mọi output liên quan đến interpretation.
- **Hợp tác với Master/Practitioner** là cần thiết để đảm bảo chất lượng và tính chính thống.

---

**Chúc bạn và Agent phát triển thành công!**

Nếu cần hỗ trợ thêm, hãy quay lại và cung cấp context cụ thể.