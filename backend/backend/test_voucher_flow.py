import requests
import pymongo
import jwt
import sys
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

API = 'http://localhost:5000/api'
SECRET = 'legal-contract-reviewer-secret-key-2026'

admin_email = 'admin@local.test'
user_email = 'user@local.test'

# Ensure test user exists in DB
client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
db = client['legal_AI_db']
users = db['users']
existing = users.find_one({'email': user_email})
if not existing:
    hashed = generate_password_hash('password123')
    users.insert_one({'email': user_email, 'full_name': 'Test User', 'password': hashed, 'subscription_tier': 'free', 'is_admin': False, 'created_at': datetime.now(timezone.utc)})
    print(f'Inserted test user: {user_email}')
else:
    # reset to free
    users.update_one({'email': user_email}, {'$set': {'subscription_tier': 'free'}})
    print(f'User exists, reset subscription to free: {user_email}')

# Generate tokens
now = datetime.now(timezone.utc)
admin_payload = {'email': admin_email, 'full_name': 'Admin', 'subscription_tier': 'pro', 'is_admin': True, 'exp': now + timedelta(days=7), 'iat': now}
user_payload = {'email': user_email, 'full_name': 'Test User', 'subscription_tier': 'free', 'is_admin': False, 'exp': now + timedelta(days=7), 'iat': now}

admin_token = jwt.encode(admin_payload, SECRET, algorithm='HS256')
user_token = jwt.encode(user_payload, SECRET, algorithm='HS256')

headers_admin = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
headers_user = {'Authorization': f'Bearer {user_token}', 'Content-Type': 'application/json'}


def assert_status(resp, expected_status, step_name):
    if resp.status_code != expected_status:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        raise AssertionError(f"[{step_name}] Expected {expected_status}, got {resp.status_code}. Body: {body}")


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)

code = 'PROFREE2026'
# 1) Create voucher
print('\n--- Creating voucher (admin) ---')
create_body = {
    'code': code,
    'discount_type': 'free_pro',
    'value': 0,
    'max_uses': 2,
    'expires_at': '2026-12-31'
}
resp = requests.post(f'{API}/admin/vouchers', json=create_body, headers=headers_admin)
try:
    print('Status:', resp.status_code, 'Response:', resp.json())
except Exception:
    print('Status:', resp.status_code, 'Non-JSON response')
assert_status(resp, 201, 'Create voucher')

# 2) List vouchers
print('\n--- List vouchers (admin) ---')
resp = requests.get(f'{API}/admin/vouchers', headers=headers_admin)
print('Status:', resp.status_code)
assert_status(resp, 200, 'List vouchers')
try:
    data = resp.json()
    print('Count:', len(data.get('data', [])))
    assert_true(any(v.get('code') == code for v in data.get('data', [])), 'Created voucher not found in admin list')
    for v in data.get('data', []):
        if v.get('code') == code:
            print('Voucher:', v)
except Exception as e:
    print('Failed parsing list:', e)

# 3) Apply voucher as user (first time)
print('\n--- Apply voucher (user) - first attempt ---')
resp = requests.post(f'{API}/vouchers/apply', json={'code': code}, headers=headers_user)
print('Status:', resp.status_code)
try:
    print('Response:', resp.json())
except Exception:
    print('Non-JSON')
assert_status(resp, 200, 'Apply voucher first attempt')

# 4) Check DB state after apply
print('\n--- DB state after first apply ---')
v = db['vouchers'].find_one({'code': code})
print('Voucher used_count:', v.get('used_count') if v else 'not found')
u = users.find_one({'email': user_email})
print('User subscription_tier:', u.get('subscription_tier'))
red = db['voucher_redemptions'].find_one({'voucher_code': code, 'user_email': user_email})
print('Redemption record exists:', bool(red))
assert_true(bool(v), 'Voucher not found in DB after first apply')
assert_true(v.get('used_count') == 1, 'Voucher used_count should be 1 after first apply')
assert_true(u.get('subscription_tier') == 'pro', 'First user subscription should be pro after apply')
assert_true(bool(red), 'Redemption record should exist after first apply')

