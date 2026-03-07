# Quick API test script
import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("API Testing - BM25 + PageIndex")
print("=" * 60)

# Wait for server
print("\n⏳ Waiting for server to start...")
for i in range(10):
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running!")
            break
    except:
        time.sleep(1)
        print(f"   Retrying... {i+1}/10")
else:
    print("❌ Server not responding after 10 seconds")
    exit(1)

# Test 1: ML Status
print("\n" + "=" * 60)
print("Test 1: ML Status")
print("=" * 60)

try:
    response = requests.get(f"{BASE_URL}/api/ml-status/")
    data = response.json()
    
    if data['success']:
        print("\n✅ ML Status OK")
        print(f"\n   SVM: {'✅ Loaded' if data['status']['svm']['loaded'] else '❌ Not loaded'}")
        print(f"   BM25: {'✅ Loaded' if data['status']['bm25']['loaded'] else '❌ Not loaded'}")
        print(f"   PageIndex: {'✅ Loaded' if data['status']['pageindex']['loaded'] else '❌ Not loaded'}")
        
        if data['status']['bm25']['loaded']:
            print(f"\n   BM25 Stats:")
            print(f"     - Documents: {data['status']['bm25']['total_documents']}")
            print(f"     - Tokens: {data['status']['bm25']['total_tokens']}")
            print(f"     - Avg tokens/doc: {data['status']['bm25']['avg_tokens_per_doc']}")
    else:
        print(f"❌ Error: {data.get('error')}")
except Exception as e:
    print(f"❌ Request failed: {e}")

# Test 2: BM25 Search
print("\n" + "=" * 60)
print("Test 2: BM25 Search")
print("=" * 60)

query = "Hợp đồng lao động có thời hạn"
print(f"\n🔍 Query: '{query}'")

try:
    response = requests.post(
        f"{BASE_URL}/api/bm25-search/",
        json={"query": query, "top_k": 3},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    
    if data['success']:
        print(f"✅ Found {data['total_results']} results in {data['search_time_ms']:.2f}ms")
        
        for i, result in enumerate(data['results'], 1):
            print(f"\n{i}. {result['law_name']}")
            print(f"   Score: {result['score']:.2f}")
            print(f"   Section: {result['section_title']}")
    else:
        print(f"❌ Error: {data.get('error')}")
except Exception as e:
    print(f"❌ Request failed: {e}")

# Test 3: PageIndex Search
print("\n" + "=" * 60)
print("Test 3: PageIndex Search")
print("=" * 60)

print(f"\n🌲 Query: '{query}'")

try:
    response = requests.post(
        f"{BASE_URL}/api/search/",
        json={"query": query, "top_k_docs": 2, "top_k_sections": 2},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    
    if data['success']:
        print(f"✅ Found {data['total_results']} results via PageIndex")
        
        for i, result in enumerate(data['results'][:3], 1):
            print(f"\n{i}. {result['law_name']} - {result['section_title']}")
            print(f"   Method: {result['retrieval_method']}")
            print(f"   Confidence: {result['reasoning_score']:.2%}")
    else:
        print(f"❌ Error: {data.get('error')}")
except Exception as e:
    print(f"❌ Request failed: {e}")

# Test 4: Comparison
print("\n" + "=" * 60)
print("Test 4: BM25 vs PageIndex Comparison")
print("=" * 60)

print(f"\n⚖️  Query: '{query}'")

try:
    response = requests.post(
        f"{BASE_URL}/api/compare-search/",
        json={"query": query, "top_k": 3},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    
    if data['success']:
        print("\n✅ Comparison Results:")
        
        bm25_data = data['bm25']
        pageindex_data = data['pageindex']
        
        print(f"\n   BM25 ({bm25_data['method']}):")
        print(f"     - Count: {bm25_data['count']}")
        print(f"     - Time: {bm25_data['time_ms']:.2f}ms")
        
        print(f"\n   PageIndex ({pageindex_data['method']}):")
        print(f"     - Count: {pageindex_data['count']}")
        print(f"     - Time: {pageindex_data['time_ms']:.2f}ms")
        
        print(f"\n   Speed Comparison: BM25 is {pageindex_data['time_ms'] / bm25_data['time_ms']:.1f}x faster")
    else:
        print(f"❌ Error: {data.get('error')}")
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n" + "=" * 60)
print("✅ All API Tests Completed!")
print("=" * 60)
