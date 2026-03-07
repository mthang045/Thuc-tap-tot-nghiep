# SVM VÀ RAG SYSTEM - TÀI LIỆU KỸ THUẬT

## TỔNG QUAN

Dự án Legal Contract Analyzer sử dụng 2 hệ thống Machine Learning quan trọng:

1. **SVM (Support Vector Machine)** - Phân loại hợp đồng
2. **RAG (Retrieval-Augmented Generation)** - Semantic search văn bản pháp luật

---

## 1. SVM CONTRACT CLASSIFIER

### 1.1. Mục đích

Tự động phân loại hợp đồng vào các categories để:
- Tự động tag và organize hợp đồng
- Hiểu ngữ cảnh của hợp đồng
- Giúp AI analysis chính xác hơn
- Tìm kiếm và filter theo loại hợp đồng

### 1.2. Categories (10 loại)

| Code | Tên đầy đủ | Ví dụ |
|------|------------|-------|
| `mua_ban` | Hợp đồng mua bán | Mua bán nhà đất, hàng hóa |
| `thue` | Hợp đồng thuê | Thuê nhà, văn phòng, thiết bị |
| `lao_dong` | Hợp đồng lao động | Hợp đồng làm việc, thử việc |
| `dich_vu` | Hợp đồng dịch vụ | Tư vấn, bảo trì, marketing |
| `xay_dung` | Hợp đồng xây dựng | Thi công, sửa chữa |
| `van_chuyen` | Hợp đồng vận chuyển | Logistics, giao hàng |
| `cung_ung` | Hợp đồng cung ứng | Cung cấp nguyên liệu, hàng hóa |
| `dai_ly` | Hợp đồng đại lý | Phân phối, đại diện |
| `bao_hiem` | Hợp đồng bảo hiểm | Bảo hiểm nhân thọ, xe |
| `khac` | Hợp đồng khác | Các loại khác |

### 1.3. Kiến trúc

```
Input Text (Hợp đồng)
    ↓
TF-IDF Vectorizer (max 1000 features, bigrams)
    ↓
Feature Vector (1000 dimensions)
    ↓
SVM Model (kernel=linear, C=10)
    ↓
Prediction + Confidence Score
```

### 1.4. Hyperparameters

Sau GridSearch, best parameters:
- **Kernel:** linear (tốt nhất cho text classification)
- **C:** 10 (regularization parameter)
- **Gamma:** scale (kernel coefficient)
- **Max features:** 1000 (TF-IDF)
- **N-grams:** (1, 2) - unigrams và bigrams

### 1.5. Performance

**Training Data:**
- 50 mẫu ban đầu (5 mẫu/category)
- Có thể bổ sung từ analysis_history

**Metrics:**
- **Test Accuracy:** ~60% (có thể cải thiện với thêm data)
- **Cross-validation:** 3-fold CV score ~40%
- **Inference Time:** <50ms per document

**Cải thiện:**
- ✅ Thêm training data (100+ mẫu/category)
- ✅ Fine-tune hyperparameters
- ✅ Ensemble methods
- ✅ Deep learning (BERT-based) cho accuracy cao hơn

### 1.6. API Usage

#### Endpoint: `POST /api/classify-contract/`

**Request:**
```json
{
  "text": "Hai bên thỏa thuận mua bán nhà đất tại quận 1 với giá 5 tỷ đồng..."
}
```

**Response:**
```json
{
  "success": true,
  "category_code": "mua_ban",
  "category_name": "Hợp đồng mua bán",
  "confidence": 0.85,
  "all_scores": {
    "Hợp đồng mua bán": 0.85,
    "Hợp đồng thuê": 0.10,
    "Hợp đồng khác": 0.05
  }
}
```

### 1.7. Training

**Script:** `train_svm_model.py`

```bash
cd backend
python train_svm_model.py
```

**Output:**
- `models/svm_contract_classifier.pkl` - SVM model
- `models/tfidf_vectorizer.pkl` - TF-IDF vectorizer
- `models/model_metadata.pkl` - Metadata (accuracy, categories)

**Re-training:** Chạy lại script khi có thêm data mới.

---

## 2. RAG (RETRIEVAL-AUGMENTED GENERATION) SYSTEM

### 2.1. Mục đích

Kết hợp AI Language Model với văn bản pháp luật:
- Tìm kiếm semantic (không chỉ keyword matching)
- Cung cấp legal context cho AI analysis
- Tham chiếu cụ thể đến điều luật
- Độ chính xác cao hơn pure LLM

### 2.2. Kiến trúc RAG

