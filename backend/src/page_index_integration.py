"""
PageIndex Integration Module
Provides easy integration with existing workflow
"""
import os
import pickle
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from src.page_index import (
    PageIndexRetriever, 
    DocumentTreeBuilder,
    DocumentNode,
    build_page_index_from_directory
)

load_dotenv()


class PageIndexManager:
    """
    Manages PageIndex retriever with caching and lazy loading.
    Drop-in replacement for vector-based retriever.
    """
    
    def __init__(self, data_folder: str = "data/source_laws", cache_file: str = "data/page_index_cache.pkl"):
        self.data_folder = data_folder
        self.cache_file = cache_file
        self._retriever: Optional[PageIndexRetriever] = None
        self._llm = None
    
    def _get_llm(self):
        """Get LLM client for tree search reasoning"""
        if self._llm is None:
            from langchain_groq import ChatGroq
            
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self._llm = ChatGroq(
                api_key=api_key,
                model="llama-3.1-8b-instant",
                temperature=0,
                max_retries=2
            )
        
        return self._llm
    
    def build_index(self, force_rebuild: bool = False) -> PageIndexRetriever:
        """
        Build or load PageIndex from cache.
        
        Args:
            force_rebuild: If True, rebuild even if cache exists
            
        Returns:
            PageIndexRetriever instance
        """
        # Try loading from cache
        if not force_rebuild and os.path.exists(self.cache_file):
            print("📂 Loading PageIndex from cache...")
            try:
                with open(self.cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                llm = self._get_llm()
                self._retriever = PageIndexRetriever(llm, cached_data['document_trees'])
                
                print(f"✅ Loaded {len(cached_data['document_trees'])} document trees from cache")
                return self._retriever
            
            except Exception as e:
                print(f"⚠️ Cache load failed: {e}. Rebuilding...")
        
        # Build new index
        print("🔨 Building PageIndex from documents...")
        llm = self._get_llm()
        
        self._retriever = build_page_index_from_directory(self.data_folder, llm)
        
        # Save to cache
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                pickle.dump({
                    'document_trees': self._retriever.document_trees,
                    'version': '1.0'
                }, f)
            print(f"💾 Saved PageIndex cache to {self.cache_file}")
        except Exception as e:
            print(f"⚠️ Cache save failed: {e}")
        
        return self._retriever
    
    def get_retriever(self) -> PageIndexRetriever:
        """
        Get retriever instance (lazy loading).
        """
        if self._retriever is None:
            self.build_index()
        
        return self._retriever
    
    def query(self, query_text: str, k: int = 5) -> list:
        """
        Query the PageIndex retriever.
        
        Args:
            query_text: Query string
            k: Number of results
            
        Returns:
            List of relevant documents
        """
        retriever = self.get_retriever()
        results = retriever.invoke(query_text, k=k)
        
        return results
    
    def get_search_trace(self) -> list:
        """
        Get transparent search trace showing reasoning process.
        """
        if self._retriever:
            return self._retriever.get_search_trace()
        return []
    
    def rebuild_index(self):
        """Force rebuild the index"""
        print("🔄 Force rebuilding PageIndex...")
        return self.build_index(force_rebuild=True)


# Global singleton instance
_page_index_manager: Optional[PageIndexManager] = None


def get_page_index_manager() -> PageIndexManager:
    """Get global PageIndex manager instance"""
    global _page_index_manager
    
    if _page_index_manager is None:
        _page_index_manager = PageIndexManager()
    
    return _page_index_manager


def get_page_index_retriever() -> PageIndexRetriever:
    """
    Get PageIndex retriever (convenience function).
    Drop-in replacement for get_retriever() in workflow.
    """
    manager = get_page_index_manager()
    return manager.get_retriever()


# Example usage functions
def example_query():
    """Example: Query PageIndex"""
    manager = get_page_index_manager()
    
    # Query
    query = "Điều khoản về thanh toán trong hợp đồng mua bán"
    results = manager.query(query, k=3)
    
    print(f"\n🔍 Query: {query}")
    print(f"📊 Found {len(results)} results\n")
    
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['metadata'].get('title', 'Untitled')}")
        print(f"   Path: {doc['metadata'].get('path', 'N/A')}")
        print(f"   Content: {doc['content'][:150]}...")
        print()
    
    # Show search trace
    trace = manager.get_search_trace()
    print("\n🔬 Search Trace (Transparency):")
    for step in trace:
        print(f"  Depth {step['depth']}: {step['node']}")
        print(f"    Path: {step['path']}")
        print(f"    Reasoning: {step['reasoning']}")


def example_build_index():
    """Example: Build index from scratch"""
    manager = get_page_index_manager()
    manager.rebuild_index()
    print("✅ Index built successfully!")


if __name__ == "__main__":
    # Run examples
    print("=" * 60)
    print("PageIndex Integration Example")
    print("=" * 60)
    
    # Build index
    example_build_index()
    
    # Query
    example_query()
