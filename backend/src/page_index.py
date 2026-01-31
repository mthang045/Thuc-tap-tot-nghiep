"""
PageIndex: Vectorless RAG Framework
Mimics human expert document navigation using tree-based search.

Based on VectifyAI's PageIndex approach - achieving 98.7% accuracy without vector embeddings.
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the document tree"""
    ROOT = "root"
    CATEGORY = "category"           # e.g., "Bộ luật dân sự", "Luật lao động"
    SECTION = "section"             # e.g., "Chương 1", "Phần I"
    ARTICLE = "article"             # e.g., "Điều 10"
    CLAUSE = "clause"               # e.g., "Khoản 1", "Điểm a"
    PARAGRAPH = "paragraph"         # Raw text paragraph
    

@dataclass
class DocumentNode:
    """
    Represents a node in the document tree hierarchy.
    Similar to a table-of-contents entry.
    """
    id: str
    type: NodeType
    title: str                      # e.g., "Điều 10. Quyền và nghĩa vụ của bên thuê"
    content: str                    # Full text content
    summary: Optional[str] = None   # LLM-generated summary for navigation
    metadata: Dict = field(default_factory=dict)
    children: List['DocumentNode'] = field(default_factory=list)
    parent: Optional['DocumentNode'] = None
    
    def add_child(self, child: 'DocumentNode'):
        """Add a child node"""
        child.parent = self
        self.children.append(child)
    
    def get_path(self) -> str:
        """Get the hierarchical path from root to this node"""
        path = []
        node = self
        while node:
            if node.type != NodeType.ROOT:
                path.append(node.title)
            node = node.parent
        return " > ".join(reversed(path))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'type': self.type.value,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'metadata': self.metadata,
            'path': self.get_path(),
            'children_count': len(self.children)
        }


class DocumentTreeBuilder:
    """
    Builds a hierarchical tree structure from legal documents.
    Respects natural document structure instead of arbitrary chunking.
    """
    
    def __init__(self):
        self.node_counter = 0
    
    def _get_next_id(self) -> str:
        """Generate unique node ID"""
        self.node_counter += 1
        return f"node_{self.node_counter}"
    
    def build_from_legal_document(self, text: str, source_name: str, category: str = "") -> DocumentNode:
        """
        Build document tree from Vietnamese legal document.
        
        Structure:
        - Root (source_name)
          - Articles (Điều X)
            - Clauses (Khoản X)
              - Points (Điểm X)
        """
        root = DocumentNode(
            id=self._get_next_id(),
            type=NodeType.ROOT,
            title=source_name,
            content=text,
            metadata={
                'source': source_name,
                'category': category
            }
        )
        
        # Parse articles (Điều X)
        articles = self._extract_articles(text)
        
        for article_data in articles:
            article_node = DocumentNode(
                id=self._get_next_id(),
                type=NodeType.ARTICLE,
                title=article_data['title'],
                content=article_data['content'],
                metadata={
                    'article_number': article_data['number'],
                    'source': source_name
                }
            )
            root.add_child(article_node)
            
            # Parse clauses within article (Khoản X)
            clauses = self._extract_clauses(article_data['content'])
            for clause_data in clauses:
                clause_node = DocumentNode(
                    id=self._get_next_id(),
                    type=NodeType.CLAUSE,
                    title=clause_data['title'],
                    content=clause_data['content'],
                    metadata={
                        'clause_number': clause_data['number'],
                        'article_number': article_data['number']
                    }
                )
                article_node.add_child(clause_node)
        
        return root
    
    def _extract_articles(self, text: str) -> List[Dict]:
        """Extract articles (Điều X) from legal text"""
        # Pattern: "Điều <number>." followed by optional title
        pattern = r'(Điều\s+(\d+)\.?\s*([^\n]*))'
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        articles = []
        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            article_title = match.group(1).strip()
            article_number = match.group(2)
            article_content = text[start_pos:end_pos].strip()
            
            articles.append({
                'title': article_title,
                'number': article_number,
                'content': article_content
            })
        
        return articles
    
    def _extract_clauses(self, article_text: str) -> List[Dict]:
        """Extract clauses (Khoản X) from article text"""
        # Pattern: "Khoản <number>" or just numbered list "1.", "2."
        pattern = r'(?:^|\n)(\d+\.|Khoản\s+\d+\.?)\s*([^\n]+(?:\n(?!\d+\.|Khoản)[^\n]+)*)'
        matches = list(re.finditer(pattern, article_text, re.MULTILINE | re.IGNORECASE))
        
        clauses = []
        for match in matches:
            clause_title = match.group(1).strip()
            clause_content = match.group(0).strip()
            
            # Extract number
            num_match = re.search(r'\d+', clause_title)
            clause_number = num_match.group() if num_match else "0"
            
            clauses.append({
                'title': f"Khoản {clause_number}",
                'number': clause_number,
                'content': clause_content
            })
        
        return clauses


