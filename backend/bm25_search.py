"""
BM25 Keyword-Based Search for Legal Documents
Alternative to Vector RAG - uses statistical keyword matching instead of embeddings

BM25 (Best Matching 25) is a probabilistic ranking function based on:
- Term frequency (how often terms appear in documents)
- Inverse document frequency (how rare terms are across all documents)
- Document length normalization

Advantages over Vector RAG:
- ✅ Exact keyword matching
- ✅ No need for embedding models
- ✅ Fast and lightweight (855MB pre-built index)
- ✅ Good for legal text with specific terminology

Author: THĂNG BÙI MINH
Date: March 2026
"""

import pickle
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymongo

# MongoDB connection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['legal_AI_db']


class BM25LegalSearch:
    """
    BM25-based search for Vietnamese legal documents
    Uses pre-built BM25 index (bm25_legal_corpus file)
    """
    
    def __init__(self, corpus_file: str = 'bm25_legal_corpus'):
        """
        Initialize BM25 search
        
        Args:
            corpus_file: Path to pre-built BM25 corpus file (855MB pickle file)
        """
        self.corpus_file = Path(corpus_file)
        self.bm25 = None
        self.corpus_metadata = None
        self.documents_cache = []  # Cache MongoDB documents
        self._load_corpus()
        self._load_documents_from_mongodb()
    
    def _load_corpus(self):
        """Load pre-built BM25 index from disk"""
        try:
            if not self.corpus_file.exists():
                print(f"⚠️ BM25 corpus không tồn tại: {self.corpus_file}")
                print(f"💡 File size nên là ~855MB")
                return
            
            print(f"🔍 Loading BM25 corpus từ {self.corpus_file}...")
            print(f"   File size: {self.corpus_file.stat().st_size / (1024**2):.2f} MB")
            
            start_time = time.time()
            
            # Load pickle file
            with open(self.corpus_file, 'rb') as f:
                data = pickle.load(f)
            
            # Extract BM25 model và metadata
            if isinstance(data, dict):
                self.bm25 = data.get('bm25')
                self.corpus_metadata = data.get('metadata', [])
            else:
                # Nếu file chỉ chứa BM25 model
                self.bm25 = data
                self.corpus_metadata = []
            
            load_time = time.time() - start_time
            
            print(f"✅ BM25 corpus loaded trong {load_time:.2f}s")
            print(f"   Documents indexed: {getattr(self.bm25, 'corpus_size', 'Unknown')}")
            print(f"   Average doc length: {getattr(self.bm25, 'avgdl', 'Unknown'):.2f}")
            
        except Exception as e:
            print(f"❌ Không thể load BM25 corpus: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_documents_from_mongodb(self):
        """Load all legal documents from MongoDB for metadata mapping"""
        try:
            print("📚 Loading documents từ MongoDB...")
            
            legal_docs_collection = db['legal_documents']
            docs = list(legal_docs_collection.find())
            
            # Flatten to sections for BM25 mapping
            for doc in docs:
                law_name = doc.get('law_name', 'Unknown')
                category = doc.get('category_code', '')
                sections = doc.get('sections', [])
                
                for idx, section in enumerate(sections):
                    self.documents_cache.append({
                        'doc_id': str(doc['_id']),
                        'law_name': law_name,
                        'category': category,
                        'section_title': section.get('title', f'Phần {idx+1}'),
                        'section_content': section.get('content', '')
                    })
            
            print(f"✅ Loaded {len(self.documents_cache)} sections from {len(docs)} legal documents")
            
        except Exception as e:
            print(f"⚠️ Không thể load documents từ MongoDB: {e}")
            self.documents_cache = []
    
    def is_loaded(self) -> bool:
        """Check if BM25 index đã được load thành công"""
        return self.bm25 is not None
    
    def search(self, query: str, top_k: int = 5, filter_category: Optional[str] = None) -> Dict[str, Any]:
        """
        Search legal documents using BM25 keyword matching
        
        Args:
            query: Query string (user question/keywords)
            top_k: Number of results to return
            filter_category: Optional category filter (e.g., 'lao_dong', 'dan_su')
            
        Returns:
            Dict with search results and metadata
        """
        if not self.is_loaded():
            return {
                'success': False,
                'error': 'BM25 corpus chưa được load',
                'results': [],
                'total_results': 0,
                'search_time_ms': 0
            }
        
        try:
            start_time = time.time()
            
            # Tokenize query (simple whitespace split)
            # NOTE: For production, use proper Vietnamese tokenizer
            query_tokens = query.lower().split()
            
            print(f"🔍 BM25 Search: '{query[:50]}...'")
            print(f"   Query tokens: {query_tokens}")
            
            # Get BM25 scores
            scores = self.bm25.get_scores(query_tokens)
            
            # Get top_k indices
            import numpy as np
            top_indices = np.argsort(scores)[-top_k:][::-1]
            
            # Build results
            results = []
            for idx in top_indices:
                score = float(scores[idx])
                
                # Skip zero scores
                if score == 0:
                    continue
                
                # Get document from cache (MongoDB sections)
                # BM25 corpus có 692k documents, nhưng MongoDB chỉ có 3.8k sections
                # Cần map index về MongoDB sections
                # Giả sử BM25 được build từ cùng order với MongoDB
                if idx < len(self.documents_cache):
                    doc_meta = self.documents_cache[idx]
                    
                    law_name = doc_meta.get('law_name', 'Unknown Document')
                    section_title = doc_meta.get('section_title', '')
                    section_content = doc_meta.get('section_content', '')
                    category = doc_meta.get('category', '')
                    doc_id = doc_meta.get('doc_id')
                    
                    # Filter by category if specified
                    if filter_category and category != filter_category:
                        continue
                    
                    results.append({
                        'law_name': law_name,
                        'section_title': section_title,
                        'content': section_content[:500] + '...' if len(section_content) > 500 else section_content,
                        'score': score,
                        'rank': len(results) + 1,
                        'category': category,
                        'doc_id': doc_id,
                        'bm25_index': int(idx)
                    })
                
                # Stop when we have enough results
                if len(results) >= top_k:
                    break
            
            search_time_ms = (time.time() - start_time) * 1000
            
            print(f"✅ BM25: Found {len(results)} results in {search_time_ms:.2f}ms")
            
            return {
                'success': True,
                'results': results,
                'total_results': len(results),
                'search_time_ms': search_time_ms,
                'query': query,
                'top_k': top_k
            }
            
        except Exception as e:
            print(f"❌ BM25 search error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'total_results': 0,
                'search_time_ms': 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get BM25 index statistics"""
        if not self.is_loaded():
            return {
                'loaded': False,
                'error': 'BM25 not loaded'
            }
        
        return {
            'loaded': True,
            'corpus_size': getattr(self.bm25, 'corpus_size', 0),
            'average_doc_length': getattr(self.bm25, 'avgdl', 0),
            'k1': getattr(self.bm25, 'k1', 1.2),
            'b': getattr(self.bm25, 'b', 0.75),
            'delta': getattr(self.bm25, 'delta', 0),
            'file_size_mb': self.corpus_file.stat().st_size / (1024**2) if self.corpus_file.exists() else 0,
            'metadata_count': len(self.corpus_metadata) if self.corpus_metadata else 0
        }


# Singleton instance (lazy loading)
_bm25_searcher = None

def get_bm25_searcher() -> BM25LegalSearch:
    """Get singleton BM25 searcher instance"""
    global _bm25_searcher
    
    if _bm25_searcher is None:
        # Load from root directory (where bm25_legal_corpus file is located)
        corpus_path = Path(__file__).parent.parent / 'bm25_legal_corpus'
        _bm25_searcher = BM25LegalSearch(corpus_file=str(corpus_path))
    
    return _bm25_searcher


# Test script
if __name__ == '__main__':
    print("=" * 60)
    print("BM25 Legal Search - Test Script")
    print("=" * 60)
    
    # Initialize
    searcher = get_bm25_searcher()
    
    if not searcher.is_loaded():
        print("\n❌ BM25 corpus chưa được load!")
        print("💡 Kiểm tra file bm25_legal_corpus có tồn tại không")
        exit(1)
    
    # Print stats
    stats = searcher.get_stats()
    print("\n📊 BM25 Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test queries
    test_queries = [
        "Hợp đồng lao động có thời hạn",
        "Quyền và nghĩa vụ của người lao động",
        "Điều kiện thành lập doanh nghiệp",
        "Thuế thu nhập cá nhân"
    ]
    
    print("\n" + "=" * 60)
    print("Test Queries")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 60)
        
        result = searcher.search(query, top_k=3)
        
        if result['success']:
            print(f"✅ Found {result['total_results']} results in {result['search_time_ms']:.2f}ms")
            
            for i, res in enumerate(result['results'], 1):
                print(f"\n{i}. {res['law_name']}")
                print(f"   Score: {res['score']:.4f}")
                print(f"   Section: {res['section_title']}")
                print(f"   Preview: {res['content'][:100]}...")
        else:
            print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ BM25 Test completed!")
    print("=" * 60)