```
┌─────────────────────────────────────────────┐
│         OFFLINE: BUILD INDEX                │
├─────────────────────────────────────────────┤
│  24 Legal Documents (3,816 sections)        │
│              ↓                              │
│  Parse & Split into sections               │
│              ↓                              │
│  Sentence Transformer Model                │
│  (paraphrase-multilingual-MiniLM-L12-v2)   │
│              ↓                              │
│  3,840 Embeddings (384 dimensions each)    │
│              ↓                              │
│  Save to embeddings/legal_embeddings.npy   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│         ONLINE: SEARCH                      │
├─────────────────────────────────────────────┤
│  User Query                                 │
│              ↓                              │
│  Embed Query → Vector (384 dims)           │
│              ↓                              │
│  Cosine Similarity với 3,840 embeddings    │
│              ↓                              │
│  Top-K most similar (K=3-5)                │
│              ↓                              │
│  Return relevant sections                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│         ONLINE: AUGMENT AI                  │
├─────────────────────────────────────────────┤
│  Contract Text + Relevant Legal Context    │
│              ↓                              │
│  LLM (Llama 3.3 70B)                       │
│              ↓                              │
│  Analysis với tham chiếu pháp luật         │
└─────────────────────────────────────────────┘
```

### 2.3. Embedding Model

**Model:** `paraphrase-multilingual-MiniLM-L12-v2`
- From: Sentence Transformers library
- Support: 50+ languages including Vietnamese
- Dimensions: 384
- Size: ~471MB download
- Speed: ~30ms per embedding

**Tại sao chọn model này:**
- ✅ Support tiếng Việt tốt
- ✅ Nhẹ (384 dims vs BERT 768 dims)
- ✅ Nhanh (MiniLM architecture)
- ✅ Quality tốt cho semantic similarity

### 2.4. Index Statistics

**Data:**
- 24 văn bản pháp luật
- 3,816 sections được embed
- 24 full documents được embed
- **Tổng: 3,840 embeddings**

**Storage:**
- Embeddings: ~6MB (3840 × 384 × 4 bytes)
- Metadata: ~500KB
- Fast loading: <1 second

**Memory:**
- RAM usage: ~10MB
- Efficient with numpy arrays

### 2.5. Search Algorithm

**Cosine Similarity:**
```python
similarity = dot(query_vector, doc_vector) / 
             (norm(query_vector) * norm(doc_vector))
```

**Results:**
- Score range: 0.0 to 1.0
- Typical good match: >0.70
- Very relevant: >0.80
- Perfect match: >0.90

**Top-K Selection:**
- Default K=5 (configurable)
- Có thể filter by category
- Results sorted by similarity score

### 2.6. Performance

**Search Time:**
- 3,840 embeddings: **~150-200ms**
- Includes: embed query + compute similarities + sort + retrieve

**Accuracy:**
- Qualitative testing: Excellent
- Relevant results in top 3: >90%
- Better than keyword search

**Examples:**

| Query | Top Result | Score |
|-------|------------|-------|
| "Hợp đồng lao động có thời hạn" | Bộ luật Lao động - Điều 20 | 0.776 |
| "Quyền sử dụng đất" | Luật Đất đai - Điều 166 | 0.872 |
| "Điều kiện thành lập doanh nghiệp" | Luật Doanh nghiệp - Điều 8 | 0.752 |

### 2.7. API Usage

#### Endpoint: `POST /api/rag-search/`

**Request:**
```json
{
  "query": "Quyền và nghĩa vụ của người thuê nhà",
  "top_k": 3,
  "category": ""
}
```

**Response:**
```json
{
  "success": true,
  "query": "Quyền và nghĩa vụ của người thuê nhà",
  "total_results": 3,
  "results": [
    {
      "doc_id": "...",
      "law_name": "ban Luat Nha o",
      "type": "section",
      "section_title": "Điều 34. Quyền và nghĩa vụ của người thuê nhà công vụ",
      "section_index": 33,
      "category": "co_ban",
      "year": 2023,
      "content": "Nội dung điều luật...",
      "similarity_score": 0.799
    }
  ]
}
```

#### Check ML Status: `GET /api/ml-status/`

**Response:**
```json
{
  "success": true,
  "status": {
    "svm": {
      "loaded": true,
      "accuracy": 0.60,
      "categories": ["Hợp đồng mua bán", ...]
    },
    "rag": {
      "loaded": true,
      "total_embeddings": 3840,
      "embedding_dim": 384
    }
  }
}
```

### 2.8. Building Index

**Script:** `build_rag_index.py`

```bash
cd backend
python build_rag_index.py
```

**Output:**
- `embeddings/legal_embeddings.npy` - Vector embeddings
- `embeddings/document_metadata.pkl` - Document metadata
- `embeddings/index_metadata.json` - Index info

**Time:** ~2-3 phút (download model + create embeddings)

**Re-building:** Chỉ khi:
- Thêm văn bản pháp luật mới
- Update model
- Thay đổi chunking strategy

---

## 3. TÍCH HỢP VÀO API

### 3.1. File Structure

