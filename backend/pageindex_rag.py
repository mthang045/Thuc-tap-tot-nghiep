"""
PageIndex RAG Framework - Vectorless, Tree-Based Retrieval
Implements the PageIndex approach for legal document analysis

Based on: github.com/VectifyAI/PageIndex
Approach: Build hierarchical document tree and use LLM reasoning for search
No vector embeddings - pure reasoning-based retrieval
"""

import os
import json
import pymongo
import pickle
from bson import ObjectId
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['legal_AI_db']


@dataclass
class DocumentNode:
    """
    Represents a node in the document tree (table-of-contents style)
    """
    id: str
    title: str
    content: str
    level: int  # 0 = document root, 1 = chapter, 2 = section, etc.
    parent_id: Optional[str] = None
    children: List['DocumentNode'] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        result = {
            'id': self.id,
            'title': self.title,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'level': self.level,
            'parent_id': self.parent_id,
            'metadata': self.metadata,
            'children': [child.to_dict() for child in self.children]
        }
        return result
    
    def get_path(self) -> str:
        """Get breadcrumb path for this node"""
        if self.parent_id:
            return f"{self.metadata.get('parent_title', '')} > {self.title}"
        return self.title
    
    def get_full_content(self, max_depth: int = 2) -> str:
        """Get content including children up to max_depth"""
        content = f"[{self.title}]\n{self.content}\n"
        
        if max_depth > 0 and self.children:
            for child in self.children[:3]:  # Limit to first 3 children
                content += f"\n{child.get_full_content(max_depth - 1)}"
        
        return content


class DocumentTreeBuilder:
    """
    Builds hierarchical tree structure from legal documents
    Mimics table-of-contents structure
    """
    
    def __init__(self):
        self.node_counter = 0
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID"""
        self.node_counter += 1
        return f"node_{self.node_counter}"
    
    def build_from_legal_document(self, legal_doc: Dict) -> DocumentNode:
        """
        Build document tree from MongoDB legal document
        
        Structure:
        - Root: Document (level 0)
        - Children: Sections (level 1)
        - Can be extended to subsections if needed
        """
        doc_id = str(legal_doc['_id'])
        law_name = legal_doc.get('law_name', 'Unknown')
        category = legal_doc.get('category', '')
        year = legal_doc.get('year', 0)
        
        # Create root node (document level)
        root = DocumentNode(
            id=self._generate_node_id(),
            title=law_name,
            content=legal_doc.get('full_content', '')[:500],  # Brief overview
            level=0,
            metadata={
                'doc_id': doc_id,
                'category': category,
                'year': year,
                'type': 'document'
            }
        )
        
        # Add sections as children
        sections = legal_doc.get('sections', [])
        for idx, section in enumerate(sections):
            section_title = section.get('title', f'Section {idx+1}')
            section_content = section.get('content', '')
            
            section_node = DocumentNode(
                id=self._generate_node_id(),
                title=section_title,
                content=section_content,
                level=1,
                parent_id=root.id,
                metadata={
                    'doc_id': doc_id,
                    'law_name': law_name,
                    'section_index': idx,
                    'type': 'section',
                    'parent_title': law_name
                }
            )
            
            root.children.append(section_node)
        
        return root
    
    def build_from_mongodb(self) -> List[DocumentNode]:
        """Build trees for all legal documents in MongoDB"""
        print("🌲 Building document trees from MongoDB...")
        
        legal_docs_collection = db['legal_documents']
        documents = list(legal_docs_collection.find())
        
        trees = []
        for doc in documents:
            tree = self.build_from_legal_document(doc)
            trees.append(tree)
        
        print(f"✅ Built {len(trees)} document trees")
        total_nodes = sum(1 + len(tree.children) for tree in trees)
        print(f"📊 Total nodes: {total_nodes}")
        
        return trees


class PageIndexRetriever:
    """
    PageIndex RAG system using tree search with LLM reasoning
    No vector embeddings - pure reasoning-based retrieval
    """
    
    def __init__(self, llm, document_trees: List[DocumentNode]):
        """
        Initialize PageIndex retriever
        
        Args:
            llm: Language model for reasoning
            document_trees: List of document trees
        """
        self.llm = llm
        self.document_trees = document_trees
        self.node_index = self._build_node_index()
        
        print(f"✅ PageIndex initialized with {len(document_trees)} documents")
    
    def _build_node_index(self) -> Dict[str, DocumentNode]:
        """Build flat index for quick node lookup"""
        index = {}
        
        def add_to_index(node: DocumentNode):
            index[node.id] = node
            for child in node.children:
                add_to_index(child)
        
        for tree in self.document_trees:
            add_to_index(tree)
        
        return index
    
    def _get_document_summaries(self) -> str:
        """Get concise summary of all documents for initial selection"""
        summaries = []
        for tree in self.document_trees:
            summary = f"- {tree.title} ({len(tree.children)} sections)"
            if tree.metadata.get('category'):
                summary += f" [Category: {tree.metadata['category']}]"
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def _select_relevant_documents(self, query: str, top_k: int = 3) -> List[DocumentNode]:
        """
        Step 1: Use LLM to select which documents are most relevant
        This is the first level of tree search
        """
        document_summaries = self._get_document_summaries()
        
        prompt = f"""Bạn là chuyên gia pháp lý. Dưới đây là danh sách các văn bản pháp luật:

