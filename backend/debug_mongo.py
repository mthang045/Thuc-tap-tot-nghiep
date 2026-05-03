"""Debug script to check MongoDB data structure"""
from pymongo import MongoClient
from bson import ObjectId
import sys
import os

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['legal_AI_db']
analysis_collection = db['analysis_history']

# Get all documents
docs = list(analysis_collection.find({}).limit(3))

print(f"Found {len(docs)} documents")
for i, doc in enumerate(docs):
    print(f"\n=== Document {i+1} ===")
    print(f"_id: {doc.get('_id')}")
    print(f"Keys: {list(doc.keys())}")
    
    # Check for nested 'data' field
    if 'data' in doc:
        print(f"'data' field: EXISTS")
        if isinstance(doc['data'], dict):
            print(f"  data keys: {list(doc['data'].keys())}")
    else:
        print(f"'data' field: NOT EXISTS")
    
    # Top-level fields
    print(f"filename: {doc.get('filename', 'N/A')}")
    print(f"upload_time: {doc.get('upload_time', 'N/A')}")
    print(f"created_at: {doc.get('created_at', 'N/A')}")
    print(f"ai_analysis length: {len(str(doc.get('ai_analysis', '')))}")
    print(f"summary length: {len(str(doc.get('summary', '')))}")
    print(f"issues_count: {doc.get('issues_count', 'N/A')}")
    
    issues = doc.get('issues')
    if issues:
        print(f"issues type: {type(issues)}")
        if isinstance(issues, list):
            print(f"issues count: {len(issues)}")
            if issues:
                first = issues[0]
                print(f"first issue type: {type(first)}")
                if isinstance(first, dict):
                    print(f"first issue keys: {list(first.keys())}")