# 5) Apply voucher again (should fail)
print('\n--- Apply voucher (user) - second attempt (expect failure) ---')
resp2 = requests.post(f'{API}/vouchers/apply', json={'code': code}, headers=headers_user)
print('Status:', resp2.status_code)
try:
    print('Response:', resp2.json())
except Exception:
    print('Non-JSON')
assert_status(resp2, 400, 'Apply voucher second attempt same user')

# 6) Another user uses voucher to consume second slot
another_email = 'user2@local.test'
existing2 = users.find_one({'email': another_email})
if not existing2:
    users.insert_one({'email': another_email, 'full_name': 'Second User', 'password': generate_password_hash('x'), 'subscription_tier': 'free', 'is_admin': False, 'created_at': datetime.now(timezone.utc)})
print('\n--- Apply voucher as second user to consume last slot ---')
user2_payload = {'email': another_email, 'full_name': 'Second User', 'subscription_tier': 'free', 'is_admin': False, 'exp': now + timedelta(days=7), 'iat': now}
user2_token = jwt.encode(user2_payload, SECRET, algorithm='HS256')
headers_user2 = {'Authorization': f'Bearer {user2_token}', 'Content-Type': 'application/json'}
resp3 = requests.post(f'{API}/vouchers/apply', json={'code': code}, headers=headers_user2)
print('Status:', resp3.status_code)
try:
    print('Response:', resp3.json())
except Exception:
    print('Non-JSON')
assert_status(resp3, 200, 'Apply voucher second user')

print('\n--- DB state after second user apply ---')
v = db['vouchers'].find_one({'code': code})
print('Voucher used_count:', v.get('used_count') if v else 'not found')
assert_true(v.get('used_count') == 2, 'Voucher used_count should be 2 after second user apply')

# 7) Third user attempt should be blocked due to max_uses
third_email = 'user3@local.test'
existing3 = users.find_one({'email': third_email})
if not existing3:
    users.insert_one({'email': third_email, 'full_name': 'Third User', 'password': generate_password_hash('x'), 'subscription_tier': 'free', 'is_admin': False, 'created_at': datetime.now(timezone.utc)})
third_payload = {'email': third_email, 'full_name': 'Third User', 'subscription_tier': 'free', 'is_admin': False, 'exp': now + timedelta(days=7), 'iat': now}
third_token = jwt.encode(third_payload, SECRET, algorithm='HS256')
headers_third = {'Authorization': f'Bearer {third_token}', 'Content-Type': 'application/json'}
print('\n--- Apply voucher as third user (expect exhausted) ---')
resp4 = requests.post(f'{API}/vouchers/apply', json={'code': code}, headers=headers_third)
print('Status:', resp4.status_code)
try:
    print('Response:', resp4.json())
except Exception:
    print('Non-JSON')
assert_status(resp4, 400, 'Apply voucher third user exhausted')

# Final DB checks
print('\n--- Final DB checks ---')
v = db['vouchers'].find_one({'code': code})
print('Voucher doc:', {k: v[k] for k in ('code', 'used_count', 'max_uses', 'is_active', 'expires_at')})
print('Redemptions count:', db['voucher_redemptions'].count_documents({'voucher_code': code}))
print('User subscription (first user):', users.find_one({'email': user_email}).get('subscription_tier'))
print('Second user subscription:', users.find_one({'email': another_email}).get('subscription_tier'))
assert_true(v.get('used_count') == 2, 'Final voucher used_count should remain 2')
assert_true(db['voucher_redemptions'].count_documents({'voucher_code': code}) == 2, 'Final redemption count should be 2')
assert_true(users.find_one({'email': user_email}).get('subscription_tier') == 'pro', 'First user final subscription should be pro')
assert_true(users.find_one({'email': another_email}).get('subscription_tier') == 'pro', 'Second user final subscription should be pro')
client.close()

print('\n✅ Voucher flow test passed')
sys.exit(0)