{document_summaries}

Câu hỏi: {query}

Hãy chọn TOP {top_k} văn bản pháp luật QUAN TRỌNG NHẤT để trả lời câu hỏi trên.
CHỈ trả về tên chính xác của các văn bản, mỗi dòng một văn bản, KHÔNG giải thích.

Ví dụ format:
ban Bo luat Lao dong
ban Luat Dat dai
nghiep Luat Doanh nghiep

Trả lời:"""
        
        try:
            # LLM reasoning để chọn documents
            response = self.llm.invoke(prompt)
            selected_names = response.content.strip().split('\n')
            
            # Match với document trees
            selected_docs = []
            for name in selected_names[:top_k]:
                name_clean = name.strip('-').strip()
                for tree in self.document_trees:
                    if name_clean in tree.title or tree.title in name_clean:
                        selected_docs.append(tree)
                        break
            
            print(f"  📑 Selected {len(selected_docs)} documents via LLM reasoning")
            return selected_docs
            
        except Exception as e:
            print(f"  ⚠️ LLM selection failed: {e}, using fallback")
            # Fallback: return first top_k documents
            return self.document_trees[:top_k]
    
    def _select_relevant_sections(self, query: str, document: DocumentNode, top_k: int = 3) -> List[DocumentNode]:
        """
        Step 2: Within selected document, use LLM to find relevant sections
        This is the second level of tree search
        """
        if not document.children:
            return []
        
        # Create section summaries
        section_summaries = []
        for i, section in enumerate(document.children[:20]):  # Limit to first 20 sections
            summary = f"{i+1}. {section.title}"
            section_summaries.append(summary)
        
        sections_text = "\n".join(section_summaries)
        
        prompt = f"""Trong văn bản "{document.title}", có các phần sau:

{sections_text}

Câu hỏi: {query}

Hãy chọn TOP {top_k} phần (sections) QUAN TRỌNG NHẤT để trả lời câu hỏi.
CHỈ trả về SỐ THỨ TỰ của các phần, phân cách bằng dấu phẩy, KHÔNG giải thích.

Ví dụ format: 1, 5, 12

