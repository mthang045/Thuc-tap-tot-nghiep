"""
PageIndex Ingest Script
Build document tree index from legal documents.
Replaces vector-based ingestion with tree-based indexing.
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.page_index_integration import PageIndexManager
from dotenv import load_dotenv

load_dotenv()


def main():
    """Main ingestion function"""
    print("=" * 70)
    print("🌲 PAGEINDEX INGESTION - Tree-Based Document Indexing")
    print("=" * 70)
    print()
    print("📌 What is PageIndex?")
    print("   - Vectorless RAG framework (no embedding needed)")
    print("   - Builds table-of-contents tree structure")
    print("   - Uses LLM reasoning for retrieval (not cosine similarity)")
    print("   - 98.7% accuracy on complex documents")
    print("   - Transparent and explainable search process")
    print()
    print("=" * 70)
    print()
    
    # Configuration
    data_folder = "data/source_laws"
    cache_file = "data/page_index_cache.pkl"
    
    # Check if data folder exists
    if not os.path.exists(data_folder):
        print(f"❌ Error: Data folder '{data_folder}' not found!")
        print(f"   Please create it and add legal documents (.txt or .pdf)")
        return
    
    # Count files
    data_path = Path(data_folder)
    txt_files = list(data_path.rglob("*.txt"))
    pdf_files = list(data_path.rglob("*.pdf"))
    total_files = len(txt_files) + len(pdf_files)
    
    print(f"📂 Data folder: {data_folder}")
    print(f"📄 Found {total_files} documents:")
    print(f"   - {len(txt_files)} text files (.txt)")
    print(f"   - {len(pdf_files)} PDF files (.pdf)")
    print()
    
    if total_files == 0:
        print("⚠️  No documents found! Please add .txt or .pdf files to data folder.")
        return
    
    # Ask user for confirmation
    print("🔨 Ready to build PageIndex...")
    response = input("   Continue? (y/n): ").strip().lower()
    
    if response != 'y':
        print("❌ Cancelled by user.")
        return
    
    print()
    print("=" * 70)
    print("🚀 Starting PageIndex build process...")
    print("=" * 70)
    print()
    
    try:
        # Create PageIndex manager
        manager = PageIndexManager(
            data_folder=data_folder,
            cache_file=cache_file
        )
        
        # Force rebuild index
        print("🔄 Building document trees from files...")
        print("   This may take a few minutes depending on document count...")
        print()
        
        retriever = manager.build_index(force_rebuild=True)
        
        print()
        print("=" * 70)
        print("✅ PageIndex build completed successfully!")
        print("=" * 70)
        print()
        
        # Show statistics
        tree_count = len(retriever.document_trees)
        print(f"📊 Statistics:")
        print(f"   - Total document trees: {tree_count}")
        print(f"   - Cache file: {cache_file}")
        print()
        
        # Show tree structure examples
        print("🌲 Sample document tree structures:")
        print()
        
        for i, (source_name, root) in enumerate(list(retriever.document_trees.items())[:3]):
            print(f"{i+1}. {source_name}")
            print(f"   - Root node: {root.title}")
            print(f"   - Articles: {len(root.children)}")
            
            if root.children:
                # Show first 3 articles
                for j, article in enumerate(root.children[:3]):
                    print(f"     └─ {article.title} ({len(article.children)} clauses)")
            print()
        
        if tree_count > 3:
            print(f"   ... and {tree_count - 3} more documents")
            print()
        
        # Test query
        print("=" * 70)
        print("🧪 Testing PageIndex with sample query...")
        print("=" * 70)
        print()
        
        test_query = "Điều khoản về thời gian làm việc và nghỉ phép"
        print(f"🔍 Query: {test_query}")
        print()
        
        results = manager.query(test_query, k=3)
        
        print(f"📊 Retrieved {len(results)} results:")
        print()
        
        for i, doc in enumerate(results, 1):
            metadata = doc.get('metadata', {})
            path = metadata.get('path', 'N/A')
            title = metadata.get('title', 'Untitled')
            content_preview = doc.get('content', '')[:150]
            
            print(f"{i}. {title}")
            print(f"   Path: {path}")
            print(f"   Preview: {content_preview}...")
            print()
        
        # Show search trace for transparency
        trace = manager.get_search_trace()
        if trace:
            print("🔬 Search Trace (Transparency):")
            print("   PageIndex reasoning process:")
            for step in trace[:5]:  # Show first 5 steps
                print(f"   - Depth {step['depth']}: {step['node']}")
                print(f"     Reasoning: {step['reasoning']}")
            print()
        
        print("=" * 70)
        print("✅ ALL DONE!")
        print("=" * 70)
        print()
        print("📝 Next steps:")
        print("   1. Your application will automatically use PageIndex")
        print("   2. No changes needed to your workflow code")
        print("   3. PageIndex provides transparent, reasoning-based retrieval")
        print()
        print("🎯 Benefits over vector search:")
        print("   ✅ No arbitrary chunking - respects document structure")
        print("   ✅ Transparent reasoning - see why documents were selected")
        print("   ✅ Human-like navigation - follows document hierarchy")
        print("   ✅ Better accuracy on complex legal documents")
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR OCCURRED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("  - Missing GROQ_API_KEY in .env file")
        print("  - Invalid PDF files (try converting to .txt)")
        print("  - Insufficient memory for large document sets")
        print()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