class TreeSearchEngine:
    """
    Implements tree search to find relevant information.
    Uses LLM reasoning instead of vector similarity.
    """
    
    def __init__(self, llm_client):
        """
        Args:
            llm_client: LLM client for reasoning (e.g., ChatGroq)
        """
        self.llm = llm_client
        self.search_trace = []  # For transparency
    
    def search(self, root: DocumentNode, query: str, max_depth: int = 3) -> List[DocumentNode]:
        """
        Search document tree using LLM-guided navigation.
        
        Args:
            root: Root node of document tree
            query: User query
            max_depth: Maximum depth to search
            
        Returns:
            List of relevant nodes
        """
        self.search_trace = []
        relevant_nodes = []
        
        # Start with root's children
        current_nodes = root.children
        depth = 0
        
        while depth < max_depth and current_nodes:
            # Ask LLM to rank children by relevance
            ranked_nodes = self._rank_nodes_by_relevance(current_nodes, query, depth)
            
            if not ranked_nodes:
                break
            
            # Take top node
            best_node = ranked_nodes[0]
            relevant_nodes.append(best_node)
            
            self.search_trace.append({
                'depth': depth,
                'node': best_node.title,
                'path': best_node.get_path(),
                'reasoning': f"Selected as most relevant at depth {depth}"
            })
            
            # Continue searching children
            if best_node.children:
                current_nodes = best_node.children
                depth += 1
            else:
                break
        
        return relevant_nodes
    
    def _rank_nodes_by_relevance(self, nodes: List[DocumentNode], query: str, depth: int) -> List[DocumentNode]:
        """
        Use LLM to rank nodes by relevance to query.
        This is the core of the "reasoning-based" retrieval.
        """
        if not nodes:
            return []
        
        # Build prompt for LLM
        node_descriptions = []
        for i, node in enumerate(nodes):
            node_descriptions.append(
                f"{i}. {node.title}\n   Preview: {node.content[:200]}..."
            )
        
        prompt = f"""You are a legal document navigation expert. Given a user query and a list of document sections, identify which section is MOST relevant to answer the query.

Query: {query}

Available sections:
{chr(10).join(node_descriptions)}

Return ONLY the number (0-{len(nodes)-1}) of the most relevant section. Think step-by-step about which section would contain the answer.

Response format: Just the number, nothing else."""

        try:
            response = self.llm.invoke(prompt)
            
            # Extract number from response
            content = response.content if hasattr(response, 'content') else str(response)
            selected_idx = int(re.search(r'\d+', content).group())
            
            if 0 <= selected_idx < len(nodes):
                # Return ranked list (best first)
                return [nodes[selected_idx]]
            
        except Exception as e:
            print(f"LLM ranking error: {e}")
        
        # Fallback: return first node
        return [nodes[0]] if nodes else []
    
    def get_trace(self) -> List[Dict]:
        """Get search trace for transparency"""
        return self.search_trace


class PageIndexRetriever:
    """
    Main retriever interface compatible with existing RAG pipeline.
    Replaces vector-based retrieval with tree-based search.
    """
    
    def __init__(self, llm_client, document_trees: Dict[str, DocumentNode]):
        """
        Args:
            llm_client: LLM for reasoning
            document_trees: Dict mapping source_name -> root DocumentNode
        """
        self.search_engine = TreeSearchEngine(llm_client)
        self.document_trees = document_trees
    
    def invoke(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents using tree search.
        
        Args:
            query: User query
            k: Number of results to return (searches up to k trees)
            
        Returns:
            List of document dictionaries with content and metadata
        """
        all_results = []
        
        # Search each document tree
        for source_name, root in list(self.document_trees.items())[:k]:
            relevant_nodes = self.search_engine.search(root, query, max_depth=3)
            
            for node in relevant_nodes:
                all_results.append({
                    'content': node.content,
                    'metadata': {
                        **node.metadata,
                        'path': node.get_path(),
                        'node_type': node.type.value,
                        'title': node.title
                    }
                })
        
        return all_results[:k]
    
    def get_search_trace(self) -> List[Dict]:
        """Get transparent search reasoning"""
        return self.search_engine.get_trace()


def build_page_index_from_directory(directory_path: str, llm_client) -> PageIndexRetriever:
    """
    Build PageIndex retriever from directory of legal documents.
    
    Args:
        directory_path: Path to directory containing legal documents
        llm_client: LLM client for reasoning
        
    Returns:
        PageIndexRetriever instance
    """
    import os
    from pathlib import Path
    
    builder = DocumentTreeBuilder()
    document_trees = {}
    
    # Process all text and PDF files
    data_path = Path(directory_path)
    
    for root_dir, _, files in os.walk(data_path):
        for filename in files:
            if not filename.endswith(('.txt', '.pdf')):
                continue
            
            file_path = os.path.join(root_dir, filename)
            
            # Determine category from folder structure
            category = Path(root_dir).name if Path(root_dir).name != data_path.name else "uncategorized"
            
            # Read file content
            if filename.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif filename.endswith('.pdf'):
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    content = "\n".join([page.extract_text() for page in reader.pages])
                except Exception as e:
                    print(f"Error reading PDF {filename}: {e}")
                    continue
            
            # Build tree
            source_name = filename
            tree = builder.build_from_legal_document(content, source_name, category)
            document_trees[source_name] = tree
            
            print(f"✅ Built tree for {source_name}: {len(tree.children)} articles")
    
    print(f"\n🌲 Total document trees: {len(document_trees)}")
    
    return PageIndexRetriever(llm_client, document_trees)
