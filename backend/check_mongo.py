"""Reset admin password"""
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("mongodb://localhost:27017/")
db = client['legal_AI_db']

# Reset password for admin user
new_password = 'admin123'
new_hash = generate_password_hash(new_password)

result = db['users'].update_one(
    {'email': 'Buiminhthang834@gmail.com'},
    {'$set': {'password': new_hash}}
)

print(f"Updated {result.modified_count} user(s)")
print(f"New hash: {new_hash[:50]}...")

# Verify
user = db['users'].find_one({'email': 'Buiminhthang834@gmail.com'})
print(f"Verify: {check_password_hash(user['password'], new_password)}")
