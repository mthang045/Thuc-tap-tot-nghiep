from pymongo import MongoClient
from pprint import pprint
import re
from collections import Counter

URI = 'mongodb://localhost:27017/'
DB_NAME = 'legal_AI_db'
COLL_NAME = 'users'

hexit = 0
backfilled = 0

try:
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
except Exception as e:
    print(f'FAIL: CONNECT_ERROR: {type(e).__name__}: {e}')
    raise SystemExit(1)

col = client[DB_NAME][COLL_NAME]

# Load all existing usernames (non-null) to reserve them.
existing_usernames = set()
for doc in col.find({'username': {'$exists': True, '$ne': None}}, {'username': 1}):
    u = doc.get('username')
    if isinstance(u, str) and u:
        existing_usernames.add(u)

# Find missing or null usernames.
missing_query = {'$or': [{'username': {'$exists': False}}, {'username': None}]}
missing_docs = list(col.find(missing_query, {'email': 1, 'username': 1}))

used = set(existing_usernames)
updates = []

def normalize_prefix(email: str) -> str:
    if not email:
        return 'user'
    prefix = email.split('@', 1)[0]
    prefix = prefix.lower()
    prefix = re.sub(r'[^a-z0-9_]', '', prefix)
    return prefix or 'user'

for doc in missing_docs:
    base = normalize_prefix(doc.get('email'))
    candidate = base
    n = 2
    while candidate in used:
        candidate = f'{base}_{n}'
        n += 1
    used.add(candidate)
    updates.append((doc['_id'], candidate))

for _id, username in updates:
    col.update_one({'_id': _id}, {'$set': {'username': username}})

backfilled = len(updates)

# Drop any indexes whose key is exactly [('username', 1)]
index_info = col.index_information()
for name, info in list(index_info.items()):
    if info.get('key') == [('username', 1)]:
        if name != '_id_':
            col.drop_index(name)

# Create new partial unique index
created_name = col.create_index(
    [('username', 1)],
    name='username_unique_non_null',
    unique=True,
    partialFilterExpression={'username': {'$exists': True, '$ne': None}},
)

# Stats
final_total = col.count_documents({})
remaining_null = col.count_documents({'username': None})
# Missing field count if needed; since user asked null remaining, keep both for debug
remaining_missing = col.count_documents({'username': {'$exists': False}})
indexes = col.index_information()

print('PASS: BACKFILL_COMPLETE')
print(f'TOTAL_USERS: {final_total}')
print(f'BACKFILLED: {backfilled}')
print(f'USERNAME_NULL_REMAINING: {remaining_null}')
print(f'USERNAME_MISSING_REMAINING: {remaining_missing}')
print('INDEXES:')
for name, info in indexes.items():
    print({
        'name': name,
        'key': info.get('key'),
        'unique': info.get('unique', False),
        'partialFilterExpression': info.get('partialFilterExpression')
    })
except_msg = None
