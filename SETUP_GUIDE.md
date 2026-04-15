# 🚀 Setup & Development Guide

## 📦 Quick Start

### 1. Prerequisites
- Python 3.12+
- Docker Desktop
- Node.js 18+ (cho frontend)
- Tesseract OCR (cho xử lý PDF scan)

### 2. Clone & Install

```bash
# Clone repository
git clone <your-repo>
cd Thuc_tap

# Install Python dependencies
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt

# Install frontend dependencies (optional)
cd frontend
npm install
```

### 3. Database Setup (MongoDB)

```bash
# Khởi động MongoDB container
docker-compose up -d db

# MongoDB sẽ chạy ở:
# - Host: localhost:27017
# - Database: legal_db
# - No authentication (development)
```

### 4. Build PageIndex

```bash
# Build PageIndex tree từ văn bản pháp luật
cd backend
python ingest_pageindex.py

# Nhập 'y' để xác nhận build
# ✅ PageIndex cache sẽ được lưu tại data/page_index_cache.pkl
```

### 5. Train SVM Models

```bash
# Train SVM classifier cho phân loại hợp đồng
python train_svm.py

# Models sẽ được lưu tại models/svm/
```

### 6. Run Application

```bash
# Backend (Django)
cd backend
python manage.py migrate
python manage.py runserver

# Frontend (React - optional)
cd frontend
npm run dev
```

## 🗂️ Project Structure

```
Thuc_tap/
├── backend/
│   ├── src/
│   │   ├── classifier/           # SVM classification
│   │   ├── page_index.py         # PageIndex implementation
│   │   └── workflow/             # LangGraph workflow
│   ├── data/
│   │   ├── source_laws/          # Văn bản pháp luật
│   │   └── page_index_cache.pkl  # PageIndex cache
│   ├── models/svm/               # Trained SVM models
│   ├── train_svm.py              # SVM training script
│   ├── ingest_pageindex.py       # PageIndex builder
│   └── manage.py                 # Django management
├── frontend/                     # React frontend
├── docker-compose.yml            # MongoDB container
└── .env                          # Environment config
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/legal_db
MONGODB_DB=legal_db
MONGODB_HOST=localhost
MONGODB_PORT=27017

# Django Settings
DEBUG=1
SECRET_KEY=your-secret-key

# AI API Keys
GROQ_API_KEY=your-groq-api-key
```

### MongoDB Collections

System tự động tạo các collections:
- **users** - User accounts
- **contracts** - Contract analysis results
- **legal_documents** - Legal reference documents
- **analysis_history** - Analysis request history
- **svm_predictions** - SVM model predictions
- **pageindex_cache** - PageIndex tree cache

## 🔧 Development Tips

### Tesseract OCR Setup (cho PDF scan)

1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install với Vietnamese language pack
3. Path: `C:\Program Files\Tesseract-OCR`

```python
# Sử dụng OCR trong code
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### MongoDB Connection (VSCode)

1. Install "MongoDB for VS Code" extension
2. Add connection: `mongodb://localhost:27017`
3. Browse database: `legal_db`

### Hot Reload

```bash
# Backend auto-reload
python manage.py runserver

# Frontend hot reload
npm run dev
```

## 🎯 Key Features Implemented

### ✅ PageIndex RAG (98.7% accuracy)
- Tree-based document indexing
- No vector embeddings needed
- Transparent reasoning process
- Respects document structure

### ✅ SVM Classification
- Contract type classification (5 types)
- Risk level assessment (3 levels)
- Violation detection
- Trained on Vietnamese legal contracts

### ✅ LangGraph Workflow
- Multi-agent analysis pipeline
- Contract classification → Extraction → Research → Analysis
- Streaming responses

### ✅ MongoDB Integration
- Document-based storage
- Flexible schema
- Better for hierarchical data
- Easy to scale

## 📚 Documentation Files

- **README.md** - Project overview & features
- **PAGEINDEX_GUIDE_VI.md** - PageIndex detailed guide
- **LAWS_NEEDED.md** - Required legal documents
- **Attributions.md** - Credits & licenses

## 🐛 Common Issues

### MongoDB connection failed
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# Restart MongoDB
docker-compose restart db
```

### PageIndex build error
```bash
# Check data folder exists
ls backend/data/source_laws/

# Rebuild cache
python ingest_pageindex.py
```

### SVM training error
```bash
# Check models directory
mkdir -p backend/models/svm

# Re-train models
python train_svm.py
```

## 🚀 Next Steps

1. **Add more training data** for SVM models
2. **Implement payment integration** (VNPay/MoMo)
3. **Add user authentication** endpoints
4. **Deploy to production** with Docker
5. **Add more legal document sources**

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📝 License

See LICENSE file for details.
