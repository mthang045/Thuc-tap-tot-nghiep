# Phan Cong Do An - Legal AI Contract Reviewer

## 1. TOM TAT DU AN

**Ten du an:** Legal AI Contract Reviewer
**Cong nghe:** Python (FastAPI) + React (Vite) + MongoDB
**Mo ta:** He thong phan tich hop dong phap luat Viet Nam, su dung AI de phan loai, danh gia rui ro, tra cuu phap luat tu dong, va tra loi phap ly qua chatbot.

---

## 2. MO HINH HE THONG

```
                    +-----------------+
                    |   Nguoi dung     |
                    |  (Frontend)      |
                    +--------+---------+
                             | HTTP/WebSocket
                    +--------v---------+
                    |  Backend API     |
                    |  FastAPI/Python  |
                    +--------+---------+
                             |
          +------------------+------------------+
          |                  |                  |
  +-------v------+  +--------v------+  +-------v------+
  |  MongoDB     |  |  AI Models   |  |  VNPay API   |
  |  (Database)  |  |  (OpenAI)    |  |  (Thanh toan)|
  +-------------+  +--------------+  +--------------+
```

---

## 3. PHAN CONG CONG VIEC CHO 3 THANH VIEN

### THÀNH VIÊN 1: Backend - AI / Machine Learning

**Trach nhiem:** Xây dựng và huấn luyện các mô hình AI phân loại và tìm kiếm pháp luật.

#### 3.1.1. Mô hình phân loại loại hợp đồng (Contract Classification)
- **File:** `train_fast.py`, `train_models.py`
- **Mo ta:** Huấn luyện mô hình phân loại văn bản thành 13 loại hợp đồng
- **Models:** SVM, Logistic Regression
- **Features:**
  - Tiền xử lý văn bản tiếng Việt (stopwords, tokenization)
  - TF-IDF vectorization
  - Training data: ~600+ mẫu hợp đồng tiếng Việt
- **Output:** 13 nhãn: hợp đồng lao động, mua bán, thuê nhà, ủy quyền, nghỉ phép, quy chế nội bộ, thỏa thuận NDA, quyết định bổ nhiệm, giấy ủy quyền, hợp đồng cung cấp dịch vụ, vay tiền, hợp đồng giao khoán, biên bản họp

#### 3.1.2. Mô hình đánh giá mức độ rủi ro (Risk Assessment)
- **File:** `train_fast.py`
- **Mo ta:** Phân loại mức độ rủi ro thành: thấp (low), trung bình (medium), cao (high)
- **Accuracy:** ~85%+
- **Feature importance:** Từ khóa pháp lý, điều khoản vi phạm, điều khoản bất lợi

#### 3.1.3. Mô hình phát hiện vi phạm pháp luật (Violation Detection)
- **File:** `train_fast.py`
- **Mo ta:** Nhận diện các điều khoản vi phạm pháp luật trong hợp đồng
- **Features:** Clause extraction, legal term matching

#### 3.1.4. RAG - Retrieval Augmented Generation (Tra cuu phap luat)
- **File:** `bm25_search.py`, `bm25_search_v2.py`, `build_rag_index.py`, `pageindex_rag.py`
- **Mo ta:** Tìm kiếm đoạn văn bản pháp luật liên quan đến câu hỏi
- **Ky thuat:**
  - BM25 (Okapi BM25) cho keyword search
  - Sentence embeddings (sentence-transformers) cho semantic search
  - MongoDB vector search (ANN index)
  - Hybrid search (BM25 + vector)
- **Database:** 24 văn bản pháp luật Việt Nam (Bộ Luật Lao Động, Bộ Luật Dân Sự, Luật Thương Mại, ...)
- **Collection:** `law_chunks` (đã chunk theo điều luật)

