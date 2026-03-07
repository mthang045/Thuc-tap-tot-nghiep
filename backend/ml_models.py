"""
SVM và RAG Model Loaders
Wrapper classes để load và sử dụng models đã train
"""

import os
import joblib
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from bson import ObjectId
import pymongo

# MongoDB connection  
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['legal_AI_db']


class SVMContractClassifierV2:
    """
    Load và sử dụng SVM model đã train để classify loại hợp đồng
    """
    
    def __init__(self, model_dir='models'):
        """Initialize với đường dẫn đến models directory"""
        self.model_dir = Path(model_dir)
        self.model = None
        self.vectorizer = None
        self.metadata = None
        self.categories = None
        
        self._load_models()
    
    def _load_models(self):
        """Load SVM model, vectorizer và metadata"""
        try:
            model_path = self.model_dir / 'svm_contract_classifier.pkl'
            vectorizer_path = self.model_dir / 'tfidf_vectorizer.pkl'
            metadata_path = self.model_dir / 'model_metadata.pkl'
            
            if not model_path.exists():
                print(f"⚠️ SVM model không tồn tại: {model_path}")
                print(f"💡 Chạy: python train_svm_model.py để train model")
                return
            
            # Load model
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.metadata = joblib.load(metadata_path)
            self.categories = self.metadata.get('categories', {})
            
            print(f"✅ Loaded SVM model (accuracy: {self.metadata.get('accuracy', 0):.2%})")
            
        except Exception as e:
            print(f"❌ Không thể load SVM model: {e}")
    
    def classify(self, text: str):
        """
        Phân loại hợp đồng
        
        Args:
            text: Nội dung hợp đồng
            
        Returns:
            dict với category, label và confidence
        """
        if self.model is None:
            return {
                'success': False,
                'error': 'Model not loaded',
                'category_code': 'khac',
                'category_name': 'Hợp đồng khác',
                'confidence': 0.0
            }
        
        try:
            # Transform text
            X = self.vectorizer.transform([text])
            
            # Predict
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            confidence = float(max(probabilities))
            
            # Get category name
            category_name = self.categories.get(prediction, 'Unknown')
            
            return {
                'success': True,
                'category_code': prediction,
                'category_name': category_name,
                'confidence': confidence,
                'all_scores': {
                    self.categories.get(cat, cat): float(prob)
                    for cat, prob in zip(self.model.classes_, probabilities)
                }
            }
            
        except Exception as e:
            print(f"❌ Classification error: {e}")
            return {
                'success': False,
                'error': str(e),
                'category_code': 'khac',
                'category_name': 'Hợp đồng khác',
                'confidence': 0.0
            }
    
    def is_loaded(self):
        """Check if model đã được load thành công"""
        return self.model is not None


class RAGRetrieverV2:
    """
    Load và sử dụng RAG embeddings để semantic search
    """
    
    def __init__(self, embeddings_dir='embeddings'):
        """Initialize với đường dẫn đến embeddings directory"""
        self.embeddings_dir = Path(embeddings_dir)
        self.model = None
        self.embeddings = None
        self.documents = None
        self.index_metadata = None
        
        self._load_model()
        self._load_embeddings()
    
    def _load_model(self):
        """Load sentence transformer model"""
        try:
            print("🤖 Loading embedding model...")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"❌ Không thể load embedding model: {e}")
    
    def _load_embeddings(self):
        """Load embeddings và metadata từ disk"""
        try:
            embeddings_path = self.embeddings_dir / 'legal_embeddings.npy'
            metadata_path = self.embeddings_dir / 'document_metadata.pkl'
            
            if not embeddings_path.exists():
                print(f"⚠️ Embeddings không tồn tại: {embeddings_path}")
                print(f"💡 Chạy: python build_rag_index.py để build embeddings")
                return
            
            # Load embeddings
            self.embeddings = np.load(embeddings_path)
            self.documents = joblib.load(metadata_path)
            
            print(f"✅ Loaded {len(self.embeddings)} embeddings")
            
        except Exception as e:
            print(f"❌ Không thể load embeddings: {e}")
    
    def search(self, query: str, top_k: int = 5, filter_category: str = None):
        """
        Semantic search với vector similarity
        
        Args:
            query: Query text
            top_k: Số lượng kết quả
            filter_category: Lọc theo category (optional)
            
        Returns:
            List of search results
        """
        if self.model is None or self.embeddings is None:
            return {
                'success': False,
                'error': 'Model or embeddings not loaded',
                'results': []
            }
        
        try:
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
                    if doc.get('category', '') == filter_category
                ]
                if filtered_indices:
                    filtered_similarities = similarities[filtered_indices]
                    top_indices = np.argsort(filtered_similarities)[-top_k:][::-1]
                    top_indices = [filtered_indices[i] for i in top_indices]
                else:
                    top_indices = []
            else:
                # Lấy top_k cao nhất
                top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Build results
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                metadata = self.documents[idx]
                
                # Get content từ MongoDB
                doc_id = metadata['doc_id']
                try:
                    legal_doc = db['legal_documents'].find_one({'_id': ObjectId(doc_id)})
                    
                    if legal_doc:
                        if metadata['type'] == 'full_document':
                            content = legal_doc.get('full_content', '')[:500]
                            if len(legal_doc.get('full_content', '')) > 500:
                                content += '...'
                        else:
                            section_idx = metadata.get('section_index', 0)
                            sections = legal_doc.get('sections', [])
                            if section_idx < len(sections):
                                section = sections[section_idx]
                                content = section.get('content', '')
                            else:
                                content = ''
                        
                        results.append({
                            'doc_id': doc_id,
                            'law_name': metadata.get('law_name', ''),
                            'type': metadata.get('type', ''),
                            'section_title': metadata.get('section_title', ''),
                            'section_index': metadata.get('section_index', -1),
                            'category': metadata.get('category', ''),
                            'year': metadata.get('year', 0),
                            'content': content,
                            'similarity_score': score
                        })
                except Exception as e:
                    print(f"⚠️ Error loading doc {doc_id}: {e}")
                    continue
            
            return {
                'success': True,
                'query': query,
                'total_results': len(results),
                'results': results
            }
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def get_context(self, query: str, max_length: int = 2000):
        """
        Lấy relevant context để đưa vào LLM (RAG)
        
        Args:
            query: Query text
            max_length: Độ dài tối đa của context
            
        Returns:
            Context string
        """
        search_result = self.search(query, top_k=5)
        
        if not search_result['success']:
            return ""
        
        context_parts = []
        current_length = 0
        
        for result in search_result['results']:
            law_name = result['law_name']
            content = result['content']
            
            # Format context
            if result['type'] == 'section':
                piece = f"[{law_name} - {result['section_title']}]\n{content}\n"
            else:
                piece = f"[{law_name}]\n{content}\n"
            
            # Check length
            if current_length + len(piece) > max_length:
                break
            
            context_parts.append(piece)
            current_length += len(piece)
        
        context = "\n---\n".join(context_parts)
        return context
    
    def is_loaded(self):
        """Check if embeddings đã được load thành công"""
        return self.model is not None and self.embeddings is not None


# Global instances (lazy loading)
_svm_classifier = None
_rag_retriever = None


def get_svm_classifier():
    """Get global SVM classifier instance"""
    global _svm_classifier
    if _svm_classifier is None:
        _svm_classifier = SVMContractClassifierV2()
    return _svm_classifier


def get_rag_retriever():
    """Get global RAG retriever instance"""
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = RAGRetrieverV2()
    return _rag_retriever