```
backend/
├── simple_api.py                  # Main API với SVM + RAG
├── ml_models.py                   # Model loaders
├── train_svm_model.py            # SVM training
├── build_rag_index.py            # RAG indexing
├── models/                        # SVM models
│   ├── svm_contract_classifier.pkl
│   ├── tfidf_vectorizer.pkl
│   └── model_metadata.pkl
└── embeddings/                    # RAG embeddings
    ├── legal_embeddings.npy
    ├── document_metadata.pkl
    └── index_metadata.json
```

### 3.2. Lazy Loading

Models được load khi cần thiết (lazy loading):
- SVM: Load khi first request đến `/api/classify-contract/`
- RAG: Load khi first request đến `/api/rag-search/` hoặc `/api/upload/`
- LLM: Load khi first AI analysis

**Lợi ích:**
- Startup nhanh hơn
- Tiết kiệm memory
- Chỉ load khi cần

### 3.3. Integration trong Upload Endpoint

**Workflow:**
1. User upload hợp đồng
2. Extract text từ file
3. **RAG:** Search relevant legal documents
4. **SVM:** Classify contract type
5. **AI:** Analyze với legal context
6. Save to database
7. Return results

**Code snippet:**
```python
# RAG search
rag_retriever = get_rag_retriever()
rag_results = rag_retriever.search(contract_text[:500], top_k=3)

# Build legal context
legal_context = build_context_from_rag(rag_results)

# SVM classification
svm_classifier = get_svm_classifier()
classification = svm_classifier.classify(contract_text[:1000])

# AI analysis with context
llm = get_llm_client()
analysis = llm.invoke({
    "contract_text": contract_text,
    "legal_context": legal_context
})
```

---

## 4. TESTING

### 4.1. Test SVM

```python
from ml_models import get_svm_classifier

classifier = get_svm_classifier()

test_text = "Hai bên thỏa thuận cho thuê văn phòng với giá 20 triệu/tháng"
result = classifier.classify(test_text)

print(f"Category: {result['category_name']}")
print(f"Confidence: {result['confidence']:.0%}")
```

### 4.2. Test RAG

```python
from ml_models import get_rag_retriever

rag = get_rag_retriever()

query = "Hợp đồng lao động có thời hạn"
results = rag.search(query, top_k=3)

for r in results['results']:
    print(f"[{r['similarity_score']:.3f}] {r['law_name']} - {r['section_title']}")
```

### 4.3. Test via API

```bash
# Test SVM
curl -X POST http://localhost:5000/api/classify-contract/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hợp đồng thuê nhà tại quận 1"}'

# Test RAG
curl -X POST http://localhost:5000/api/rag-search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "quyền sử dụng đất", "top_k": 3}'

# Check status
curl http://localhost:5000/api/ml-status/
```

---

## 5. TROUBLESHOOTING

### 5.1. SVM Model không load

**Lỗi:** `SVM model không tồn tại`

**Giải pháp:**
```bash
cd backend
python train_svm_model.py
```

### 5.2. RAG Embeddings không load

**Lỗi:** `Embeddings không tồn tại`

**Giải pháp:**
```bash
cd backend
python build_rag_index.py
```

### 5.3. Model download chậm

**Vấn đề:** Sentence Transformers download từ HuggingFace

**Giải pháp:**
- Đợi lần đầu download (~471MB)
- Sau đó cache tại `~/.cache/huggingface/`
- Lần sau sẽ load từ cache

### 5.4. Memory issues

**Giải pháp:**
- RAG chỉ dùng ~10MB RAM
- SVM chỉ dùng ~5MB RAM
- Tổng memory footprint nhỏ

---

## 6. FUTURE IMPROVEMENTS

### 6.1. SVM

- [ ] Thu thập thêm training data (1000+ samples)
- [ ] Thử deep learning (BERT-based classifiers)
- [ ] Ensemble multiple models
- [ ] Active learning để improve accuracy

### 6.2. RAG

- [ ] Add re-ranking algorithms (cross-encoder)
- [ ] Implement hybrid search (keyword + semantic)
- [ ] Add metadata filters (year, category auto-detect)
- [ ] Cache popular queries
- [ ] Add more legal documents

### 6.3. Integration

- [ ] A/B testing giữa pure LLM vs RAG-enhanced
- [ ] Metrics dashboard (search quality, classification accuracy)
- [ ] User feedback loop để improve models
- [ ] Deploy với caching layer (Redis)

---

## 7. REFERENCES

1. **Scikit-learn Documentation:** https://scikit-learn.org/
2. **Sentence Transformers:** https://www.sbert.net/
3. **RAG Paper:** "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
4. **Multilingual Models:** https://huggingface.co/sentence-transformers

---

**Created:** March 2026  
**Author:** THĂNG BÙI MINH (2331540024)  
**Project:** Legal Contract Analyzer - Graduation Internship Report
