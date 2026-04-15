import re
import os
from typing import List
from pypdf import PdfReader  # Dùng pypdf thay vì PyPDF2 (pypdf là bản mới hơn)
from langchain_core.documents import Document
from langchain_postgres import PGVector
from sentence_transformers import SentenceTransformer
import numpy as np

# Import biến môi trường cho DB connection
from dotenv import load_dotenv

# Load biến môi trường (ưu tiên .env.local nếu có)
load_dotenv('.env.local')
load_dotenv()  # Fallback to .env

# Lấy chuỗi kết nối từ .env
CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", "postgresql+psycopg://admin:Buithang12@localhost:5432/legal_db")
COLLECTION_NAME = "legal_documents"
# Custom Embeddings class cho sentence-transformers
class LocalEmbeddings:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts):
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]
    
    def embed_query(self, text):
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
def clean_text(text: str) -> str:
    """Làm sạch văn bản: xóa khoảng trắng thừa, nối dòng bị ngắt."""
    if not text: 
        return ""
    text = re.sub(r'\s+', ' ', text)  # Thay thế nhiều khoảng trắng bằng 1 dấu cách
    text = text.strip()
    return text

def split_by_article(text: str, source_name: str) -> List[Document]:
    """
    Hàm cắt văn bản thông minh dựa trên từ khóa 'Điều <số>.'
    Nếu không tìm thấy, sẽ chia thành chunks cố định.
    """
    # Regex tìm: Bắt đầu dòng hoặc sau dấu xuống dòng, chữ "Điều", khoảng trắng, số, dấu chấm
    pattern = r"(?:^|\n)(Điều\s+\d+\.)"
    splits = re.split(pattern, text)
    
    documents = []
    
    if len(splits) > 1:
        # Tách theo điều luật
        for i in range(1, len(splits) - 1, 2):
            header = splits[i].strip()
            content = splits[i+1].strip()
            full_clause = f"{header} {content}"
            
            try:
                article_id = re.search(r'\d+', header).group()
            except AttributeError:
                article_id = "unknown"
            
            doc = Document(
                page_content=full_clause,
                metadata={
                    "source": source_name,
                    "article_id": article_id,
                    "type": "legal_article"
                }
            )
            documents.append(doc)
    else:
        # Không tìm thấy điều khoản, chia thành chunks cố định
        words = text.split()
        chunk_size = 500
        overlap = 50
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": source_name,
                        "chunk_id": i // (chunk_size - overlap),
                        "type": "legal_chunk"
                    }
                )
                documents.append(doc)
            
    return documents

def ingest_pdf_to_postgres(pdf_path: str):
    """Hàm chính để nạp dữ liệu"""
    print(f"🔄 Đang xử lý file: {pdf_path}...")
    
    try:
        # 1. Load PDF
        reader = PdfReader(pdf_path)
        
        # Trích xuất text từ từng trang và nối lại
        full_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"
        
        full_text = clean_text(full_text)
        
        # 2. Cắt nhỏ (Chunking) theo Điều luật
        docs = split_by_article(full_text, source_name=os.path.basename(pdf_path))
        print(f"✅ Đã tách thành {len(docs)} điều khoản/chunk.")
        
        if not docs:
            print("⚠️ Cảnh báo: File rỗng hoặc không thể xử lý.")
            return

        # 3. Embedding & Lưu vào Postgres
        print("🚀 Đang embedding và đẩy vào PostgreSQL (có thể mất vài giây)...")
        
        embeddings = LocalEmbeddings()
        
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=CONNECTION_STRING,
            use_jsonb=True,
        )
        
        # Hàm này sẽ tự động: Embed text -> Tạo vector -> Lưu vào bảng
        vector_store.add_documents(docs)
        
        print("🎉 Hoàn tất! Dữ liệu đã nằm trong Database.")
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra khi xử lý file {pdf_path}: {e}")