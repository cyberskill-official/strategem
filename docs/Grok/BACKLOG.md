# Tam Thuc Strategem - Development Backlog

**Phiên bản:** 1.0  
**Ngày cập nhật:** 2026-07-08  
**Mục tiêu:** Xây dựng MVP của nền tảng Tam Thuc Strategem hỗ trợ tư vấn chiến lược dựa trên Tam Thức (Kỳ Môn, Lục Nhâm, Thái Ất).

---

## Epic 1: Nền tảng & Hạ tầng (Foundation)

### Epic 1.1: Project Setup & Infrastructure

**Task 1.1.1: Khởi tạo Monorepo**
- **Mô tả:** Thiết lập cấu trúc monorepo cho backend (Python/FastAPI) và frontend (Next.js/React).
- **Acceptance Criteria:**
- Sử dụng Turborepo hoặc Nx.
- Có folder `backend/`, `frontend/`, `shared/`, `docs/`.
- Có file `package.json` root và scripts chung.
- CI/CD cơ bản (GitHub Actions) đã setup.
- **Ưu tiên:** P0
- **Dependencies:** None

**Task 1.1.2: Thiết lập Database & Migrations**
- **Mô tả:** Thiết lập PostgreSQL + Alembic migrations cho các bảng chính.
- **Acceptance Criteria:**
- Bảng `users`, `queries`, `charts`, `knowledge_patterns`, `reports` đã được migrate.
- Có seed script cơ bản.
- Connection pooling và environment variables đã config.
- **Ưu tiên:** P0

**Task 1.1.3: Thiết lập Authentication**
- **Mô tả:** Implement JWT + Refresh Token + Social Login (Google/Apple).
- **Acceptance Criteria:**
- Đăng ký, đăng nhập, refresh token hoạt động.
- Birth data được encrypt khi lưu.
- Role-based access (Free/Premium/Enterprise) hoạt động.
- **Ưu tiên:** P0

---

## Epic 2: Calculation Engines (Cốt lõi)

### Epic 2.1: Qi Men Dun Jia Engine

**Task 2.1.1: Implement Ju Calculation & Plate Construction**
- **Mô tả:** Xây dựng logic tính Ju và xây dựng Thiên bàn / Địa bàn theo cổ pháp.
- **Acceptance Criteria:**
- Hàm `calculate_ju()` và `build_plates()` hoạt động chính xác.
- Test pass với ít nhất 30 ví dụ cổ điển.
- **Ưu tiên:** P0
- **Reference:** File `28_QiMen_Engine_Full_Implementation_Detail.pdf`

**Task 2.1.2: Bố trí Tam Kỳ, Lục Nghi, Bát Môn, Cửu Tinh, Bát Thần**
- **Mô tả:** Implement logic đặt các yếu tố chính trong chart.
- **Acceptance Criteria:**
- Chart data JSON đầy đủ và chính xác.
- Zhifu/Zhishi được xác định đúng.
- **Ưu tiên:** P0

**Task 2.1.3: Pattern Detection cho Kỳ Môn**
- **Mô tả:** Implement Rule Engine detect các patterns quan trọng của Kỳ Môn.
- **Acceptance Criteria:**
- Ít nhất 15-20 patterns quan trọng được detect đúng.
- Patterns được lưu dưới dạng JSON conditions.
- **Ưu tiên:** P0

### Epic 2.2: Liu Ren Engine

**Task 2.2.1 - 2.2.3:** Tương tự như Kỳ Môn, nhưng cho Lục Nhâm (Tứ khóa, Tam truyền, 12 Thiên tướng, patterns).
- **Ưu tiên:** P1
- **Reference:** File `29_LiuRen_Engine_Full_Implementation_Detail.pdf`

### Epic 2.3: Tai Yi Engine

**Task 2.3.1 - 2.3.3:** Tương tự, cho Thái Ất Thần Số.
- **Ưu tiên:** P2
- **Reference:** File `30_TaiYi_Engine_Full_Implementation_Detail.pdf`

---

## Epic 3: Rule Engine & Knowledge Base

**Task 3.1: Xây dựng Rule Engine chung**
- **Mô tả:** Xây dựng engine quét chart data và match patterns từ database.
- **Acceptance Criteria:**
- Hỗ trợ conditions phức tạp (AND/OR).
- Dễ thêm pattern mới qua JSON.
- **Ưu tiên:** P0
- **Reference:** File `31_Rule_Engine_and_Pattern_Matching_Full_Detail.pdf`

**Task 3.2: Seed Knowledge Base ban đầu**
- **Mô tả:** Seed 150-200 patterns quan trọng nhất cho 3 hệ thống.
- **Ưu tiên:** P0

---

## Epic 4: RAG Service & AI Interpretation

**Task 4.1: Thiết lập Vector Database & Embedding**
- **Mô tả:** Embed và lưu patterns + classical excerpts vào Vector DB.
- **Ưu tiên:** P0
- **Reference:** File `32_RAG_Service_Full_Implementation_Detail.pdf`

**Task 4.2: Xây dựng Prompt Engineering & LLM Integration**
- **Mô tả:** Xây dựng prompt template và gọi LLM để tạo interpretation.
- **Acceptance Criteria:**
- Output có cấu trúc JSON rõ ràng (Beginner/Expert/Recommendations).
- Có citation và disclaimer.
- **Ưu tiên:** P0

---

## Epic 5: Frontend & Interactive Experience

**Task 5.1: Interactive 9-cung Chart Component**
- **Mô tả:** Xây dựng component SVG/Canvas cho chart Kỳ Môn tương tác.
- **Acceptance Criteria:**
- Hover/Click vào cung hiển thị chi tiết.
- Color coding cát/hung rõ ràng.
- Responsive và export được.
- **Ưu tiên:** P0
- **Reference:** File `34_Interactive_Chart_Component_Full_Detail.pdf` + Mockups

**Task 5.2 - 5.7:** Xây dựng các trang: Dashboard, Query Input, Results, Timing Optimizer, Report View, Learning Hub.
- **Ưu tiên:** P0 - P1
- **Reference:** File `35_Frontend_Pages_Implementation_Guide.pdf` + Wireframes + Mockups

---

## Epic 6: Report, Testing, DevOps & Launch

**Task 6.1: Report Generation Service**
- **Ưu tiên:** P1
- **Reference:** File `33_Report_Generation_Service_Full_Detail.pdf`

**Task 6.2: Comprehensive Testing Suite**
- **Mô tả:** Unit test, Integration test, Validation test với classical examples, Expert review process.
- **Ưu tiên:** P0
- **Reference:** File `38_Testing_and_Validation_Detailed_Strategy.pdf`

**Task 6.3: CI/CD & Deployment**
- **Ưu tiên:** P1
- **Reference:** File `39_Deployment_CI_CD_and_Infrastructure_Detailed.pdf`

**Task 6.4: MVP Beta Launch**
- **Mô tả:** Deploy staging, mời beta users (practitioner + early users), thu thập feedback.

---

## Ghi chú chung

- **P0** = Must have cho MVP
- **P1** = Should have
- **P2** = Nice to have

Tất cả task nên tuân thủ nghiêm ngặt các file PDF tương ứng trong thư mục `docs/`.