import jwt, datetime
payload={'email':'pro@example.com','subscription_tier':'pro','exp': datetime.datetime.utcnow()+datetime.timedelta(days=7),'iat':datetime.datetime.utcnow()}
print(jwt.encode(payload, 'legal-contract-reviewer-secret-key-2026', algorithm='HS256'))
