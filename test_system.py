"""
Simple test script - kiểm tra các thành phần cơ bản
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("🧪 TESTING LEGAL CONTRACT SYSTEM")
print("=" * 60)
print()

# Test 1: MongoDB connection
print("1. Testing MongoDB connection...")
try:
    import pymongo
    client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
    client.server_info()
    db = client['legal_db']
    collections = db.list_collection_names()
    print(f"   ✅ MongoDB connected!")
    print(f"   📂 Collections: {len(collections)}")
    client.close()
except Exception as e:
    print(f"   ❌ MongoDB error: {e}")

# Test 2: PageIndex cache
print("\n2. Checking PageIndex cache...")
try:
    cache_file = "backend/data/page_index_cache.pkl"
    if os.path.exists(cache_file):
        import pickle
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)
        print(f"   ✅ PageIndex cache found!")
        print(f"   📊 Documents indexed: {len(cache)}")
    else:
        print(f"   ⚠️  Cache not found. Run: python backend/ingest_pageindex.py")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: SVM Models
print("\n3. Checking SVM models...")
try:
    model_dir = "backend/models/svm"
    if os.path.exists(model_dir):
        models = os.listdir(model_dir)
        print(f"   ✅ SVM model directory found!")
        print(f"   📦 Model files: {len(models)}")
        for m in models:
            print(f"      - {m}")
    else:
        print(f"   ⚠️  Models not found. Run: python backend/train_svm.py")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Environment variables
print("\n4. Checking environment...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    groq_key = os.getenv('GROQ_API_KEY', '')
    mongo_uri = os.getenv('MONGODB_URI', 'not set')
    print(f"   ✅ .env loaded!")
    print(f"   🔑 GROQ_API_KEY: {'Set ✅' if groq_key else 'Missing ❌'}")
    print(f"   🗄️  MONGODB_URI: {mongo_uri[:50]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 60)
print("✅ SYSTEM CHECK COMPLETED!")
print("=" * 60)
print()
print("🚀 To run the application:")
print("   cd backend")
print("   python app.py")
print()
