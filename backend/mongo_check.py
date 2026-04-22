from pymongo import MongoClient
from pprint import pprint

uri = "mongodb://localhost:27017/"
db_name = "legal_AI_db"

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
except Exception as e:
    print(f"CONNECT_ERROR: {type(e).__name__}: {e}")
    raise SystemExit(1)

col = client[db_name]["users"]

print(f"TOTAL_USERS: {col.count_documents({})}")
print(f"USERNAME_NULL: {col.count_documents({'username': None})}")
print(f"USERNAME_MISSING: {col.count_documents({'username': {'$exists': False}})}")

print("SAMPLE_DOCS:")
for d in col.find({}, {'_id': 1, 'email': 1, 'username': 1}).limit(5):
    pprint(d)

print("CREATE_UNIQUE_INDEX_USERNAME:")
try:
    idx = col.create_index('username', unique=True, name='uniq_username_test')
    print(f"INDEX_CREATED: {idx}")
except Exception as e:
    print(f"INDEX_ERROR: {type(e).__name__}: {str(e).splitlines()[0]}")