#### 3.1.5. AI Agent cho Chatbot
- **File:** `backend/src/agents/`, `backend/src/workflow/`
- **Mo ta:** Agent AI trả lời câu hỏi pháp lý dựa trên RAG
- **Features:**
  - Multi-turn conversation (LangGraph checkpointer)
  - Tool-calling: tra cứu pháp luật, phân tích hợp đồng
  - Memory: lưu lịch sử hội thoại (company_memory)
  - Streaming response

#### 3.1.6. Sinh du lieu huấn luyện (Training Data Generation)
- **File:** `generate_training_data.py`, `convert_formats.py`
- **Mo ta:** Chuyển đổi và sinh dữ liệu huấn luyện cho nhiều định dạng:
  - Multi-task learning format
  - Classification format
  - Risk assessment format
  - Violation detection format
  - LLM fine-tuning format (OpenAI)

#### 3.1.7. PDF OCR (Nhận diện van ban)
- **File:** `ocr_pdfs.py`
- **Mo ta:** Trích xuất văn bản từ file PDF scan bằng OCR (pytesseract)

---

### THANH VIEN 2: Backend - API / Database / Payment

**Trach nhiem:** Xây dựng API, quản lý cơ sở dữ liệu, và tích hợp thanh toán.

#### 3.2.1. Backend API chính
- **File:** `simple_api.py` (~1500+ lines)
- **Mo ta:** REST API chính của ứng dụng
- **Framework:** FastAPI
- **Các endpoint chinh:**
  - `GET /api/legal-documents/` - Danh sach van ban phap luat
  - `GET /api/legal-documents/<id>` - Chi tiet van ban phap luat
  - `GET /api/legal-documents/search` - Tim kiem van ban
  - `GET /api/legal-documents/categories` - Thong ke theo danh muc
  - `/api/auth/*` - Auth (login, register, logout)
  - `/api/upload/*` - Upload tai lieu
  - `/api/analysis/*` - Phan tich hop dong
  - `/api/templates/*` - Quan ly mau van ban
  - `/api/chat/*` - Chatbot API
  - `/api/admin/*` - Quan ly he thong
  - `/api/payments/*` - Thanh toan VNPay

#### 3.2.2. API phan tich hop dong
- **File:** `simple_api.py` (phan phan tich)
- **Mo ta:**
  - Upload và phân tích hợp đồng
  - Trích xuất văn bản (OCR/file)
  - Phân loại loại hợp đồng
  - Đánh giá mức độ rủi ro
  - Phát hiện vi phạm pháp luật
  - Đề xuất điều khoản sửa đổi
  - Tham chiếu điều luật liên quan

#### 3.2.3. Quan ly CSDL MongoDB
- **File:** `src/db.py`, `src/ingest.py`, `src/resource_config.py`
- **Database:** MongoDB (legal_AI_db) - 12 collections
- **Collections chinh:**
  - `users` - Tai khoan nguoi dung (6 tai khoan)
  - `law_documents` - Van ban phap luat (24 tai lieu)
  - `law_chunks` - Cac chunk phap luat cho RAG
  - `analysis_history` - Lich su phan tich hop dong (31 ban ghi)
  - `chat_sessions` - Phien chat (4 phien)
  - `payments` - Giao dich thanh toan (10 giao dich)
  - `templates` - Mau van ban
  - `contracts` - Hop dong duoc quan ly
  - `documents` - Tai lieu upload
  - `audit_logs` - Nhat ky hanh dong
- **Indexes:** Da co index tren tat ca cac truong thuong dung (user_id, email, created_at, ...)
- **Cong cu:** MongoDB Compass, PyMongo

#### 3.2.4. Tich hop thanh toan VNPay
- **File:** `vnpay_utils.py`, `simple_api.py` (phan payment)
- **Mo ta:** Tich hop cong thanh toan VNPay
- **Luong:**
  1. User chon goi (Pro/Enterprise)
  2. Backend tao payment URL VNPay
  3. User thanh toan tren VNPay
  4. VNPay callback ve return_url
  5. Backend verify signature, cap nhat payment status
- **Plans:** Free, Pro (tháng/năm), Enterprise

