"""
Sync MongoDB Compass with new schema.

New schema has 11 collections:
    users, chat_sessions, messages, documents, contracts,
    templates, audit_logs, analysis_history,
    law_documents, law_chunks, document_annotations

Remove obsolete collections:
    companies, api_keys, usage_logs

Run: python sync_mongodb_schema.py
"""

import pymongo
from pymongo import ASCENDING, DESCENDING

# ============================================
# Cấu hình
# ============================================
MONGODB_URI = "mongodb://localhost:27017/"
DB_NAME = "legal_AI_db"

# Collections theo schema mới
TARGET_COLLECTIONS = {
    "users",
    "chat_sessions",
    "messages",
    "documents",
    "contracts",
    "templates",
    "audit_logs",
    "analysis_history",
    "law_documents",
    "law_chunks",
    "document_annotations",
}

# Collections cần xóa (thừa, không còn trong schema)
REMOVE_COLLECTIONS = {
    "companies",
    "api_keys",
    "usage_logs",
}

# Index cho từng collection
INDEXES = {
    "users": [
        [("email", ASCENDING)],
        [("role", ASCENDING)],
    ],
    "chat_sessions": [
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        [("agent_type", ASCENDING)],
        [("status", ASCENDING)],
    ],
    "messages": [
        [("session_id", ASCENDING), ("created_at", ASCENDING)],
        [("user_id", ASCENDING)],
    ],
    "documents": [
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        [("status", ASCENDING)],
        [("doc_type", ASCENDING)],
    ],
    "contracts": [
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        [("contract_type", ASCENDING)],
        [("status", ASCENDING)],
    ],
    "templates": [
        [("doc_type", ASCENDING)],
        [("is_global", ASCENDING)],
        [("created_by", ASCENDING)],
    ],
    "audit_logs": [
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        [("action", ASCENDING)],
        [("resource_type", ASCENDING)],
    ],
    "analysis_history": [
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        [("contract_type", ASCENDING)],
        [("risk_level", ASCENDING)],
    ],
    "law_documents": [
        [("title", ASCENDING)],
        [("status", ASCENDING)],
        [("domains", ASCENDING)],
        [("law_number", ASCENDING)],
    ],
    "law_chunks": [
        [("law_id", ASCENDING), ("article", ASCENDING)],
        [("domains", ASCENDING)],
    ],
    "document_annotations": [
        [("document_id", ASCENDING)],
        [("created_by", ASCENDING)],
    ],
}


def main():
    print("=" * 55)
    print("  MongoDB Schema Sync")
    print("=" * 55)

    try:
        client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print(f"[OK] Connected to MongoDB: {MONGODB_URI}")
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        return

    db = client[DB_NAME]

    # List current collections
    existing = set(db.list_collection_names())
    print(f"\n[*] Current collections ({len(existing)}): {sorted(existing)}")

    # 1. Remove obsolete collections
    print("\n[*] Removing obsolete collections...")
    for col in sorted(REMOVE_COLLECTIONS):
        if col in existing:
            try:
                db[col].drop()
                print(f"   [DEL] {col}")
            except Exception as e:
                print(f"   [ERR] {col}: {e}")
        else:
            print(f"   [SKIP] {col} (not found)")

    # 2. Create missing collections
    print("\n[*] Creating new collections...")
    for col in sorted(TARGET_COLLECTIONS):
        if col not in existing:
            db.create_collection(col)
            print(f"   [CREATED] {col}")
        else:
            print(f"   [EXISTS] {col}")

    # 3. Create indexes
    print("\n[*] Creating indexes...")
    for col, indexes in sorted(INDEXES.items()):
        if col not in TARGET_COLLECTIONS:
            continue
        try:
            existing_indexes = set(
                idx["name"] for idx in db[col].list_indexes()
            )
            for fields in indexes:
                field_names = "_".join(f for f, _ in fields)
                idx_name = field_names
                if idx_name not in existing_indexes:
                    db[col].create_index(fields, name=idx_name)
                    print(f"   [OK] {col}.{idx_name}")
                else:
                    print(f"   [SKIP] {col}.{idx_name} (already exists)")
        except Exception as e:
            print(f"   [WARN] {col}: {e}")

    # 4. Final result
    final_collections = set(db.list_collection_names())
    print("\n" + "=" * 55)
    print("DONE - Schema sync completed!")
    print(f"   Database: {DB_NAME}")
    print(f"   Collections: {sorted(final_collections)}")
    print("=" * 55)


if __name__ == "__main__":
    main()
