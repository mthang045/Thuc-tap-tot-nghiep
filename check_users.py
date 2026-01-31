from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['legal_db']

count = db.users.count_documents({})
print(f'Số users trong database: {count}\n')

if count > 0:
    print('Danh sách users:')
    for user in db.users.find():
        print(f'  - Email: {user.get("email")}')
        print(f'    Phone: {user.get("phone")}')
        print(f'    Name: {user.get("full_name")}')
        print(f'    Created: {user.get("created_at")}')
        print()
else:
    print('Database TRỐNG - không có users nào!')

client.close()