#### 3.2.5. Quan ly mau van ban (Template Engine)
- **File:** `src/services/docx_service.py`, `pdf_generator.py`
- **Mo ta:**
  - Sinh hợp đồng từ template
  - Xuất DOCX/PDF từ nội dung phân tích
  - 13 loại template: hợp đồng lao động, thuê nhà, mua bán, ủy quyền, NDA, ...
  - Variable substitution: thay the placeholder trong template bang du lieu nguoi dung

#### 3.2.6. Import van ban phap luat
- **File:** `import_laws_to_mongodb.py`
- **Mo ta:** Import van ban phap luat tu file text vao MongoDB

#### 3.2.7. Quan ly nguoi dung & phan quyen
- **File:** `src/auth.py`, `create_users.py`
- **Mo ta:**
  - Register/Login (Werkzeug password hashing)
  - Session-based authentication
  - Role: admin / member
  - Subscription tiers: free / pro

---

### THANH VIEN 3: Frontend - React / UI/UX

**Trach nhiem:** Xây dựng giao diện người dùng và trải nghiệm người dùng.

#### 3.3.1. Cau truc du an Frontend
- **Framework:** React 19 + Vite
- **Styling:** Tailwind CSS + Radix UI components
- **Router:** React Router DOM v7
- **HTTP Client:** Axios (thong qua api.js service)
- **File chinh:** `frontend/src/App.jsx` (~400+ lines)

#### 3.3.2. Trang Upload & Phan tich hop dong
- **File:** `UploadSection.jsx`, `AnalysisResults.jsx`, `ResultPage.jsx`
- **Mo ta:**
  - Upload file PDF/DOCX (drag & drop + click)
  - Hiển thị tiến trình phân tích (progress bar)
  - Kết quả phân tích chi tiết:
    - Loại hợp đồng + độ chính xác
    - Điểm an toàn (0-100)
    - Mức độ rủi ro (thấp/trung bình/cao)
    - Số vi phạm phát hiện
    - Tham chiếu điều luật liên quan
    - Điều khoản đề xuất sửa đổi
  - So sánh 2 phiên bản hợp đồng (diff view)
  - Download báo cáo PDF

#### 3.3.3. Trang Chatbot
- **File:** `Chatbot.jsx`
- **Mo ta:**
  - Giao diện chat (UI tương tác)
  - Hỗ trợ 3 chế độ: Q&A, Review, Draft
  - Citation hiển thị nguồn pháp luật
  - Streaming response (real-time)
  - Lịch sử tin nhắn

#### 3.3.4. Quan ly mau van ban
- **File:** `frontend/src/components/TemplateList.jsx` ( neu co)
- **Mo ta:**
  - Danh sach template (13 loai)
  - Tao hop dong tu template (variable substitution)
  - Preview trực tiếp trên web

#### 3.3.5. Trang quan ly tai khoan
- **File:** `LoginForm.jsx`, `RegisterForm.jsx`, `AccountSettings.jsx`
- **Mo ta:**
  - Form đăng nhập / đăng ký
  - Quản lý profile (đổi mật khẩu, thông tin cá nhân)
  - Upload avatar

#### 3.3.6. Trang goi dich vu & thanh toan
- **File:** `PricingPlans.jsx`, `PaymentReturnPage.jsx`
- **Mo ta:**
  - Hien thi 3 goi: Free, Pro, Enterprise
  - Chọn chu kỳ thanh toán (tháng/năm)
  - Tích hợp thanh toán VNPay
  - Trang callback sau thanh toán (verify payment)
  - Hiển thị lịch sử giao dịch

#### 3.3.7. Trang Admin Dashboard
- **File:** `admin/AdminDashboard.jsx`, `admin/AdminOverview.jsx`, `admin/AnalyticsManagement.jsx`, `admin/SystemStats.jsx`, `admin/UserManagement.jsx`
- **Mo ta:**
  - Tong quan he thong (so nguoi dung, so phan tich, doanh thu)
  - Bieu do thong ke (Revenue, User Growth, Document Analysis)
  - Quan ly nguoi dung (CRUD)
  - Quan ly van ban phap luat
  - Audit logs

