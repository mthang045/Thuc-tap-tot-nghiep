import jwt, datetime

secret = 'legal-contract-reviewer-secret-key-2026'
now = datetime.datetime.utcnow()
pro_payload = {
    'email': 'pro@example.com',
    'subscription_tier': 'pro',
    'is_admin': False,
    'exp': now + datetime.timedelta(days=7),
    'iat': now
}
admin_payload = {
    'email': 'admin@example.com',
    'subscription_tier': 'free',
    'is_admin': True,
    'exp': now + datetime.timedelta(days=7),
    'iat': now
}

print('PRO_TOKEN:')
print(jwt.encode(pro_payload, secret, algorithm='HS256'))
print('\nADMIN_TOKEN:')
print(jwt.encode(admin_payload, secret, algorithm='HS256'))
