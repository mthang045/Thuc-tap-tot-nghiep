# Quick test import
import sys
print("Python version:", sys.version)

try:
    import rank_bm25
    print("✅ rank_bm25 imported OK")
except ImportError as e:
    print(f"❌ Cannot import rank_bm25: {e}")
    sys.exit(1)

try:
    from bm25_search import BM25LegalSearch
    print("✅ BM25LegalSearch imported OK")
except Exception as e:
    print(f"❌ Cannot import BM25LegalSearch: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports successful!")
