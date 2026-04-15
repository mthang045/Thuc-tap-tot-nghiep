"""Promote a user to admin in the MongoDB `legal_AI_db` database.

Usage:
  python backend/set_admin.py user@example.com

This script sets the `is_admin` field to True for the given email.
Requires a running MongoDB on the default localhost:27017.
"""
import sys
import pymongo

def promote(email):
    client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['legal_AI_db']
    users = db['users']
    res = users.update_one({'email': email}, {'$set': {'is_admin': True}})
    if res.matched_count == 0:
        print(f"No user found with email: {email}")
    else:
        print(f"Promoted {email} to admin (modified: {res.modified_count})")
    client.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python backend/set_admin.py user@example.com')
        sys.exit(1)
    promote(sys.argv[1])
