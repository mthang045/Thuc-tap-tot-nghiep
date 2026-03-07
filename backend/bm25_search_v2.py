"""
BM25 In-Memory Search for Legal Documents (MongoDB-based)
Builds BM25 index directly from MongoDB instead of pre-built file

This approach is faster and more reliable than the 855MB pre-built corpus
which was built from a different dataset.

Author: THĂNG BÙI MINH
Date: March 2026
"""

import time
from typing import List, Dict, Any, Optional
import pymongo
from rank_bm25 import BM25Okapi

# MongoDB connection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['legal_AI_db']


class BM25LegalSearchInMemory:
    """
    BM25 search built directly from MongoDB legal documents
    Fast, lightweight, and always in-sync with database
    """
    
    def __init__(self):
        """Initialize and build BM25 index from MongoDB"""
        self.bm25 = None
        self.documents = []
        self.tokenized_corpus = []
        self._build_index()
    
    def _vietnamese_tokenize(self, text: str) -> List[str]:
        """
        Simple Vietnamese tokenizer
        For production: use pyvi or underthesea for proper word segmentation
        """
        # Convert to lowercase and split by whitespace
        # Remove punctuation
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 1]  # Filter single chars
    
    def _build_index(self):
        """Build BM25 index from MongoDB legal documents"""
        try:
            print("🔨 Building BM25 index từ MongoDB...")
            start_time = time.time()
            
            legal_docs_collection = db['legal_documents']
            docs = list(legal_docs_collection.find())
            
            print(f"   Found {len(docs)} legal documents")
            
            # Extract all sections as searchable documents
            for doc in docs:
                law_name = doc.get('law_name', 'Unknown')
                category = doc.get('category_code', '')
                sections = doc.get('sections', [])
                
                for idx, section in enumerate(sections):
                    section_title = section.get('title', f'Phần {idx+1}')
                    section_content = section.get('content', '')
                    
                    # Combine title + content for better search
                    full_text = f"{section_title} {section_content}"
                    
                    # Tokenize
                    tokens = self._vietnamese_tokenize(full_text)
                    
                    # Store document metadata
                    self.documents.append({
                        'doc_id': str(doc['_id']),
                        'law_name': law_name,
                        'category': category,
                        'section_title': section_title,
                        'section_content': section_content,
                        'full_text': full_text
                    })
                    
                    # Store tokenized version for BM25
                    self.tokenized_corpus.append(tokens)
            
            # Build BM25 index
            if self.tokenized_corpus:
                self.bm25 = BM25Okapi(self.tokenized_corpus)
                build_time = time.time() - start_time
                
                print(f"✅ BM25 index built trong {build_time:.2f}s")
                print(f"   Total sections indexed: {len(self.documents)}")
                print(f"   Average tokens per section: {sum(len(t) for t in self.tokenized_corpus) / len(self.tokenized_corpus):.2f}")
            else:
                print("⚠️ Không có documents để index!")
            
        except Exception as e:
            print(f"❌ Lỗi khi build BM25 index: {e}")
            import traceback
            traceback.print_exc()
    
    def is_loaded(self) -> bool:
        """Check if BM25 index đã được build thành công"""
        return self.bm25 is not None and len(self.documents) > 0
    
    def search(self, query: str, top_k: int = 5, filter_category: Optional[str] = None) -> Dict[str, Any]:
        """
        Search legal documents using BM25
        
        Args:
            query: Query string
            top_k: Number of results
            filter_category: Optional category filter
            
        Returns:
            Search results with scores
        """
        if not self.is_loaded():
            return {
                'success': False,
                'error': 'BM25 index chưa được build',
                'results': [],
                'total_results': 0,
                'search_time_ms': 0
            }
        
        try:
            start_time = time.time()
            
            # Tokenize query
            query_tokens = self._vietnamese_tokenize(query)
            
            print(f"🔍 BM25 Search: '{query[:50]}...'")
            print(f"   Query tokens: {query_tokens[:10]}...")  # Show first 10 tokens
            
            # Get BM25 scores
            scores = self.bm25.get_scores(query_tokens)
            
            # Get top indices
            import numpy as np
            top_indices = np.argsort(scores)[-top_k * 2:][::-1]  # Get more, filter later
            
            # Build results
            results = []
            for idx in top_indices:
                if idx >= len(self.documents):
                    continue
                
                score = float(scores[idx])
                
                # Skip very low scores
                if score < 0.1:
                    continue
                
                doc = self.documents[idx]
                
                # Filter by category if specified
                if filter_category and doc['category'] != filter_category:
                    continue
                
                results.append({
                    'law_name': doc['law_name'],
                    'section_title': doc['section_title'],
                    'content': doc['section_content'][:500] + '...' if len(doc['section_content']) > 500 else doc['section_content'],
                    'score': score,
                    'rank': len(results) + 1,
                    'category': doc['category'],
                    'doc_id': doc['doc_id']
                })
                
                # Stop when we have enough
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
        
        total_tokens = sum(len(tokens) for tokens in self.tokenized_corpus)
        
        return {
            'loaded': True,
            'total_documents': len(self.documents),
            'total_tokens': total_tokens,
            'avg_tokens_per_doc': total_tokens / len(self.documents) if self.documents else 0,
            'index_type': 'BM25Okapi',
            'source': 'MongoDB in-memory'
        }


# Singleton instance
_bm25_searcher = None

def get_bm25_searcher() -> BM25LegalSearchInMemory:
    """Get singleton BM25 searcher (builds index on first call)"""
    global _bm25_searcher
    
    if _bm25_searcher is None:
        _bm25_searcher = BM25LegalSearchInMemory()
    
    return _bm25_searcher


# Test script
if __name__ == '__main__':
    print("=" * 60)
    print("BM25 Legal Search (In-Memory) - Test Script")
    print("=" * 60)
    
    # Initialize
    searcher = get_bm25_searcher()
    
    if not searcher.is_loaded():
        print("\n❌ BM25 index không thể build!")
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
