# AGENTS.md - Hướng dẫn cho AI Coding Agent

**Phiên bản:** 1.0  
**Mục tiêu:** Cho phép AI Agent tự động đọc hiểu toàn bộ tài liệu, sau đó phát triển, kiểm thử và hoàn thiện sản phẩm **Tam Thuc Strategem** một cách có hệ thống và chính xác.

---

## 1. Nguyên tắc làm việc (BẮT BUỘC TUÂN THỦ)

1. **Đọc trước khi code**: Trước khi thực hiện bất kỳ task nào, Agent **phải** đọc kỹ các file PDF liên quan trong thư mục `docs/`.
2. **Tuân thủ cổ pháp**: Tính chính xác của Calculation Engines (đặc biệt Kỳ Môn) là ưu tiên số 1. Không được hy sinh độ chính xác để đổi lấy tốc độ.
3. **Test-driven cho Engines**: Mọi logic tính toán phải được test với các ví dụ cổ điển đã biết trước khi mở rộng.
4. **Pattern-as-Data**: Tất cả patterns nên được quản lý qua JSON trong database thay vì hardcode.
5. **Minh bạch & Đạo đức**: Luôn có disclaimer rõ ràng trong mọi output. Không hứa hẹn tuyệt đối.

---

## 2. Quy trình làm việc khuyến nghị

### Giai đoạn 1: Hiểu & Thiết lập (Week 1)

1. Đọc toàn bộ file `00_Master_Index_and_Completion_Checklist.pdf` để có cái nhìn tổng quan.
2. Đọc `04_Ke_hoach_Trien_khai_Toan_dien.pdf` (Implementation Plan) và `05_PRD_Product_Requirements_Document.pdf`.
3. Đọc `45_Overall_Technical_Architecture_and_Data_Flow.pdf` + `46_Detailed_Data_Models_and_Database_Schema.pdf`.
4. Setup project theo `BACKLOG.md` (Epic 1).

### Giai đoạn 2: Core Engines (Week 2-4) - Ưu tiên cao nhất

**Thứ tự khuyến nghị:**

1. **Qi Men Dun Jia Engine** (file `28_QiMen_Engine_Full_Implementation_Detail.pdf`)
   - Bắt đầu với Ju calculation + Plate construction.
   - Test với ít nhất 30-50 ví dụ cổ điển.
   - Sau đó mới implement pattern detection.

2. **Rule Engine chung** (file `31_Rule_Engine_and_Pattern_Matching_Full_Detail.pdf`)
   - Xây dựng engine đọc patterns từ JSON.

3. **Liu Ren Engine** (file `29_LiuRen_Engine_Full_Implementation_Detail.pdf`) — P1

4. **Tai Yi Engine** (file `30_TaiYi_Engine_Full_Implementation_Detail.pdf`) — P2

### Giai đoạn 3: AI Layer & RAG (Song song với Engine)

- Đọc `32_RAG_Service_Full_Implementation_Detail.pdf`
- Thiết lập Vector DB + Embedding
- Xây dựng prompt templates và LLM integration

### Giai đoạn 4: Frontend & Interactive Experience

- Đọc `34_Interactive_Chart_Component_Full_Detail.pdf` + Wireframes + Mockups
- Ưu tiên xây dựng **Interactive 9-cung Chart** trước
- Sau đó mới build các trang khác theo `35_Frontend_Pages_Implementation_Guide.pdf`

### Giai đoạn 5: Testing, Polish & Launch

- Đọc `38_Testing_and_Validation_Detailed_Strategy.pdf`
- Implement comprehensive testing (đặc biệt validation với classical examples)
- Setup CI/CD theo `39_Deployment_CI_CD_and_Infrastructure_Detailed.pdf`
- Beta launch + Expert review loop

---

## 3. Cấu trúc tài liệu & Cách đọc

Agent nên ưu tiên đọc theo thứ tự sau khi cần:

**Core Technical (Bắt buộc đọc trước khi code):**
- `28_QiMen_Engine_Full_Implementation_Detail.pdf`
- `31_Rule_Engine_and_Pattern_Matching_Full_Detail.pdf`
- `32_RAG_Service_Full_Implementation_Detail.pdf`
- `34_Interactive_Chart_Component_Full_Detail.pdf`
- `45_Overall_Technical_Architecture_and_Data_Flow.pdf`
- `46_Detailed_Data_Models_and_Database_Schema.pdf`

**Supporting:**
- `35_Frontend_Pages_Implementation_Guide.pdf`
- `38_Testing_and_Validation_Detailed_Strategy.pdf`
- `51_Detailed_Wireframes_for_All_Major_Screens.pdf`
- Tất cả các file mockup hình ảnh

**Business & Product Context:**
- `02_Trong_tam_ung_dung_Tu_van_Chien_luoc.pdf`
- `05_PRD_Product_Requirements_Document.pdf`
- `BACKLOG.md`

---

## 4. Tiêu chí hoàn thành một Task

Mỗi task chỉ được coi là hoàn thành khi:

- Code chạy được và pass tests.
- Có documentation/update tương ứng (nếu cần).
- Đã được test với dữ liệu thực tế hoặc classical examples (đối với Engines).
- Có review từ Expert (nếu là patterns hoặc interpretation).

---

## 5. Lưu ý quan trọng

- **Không được hardcode patterns** vào code. Phải dùng JSON + Database.
- **Luôn có disclaimer** trong mọi output liên quan đến interpretation.
- **Ưu tiên chất lượng calculation** hơn là giao diện đẹp ở giai đoạn đầu.
- Khi có conflict giữa các file PDF, ưu tiên file có version cao hơn hoặc file implementation detail.

---

**Agent hãy bắt đầu bằng việc đọc file `BACKLOG.md` và xác nhận đã hiểu toàn bộ yêu cầu trước khi viết code đầu tiên.**