# LegalAgentRAG

## Hướng dẫn chạy dự án

1. Tạo file `.env` và điền API Key (OpenAI, Gemini...)
2. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```
3. Chạy script khởi tạo Vector DB:
   ```bash
   python setup_knowledge.py
   ```
4. Khởi động giao diện:
   ```bash
   streamlit run app.py
   ```

## Cấu trúc thư mục
```
LegalAgentRAG/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── setup_knowledge.py
├── app.py
│
├── data/
│   ├── source_laws/
│   ├── vector_store/
│   └── test_contracts/
│
└── src/
    ├── __init__.py
    ├── config.py
    ├── ingest.py
    ├── vector_db.py
    │
    └── workflow/
        ├── __init__.py
        ├── state.py
        ├── nodes.py
        └── graph.py
```
