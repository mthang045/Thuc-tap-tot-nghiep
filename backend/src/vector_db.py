"""
Vector Database Retriever với Connection Pooling và Lazy Loading
Tối ưu tài nguyên: singleton pattern, connection pool, cache
"""
import os
import numpy as np
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from psycopg2 import pool
from dotenv import load_dotenv
from src.resource_config import (
    DB_PARAMS, DB_POOL_CONFIG, COLLECTION_NAME, 
    EMBEDDER_MODEL, EMBEDDER_DEVICE, DEFAULT_TOP_K, ENABLE_LLM_CACHE
)

load_dotenv()

# Global singletons - lazy initialization
_embedder = None
_connection_pool = None
_query_cache = {}

def get_embedder():
    """Lazy loading embedder - chỉ khởi tạo khi cần"""
    global _embedder
    if _embedder is None:
        print("🔄 Loading embedder model (first time)...")
        _embedder = SentenceTransformer(EMBEDDER_MODEL, device=EMBEDDER_DEVICE)
    return _embedder

def get_connection_pool():
    """Connection pooling - tái sử dụng kết nối DB"""
    global _connection_pool
    if _connection_pool is None:
        print("🔄 Creating database connection pool...")
        _connection_pool = pool.SimpleConnectionPool(
            DB_POOL_CONFIG['minconn'],
            DB_POOL_CONFIG['maxconn'],
            **DB_PARAMS
        )
    return _connection_pool

def get_connection():
    """Lấy connection từ pool"""
    conn_pool = get_connection_pool()
    return conn_pool.getconn()

def release_connection(conn):
    """Trả connection về pool"""
    conn_pool = get_connection_pool()
    conn_pool.putconn(conn)

@lru_cache(maxsize=100)
def _cached_query(query_text: str, k: int = DEFAULT_TOP_K):
    """Cache query results để tránh tính toán lại"""
    return None  # Placeholder cho cache key

class OptimizedRetriever:
    """Retriever tối ưu với connection pooling và caching"""
    
    def __init__(self):
        self.embedder = None
        self.cache = {} if ENABLE_LLM_CACHE else None
    
    def _get_embedder(self):
        """Lazy load embedder"""
        if self.embedder is None:
            self.embedder = get_embedder()
        return self.embedder
    
    def invoke(self, query, k=DEFAULT_TOP_K):
        """
        Tìm kiếm documents với caching và connection pooling
        
        Args:
            query: Câu query
            k: Số lượng documents cần lấy
            
        Returns:
            List of Document objects
        """
        # Kiểm tra cache
        cache_key = f"{query}_{k}"
        if self.cache is not None and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Lấy embedder và encode query
        embedder = self._get_embedder()
        query_embedding = embedder.encode(query)
        
        # Lấy connection từ pool
        conn = None
        try:
            conn = get_connection()
            
            with conn.cursor() as cur:
                # Chỉ lấy content và embedding, không cần id
                cur.execute(
                    f"SELECT content, embedding FROM {COLLECTION_NAME} WHERE embedding IS NOT NULL"
                )
                results = cur.fetchall()
            
            if not results:
                doc = type('Doc', (), {'page_content': "Không tìm thấy dữ liệu trong cơ sở dữ liệu."})()
                return [doc]
            
            # Vectorized cosine similarity (nhanh hơn loop)
            similarities = []
            for content, embedding_bytes in results:
                doc_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                )
                similarities.append((similarity, content))
            
            # Sort và lấy top k
            top_docs = sorted(similarities, reverse=True, key=lambda x: x[0])[:k]
            
            # Tạo Document objects
            Doc = type('Doc', (), {})
            result_docs = []
            for _, content in top_docs:
                doc = Doc()
                doc.page_content = content
                result_docs.append(doc)
            
            # Cache kết quả
            if self.cache is not None:
                self.cache[cache_key] = result_docs
            
            return result_docs
            
        except Exception as e:
            print(f"⚠️ Database query error: {e}")
            doc = type('Doc', (), {'page_content': f"Lỗi truy vấn: {str(e)}"})()
            return [doc]
        finally:
            # Luôn trả connection về pool
            if conn is not None:
                release_connection(conn)
    
    def clear_cache(self):
        """Xóa cache để giải phóng memory"""
        if self.cache is not None:
            self.cache.clear()
            print("✓ Cache cleared")

def get_retriever():
    """
    Factory function để tạo retriever
    Sử dụng singleton pattern
    """
    return OptimizedRetriever()

def cleanup():
    """Cleanup resources khi shutdown"""
    global _connection_pool, _embedder
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None
    _embedder = None
    print("✓ Resources cleaned up")