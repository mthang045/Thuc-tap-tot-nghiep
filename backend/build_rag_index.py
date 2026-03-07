"""
PageIndex RAG System - Retrieval-Augmented Generation
Vector embeddings cho semantic search trong văn bản pháp luật
"""

import os
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
import pymongo
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Tuple
import json

# MongoDB connection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['legal_AI_db']

class PageIndexRAG:
    """
    RAG System với vector embeddings để semantic search
    Sử dụng sentence-transformers để tạo embeddings cho văn bản pháp luật
    """
    
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initialize RAG system
        
        Args:
            model_name: Model name từ sentence-transformers (support tiếng Việt)
        """
        print(f"🤖 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.documents = None
        self.index_metadata = None
        
        # Thư mục lưu embeddings
        self.embeddings_dir = os.path.join(os.path.dirname(__file__), 'embeddings')
        os.makedirs(self.embeddings_dir, exist_ok=True)
        
        print("✅ RAG System initialized")
    
    def create_embeddings_from_mongodb(self):
        """
        Tạo embeddings cho tất cả văn bản pháp luật từ MongoDB
        Embeddings cho cả full_content và từng section
        """
        print("\n📚 Đang tạo embeddings từ MongoDB...")
        
        legal_docs_collection = db['legal_documents']
        documents = list(legal_docs_collection.find())
        
        if not documents:
            print("❌ Không có văn bản pháp luật trong database!")
            return False
        
        print(f"📄 Tìm thấy {len(documents)} văn bản pháp luật")
        
        # Chuẩn bị data để embed
        texts_to_embed = []
        document_metadata = []
        
        for doc in documents:
            doc_id = str(doc['_id'])
            law_name = doc.get('law_name', 'Unknown')
            
            # 1. Embed toàn bộ nội dung (tóm tắt nếu quá dài)
            full_content = doc.get('full_content', '')
            if len(full_content) > 5000:
                # Lấy 5000 ký tự đầu làm representative text
                full_content = full_content[:5000]
            
            texts_to_embed.append(full_content)
            document_metadata.append({
                'doc_id': doc_id,
                'law_name': law_name,
                'type': 'full_document',
                'category': doc.get('category', ''),
                'year': doc.get('year', 0),
                'section_index': -1
            })
            
            # 2. Embed từng section
            sections = doc.get('sections', [])
            for idx, section in enumerate(sections):
                section_title = section.get('title', '')
                section_content = section.get('content', '')
                
                # Kết hợp title + content
                section_text = f"{section_title}\n{section_content}"
                
                texts_to_embed.append(section_text)
                document_metadata.append({
                    'doc_id': doc_id,
                    'law_name': law_name,
                    'type': 'section',
                    'section_title': section_title,
                    'section_index': idx,
                    'category': doc.get('category', ''),
                    'year': doc.get('year', 0)
                })
        
        print(f"📝 Tổng cộng {len(texts_to_embed)} đoạn text để embed")
        print(f"   - {len(documents)} full documents")
        print(f"   - {len(texts_to_embed) - len(documents)} sections")
        
        # Tạo embeddings (batch processing)
        print("🔮 Đang tạo embeddings (có thể mất vài phút)...")
        embeddings = self.model.encode(
            texts_to_embed,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"✅ Embeddings shape: {embeddings.shape}")
        
        # Lưu vào memory
        self.embeddings = embeddings
        self.documents = document_metadata
        
        # Metadata
        self.index_metadata = {
            'total_documents': len(documents),
            'total_embeddings': len(texts_to_embed),
            'embedding_dim': embeddings.shape[1],
            'model_name': self.model.get_sentence_embedding_dimension(),
            'created_at': datetime.now().isoformat()
        }
        
        return True
    
    def save_embeddings(self):
        """Lưu embeddings và metadata vào disk"""
        print("\n💾 Lưu embeddings...")
        
        if self.embeddings is None:
            print("❌ Chưa có embeddings để lưu!")
            return False
        
        # Lưu embeddings
        embeddings_path = os.path.join(self.embeddings_dir, 'legal_embeddings.npy')
        np.save(embeddings_path, self.embeddings)
        print(f"✅ Đã lưu embeddings: {embeddings_path}")
        
        # Lưu document metadata
        metadata_path = os.path.join(self.embeddings_dir, 'document_metadata.pkl')
        joblib.dump(self.documents, metadata_path)
        print(f"✅ Đã lưu metadata: {metadata_path}")
        
        # Lưu index metadata
        index_path = os.path.join(self.embeddings_dir, 'index_metadata.json')
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index_metadata, f, ensure_ascii=False, indent=2)
        print(f"✅ Đã lưu index metadata: {index_path}")
        
        return True
    
    def load_embeddings(self):
        """Load embeddings từ disk"""
        print("📂 Loading embeddings từ disk...")
        
        embeddings_path = os.path.join(self.embeddings_dir, 'legal_embeddings.npy')
        metadata_path = os.path.join(self.embeddings_dir, 'document_metadata.pkl')
        index_path = os.path.join(self.embeddings_dir, 'index_metadata.json')
        
        if not os.path.exists(embeddings_path):
            print("❌ Không tìm thấy embeddings file!")
            return False
        
        # Load embeddings
        self.embeddings = np.load(embeddings_path)
        print(f"✅ Loaded embeddings shape: {self.embeddings.shape}")
        
        # Load metadata
        self.documents = joblib.load(metadata_path)
        print(f"✅ Loaded {len(self.documents)} document metadata")
        
        # Load index metadata
        with open(index_path, 'r', encoding='utf-8') as f:
            self.index_metadata = json.load(f)
        
        return True
    
    def semantic_search(self, query: str, top_k: int = 5, filter_category: str = None) -> List[Dict]:
        """
        Semantic search với cosine similarity
        
        Args:
            query: Query text
            top_k: Số lượng kết quả trả về
            filter_category: Lọc theo category (optional)
        
        Returns:
            List of search results với scores
        """
        if self.embeddings is None:
            print("❌ Embeddings chưa được load!")
            return []
        
        # Embed query
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]
        
        # Cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Filter by category nếu cần
        if filter_category:
            filtered_indices = [
                i for i, doc in enumerate(self.documents)
                if doc['category'] == filter_category
            ]
            filtered_similarities = similarities[filtered_indices]
            top_indices = np.argsort(filtered_similarities)[-top_k:][::-1]
            top_indices = [filtered_indices[i] for i in top_indices]
        else:
            # Lấy top_k cao nhất
            top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Tạo kết quả
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            metadata = self.documents[idx]
            
            # Lấy content từ MongoDB
            doc_id = metadata['doc_id']
            legal_doc = db['legal_documents'].find_one({'_id': ObjectId(doc_id)})
            
            if legal_doc:
                if metadata['type'] == 'full_document':
                    content = legal_doc.get('full_content', '')[:500] + '...'
                else:
                    section_idx = metadata['section_index']
                    sections = legal_doc.get('sections', [])
                    if section_idx < len(sections):
                        section = sections[section_idx]
                        content = section.get('content', '')
                    else:
                        content = ''
                
                results.append({
                    'doc_id': doc_id,
                    'law_name': metadata['law_name'],
                    'type': metadata['type'],
                    'section_title': metadata.get('section_title', ''),
                    'section_index': metadata.get('section_index', -1),
                    'category': metadata['category'],
                    'year': metadata['year'],
                    'content': content,
                    'similarity_score': score
                })
        
        return results
    
    def get_relevant_context(self, query: str, max_length: int = 2000) -> str:
        """
        Lấy context phù hợp nhất cho RAG
        Kết hợp nhiều sections relevant vào một context
        
        Args:
            query: Query text
            max_length: Độ dài tối đa của context
        
        Returns:
            Context string để đưa vào LLM
        """
        results = self.semantic_search(query, top_k=5)
        
        context_parts = []
        current_length = 0
        
        for result in results:
            law_name = result['law_name']
            content = result['content']
            
            # Format context piece
            if result['type'] == 'section':
                piece = f"[{law_name} - {result['section_title']}]\n{content}\n"
            else:
                piece = f"[{law_name}]\n{content}\n"
            
            # Kiểm tra độ dài
            if current_length + len(piece) > max_length:
                break
            
            context_parts.append(piece)
            current_length += len(piece)
        
        context = "\n---\n".join(context_parts)
        return context

def main():
    """Main function để build PageIndex"""
    print("="*60)
    print("      PAGEINDEX RAG SYSTEM - BUILD EMBEDDINGS")
    print("="*60)
    
    # Initialize RAG
    rag = PageIndexRAG()
    
    # Tạo embeddings từ MongoDB
    success = rag.create_embeddings_from_mongodb()
    
    if not success:
        print("❌ Không thể tạo embeddings!")
        return
    
    # Lưu embeddings
    rag.save_embeddings()
    
    # Test semantic search
    print("\n" + "="*60)
    print("🧪 TEST SEMANTIC SEARCH")
    print("="*60)
    
    test_queries = [
        "Hợp đồng lao động có thời hạn",
        "Quyền và nghĩa vụ của người thuê nhà",
        "Điều kiện thành lập doanh nghiệp",
        "Thuế thu nhập cá nhân",
        "Quyền sử dụng đất"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = rag.semantic_search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. [{result['similarity_score']:.3f}] {result['law_name']}")
            if result['type'] == 'section':
                print(f"      Section: {result['section_title']}")
    
    print("\n" + "="*60)
    print("✅ HOÀN THÀNH BUILD PAGEINDEX RAG!")
    print(f"📊 Total embeddings: {rag.index_metadata['total_embeddings']}")
    print(f"📊 Embedding dimension: {rag.index_metadata['embedding_dim']}")
    print(f"📁 Embeddings directory: {rag.embeddings_dir}")
    print("="*60)

if __name__ == '__main__':
    main()