#### 3.3.8. Trang Lich su phan tich
- **File:** `AnalysisHistory.jsx`
- **Mo ta:**
  - Danh sach cac lan phan tich cua nguoi dung
  - Filter theo ngay, loai hop dong, muc do rui ro
  - Xem lai ket qua phan tich cu

#### 3.3.9. UI/UX components
- **File:** `frontend/src/components/ui/` (30+ components)
- **Library:** Radix UI (headless components)
- **Components:** Button, Dialog, Dropdown, Table, Tabs, Badge, Alert, Calendar, Chart, Avatar, ...

#### 3.3.10. Cac trang thong tin
- **File:** `AboutPage.jsx`, `PrivacyPolicyPage.jsx`, `TermsPage.jsx`
- **Mo ta:** Cac trang tinh (static pages)

---

## 4. LICH TRINH CONG VIEC

### GIAI DOAN 1: Database & Backend Core (Thu 2 - Thu 4)
- ThanVien2: Setup MongoDB, xay dung API co ban, auth, payment
- ThanVien1: Thiet ke AI models, bat dau train
- ThanVien3: Setup React, xay dung UI co ban

### GIAI DOAN 2: AI & Backend Logic (Thu 5 - Chu Nhat)
- ThanVien1: Hoan thien train models, xay dung RAG
- ThanVien2: API phan tich hop dong, chatbot backend
- ThanVien3: Ket noi frontend voi API, UI ket qua phan tich

### GIAI DOAN 3: Integration & Polish (Tuan 2)
- ThanVien1: TOi uu AI, xu ly edge cases
- ThanVien2: Payment integration, testing
- ThanVien3: UI/UX polish, admin dashboard, testing

---

## 5. BANG PHAN CONG CHI TIET

| # | Cong viec | Thanh vien |
|---|-----------|------------|
| 1 | Database schema + MongoDB setup | ThanVien2 |
| 2 | Backend API chinh (auth, upload, analysis) | ThanVien2 |
| 3 | Tich hop thanh toan VNPay | ThanVien2 |
| 4 | Quan ly mau van ban (DOCX/PDF) | ThanVien2 |
| 5 | Import van ban phap luat vao MongoDB | ThanVien2 |
| 6 | Train model phan loai hop dong | ThanVien1 |
| 7 | Train model danh gia rui ro | ThanVien1 |
| 8 | Train model phat hien vi pham | ThanVien1 |
| 9 | Xay dung RAG (BM25 + Vector search) | ThanVien1 |
| 10 | AI Chatbot Agent (LangGraph) | ThanVien1 |
| 11 | Sinh du lieu huấn luyện | ThanVien1 |
| 12 | PDF OCR | ThanVien1 |
| 13 | Frontend routing + layout | ThanVien3 |
| 14 | Upload + Analysis results UI | ThanVien3 |
| 15 | Chatbot UI | ThanVien3 |
| 16 | Pricing plans + Payment UI | ThanVien3 |
| 17 | Admin Dashboard | ThanVien3 |
| 18 | Login/Register/Account settings | ThanVien3 |
| 19 | Lich su phan tich | ThanVien3 |
| 20 | Documentation + Final testing | Tat ca |

---

## 6. GHI CHU

- **Tien do hien tai:** Backend API co ban + AI models da co, Frontend UI da co nhieu trang.
- **Cong nghe chinh:**
  - Backend: Python, FastAPI, PyMongo, LangChain/LangGraph, scikit-learn, sentence-transformers
  - Frontend: React 19, Vite, Tailwind CSS, Radix UI, React Router DOM
  - Database: MongoDB
  - AI: OpenAI GPT-4, SVM, BM25, sentence embeddings
  - Payment: VNPay
- **Khi can tro giup:** Lien he thanh vien phu trách theo bang phan cong.