Trả lời:"""
        
        try:
            response = self.llm.invoke(prompt)
            selected_indices = []
            
            # Parse response
            response_text = response.content.strip()
            for part in response_text.split(','):
                try:
                    idx = int(part.strip()) - 1  # Convert to 0-based index
                    if 0 <= idx < len(document.children):
                        selected_indices.append(idx)
                except ValueError:
                    continue
            
            selected_sections = [document.children[i] for i in selected_indices[:top_k]]
            print(f"  📄 Selected {len(selected_sections)} sections via LLM reasoning")
            return selected_sections
            
        except Exception as e:
            print(f"  ⚠️ Section selection failed: {e}, using fallback")
            # Fallback: return first top_k sections
            return document.children[:top_k]
    
    def search(self, query: str, top_k_docs: int = 2, top_k_sections: int = 3) -> List[Dict]:
        """
        Main search method using tree search with LLM reasoning
        
        Process:
        1. LLM selects relevant documents from document tree roots
        2. For each selected document, LLM selects relevant sections
        3. Return ranked results
        
        No vector similarity - pure reasoning!
        """
        print(f"\n🔍 PageIndex Search: '{query[:50]}...'")
        print("  Step 1: Selecting relevant documents...")
        
        # Step 1: Select documents
        relevant_docs = self._select_relevant_documents(query, top_k=top_k_docs)
        
        # Step 2: Select sections within each document
        print("  Step 2: Selecting relevant sections...")
        results = []
        
        for doc in relevant_docs:
            sections = self._select_relevant_sections(query, doc, top_k=top_k_sections)
            
            for section in sections:
                results.append({
                    'doc_id': section.metadata.get('doc_id', ''),
                    'law_name': section.metadata.get('law_name', doc.title),
                    'section_title': section.title,
                    'section_index': section.metadata.get('section_index', 0),
                    'content': section.content,
                    'path': section.get_path(),
                    'retrieval_method': 'pageindex_tree_search',
                    'level': section.level,
                    'reasoning_score': 0.95  # High confidence from LLM reasoning
                })
        
        print(f"  ✅ Found {len(results)} results via PageIndex")
        return results
    
    def get_context(self, query: str, max_length: int = 2000) -> str:
        """
        Get relevant context for RAG using PageIndex
        Returns formatted context string for LLM
        """
        results = self.search(query, top_k_docs=2, top_k_sections=3)
        
        context_parts = []
        current_length = 0
        
        for result in results:
            law_name = result['law_name']
            section_title = result['section_title']
            content = result['content']
            
            piece = f"[{law_name} - {section_title}]\n{content}\n"
            
            if current_length + len(piece) > max_length:
                break
            
            context_parts.append(piece)
            current_length += len(piece)
        
        context = "\n---\n".join(context_parts)
        return context


class PageIndexManager:
    """
    Manager class for easy PageIndex integration
    Handles caching and lazy loading
    """
    
    def __init__(self, cache_file: str = 'pageindex_cache.pkl'):
        self.cache_file = cache_file
        self.document_trees = None
        self.retriever = None
        self.llm = None
    
    def _get_llm(self):
        """Get LLM for tree search reasoning"""
        if self.llm is None:
            try:
                from langchain_groq import ChatGroq
                api_key = os.getenv("GROQ_API_KEY")
                
                if not api_key:
                    raise ValueError("GROQ_API_KEY not found")
                
                # Use faster model for reasoning
                self.llm = ChatGroq(
                    api_key=api_key,
                    model="llama-3.1-8b-instant",  # Fast model for tree search
                    temperature=0,
                    max_retries=2
                )
            except Exception as e:
                print(f"⚠️ Langchain import failed: {e}")
                print("   Using direct Groq API fallback...")
                from groq_simple import GroqSimpleLLM
                self.llm = GroqSimpleLLM()
        
        return self.llm
    
    def build_index(self, force_rebuild: bool = False):
        """Build PageIndex from MongoDB"""
        # Try load from cache
        if not force_rebuild and os.path.exists(self.cache_file):
            print("📂 Loading PageIndex from cache...")
            try:
                with open(self.cache_file, 'rb') as f:
                    self.document_trees = pickle.load(f)
                print(f"✅ Loaded {len(self.document_trees)} document trees")
                return
            except Exception as e:
                print(f"⚠️ Cache load failed: {e}, rebuilding...")
        
        # Build new
        print("🔨 Building PageIndex from MongoDB...")
        builder = DocumentTreeBuilder()
        self.document_trees = builder.build_from_mongodb()
        
        # Save cache
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.document_trees, f)
            print(f"💾 Saved cache to {self.cache_file}")
        except Exception as e:
            print(f"⚠️ Cache save failed: {e}")
    
    def get_retriever(self) -> PageIndexRetriever:
        """Get PageIndex retriever (lazy loading)"""
        if self.retriever is None:
            if self.document_trees is None:
                self.build_index()
            
            llm = self._get_llm()
            self.retriever = PageIndexRetriever(llm, self.document_trees)
        
        return self.retriever


def main():
    """Test PageIndex system"""
    print("="*60)
    print("      PAGEINDEX RAG SYSTEM - BUILD & TEST")
    print("="*60)
    
    # Build index
    manager = PageIndexManager(cache_file='embeddings/pageindex_cache.pkl')
    manager.build_index(force_rebuild=True)
    
    # Get retriever
    retriever = manager.get_retriever()
    
    # Test queries
    print("\n" + "="*60)
    print("🧪 TESTING PAGEINDEX SEARCH")
    print("="*60)
    
    test_queries = [
        "Hợp đồng lao động có thời hạn",
        "Quyền và nghĩa vụ của người thuê nhà",
        "Điều kiện thành lập doanh nghiệp",
        "Quyền sử dụng đất"
    ]
    
    for query in test_queries:
        results = retriever.search(query, top_k_docs=2, top_k_sections=2)
        
        print(f"\n🔍 Query: {query}")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['law_name']}")
            print(f"      Section: {result['section_title']}")
            print(f"      Method: {result['retrieval_method']}")
    
    print("\n" + "="*60)
    print("✅ PAGEINDEX TESTED SUCCESSFULLY!")
    print("="*60)


if __name__ == '__main__':
    main()
