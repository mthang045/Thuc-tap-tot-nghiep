from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['legal_db']

print('Users in database with passwords:\n')
for user in db.users.find():
    print(f'Email: {user.get("email")}')
    print(f'Password: {user.get("password")}')
    print(f'Phone: {user.get("phone")}')
    print()

client.close()
