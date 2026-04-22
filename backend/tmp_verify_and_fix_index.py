from pymongo import MongoClient

URI = 'mongodb://localhost:27017/'
DB_NAME = 'legal_AI_db'
COLL_NAME = 'users'

client = MongoClient(URI, serverSelectionTimeoutMS=5000)
client.admin.command('ping')
col = client[DB_NAME][COLL_NAME]

print(f'TOTAL_USERS: {col.count_documents({})}')
print(f'USERNAME_NULL_REMAINING: {col.count_documents({"username": None})}')
print(f'USERNAME_MISSING_REMAINING: {col.count_documents({"username": {"$exists": False}})}')
print('INDEXES_BEFORE:')
for name, info in col.index_information().items():
    print({'name': name, 'key': info.get('key'), 'unique': info.get('unique', False), 'partialFilterExpression': info.get('partialFilterExpression')})

# Drop any existing indexes on username key
for name, info in list(col.index_information().items()):
    if info.get('key') == [('username', 1)] and name != '_id_':
        col.drop_index(name)

# Create supported partial unique index equivalent to non-null string usernames.
created = col.create_index(
    [('username', 1)],
    name='username_unique_non_null',
    unique=True,
    partialFilterExpression={'username': {'$exists': True, '$type': 'string'}},
)
print(f'INDEX_CREATED: {created}')
print('INDEXES_AFTER:')
for name, info in col.index_information().items():
    print({'name': name, 'key': info.get('key'), 'unique': info.get('unique', False), 'partialFilterExpression': info.get('partialFilterExpression')})
