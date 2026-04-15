import pymongo
from datetime import datetime

client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
db = client['legal_AI_db']
code = 'PROFREE2026'

v = db['vouchers'].find_one({'code': code})
print('Voucher:', {'code': v.get('code') if v else None, 'used_count': v.get('used_count') if v else None, 'max_uses': v.get('max_uses') if v else None, 'is_active': v.get('is_active') if v else None})
print('Redemptions count:', db['voucher_redemptions'].count_documents({'voucher_code': code}))
for email in ['user@local.test','user2@local.test','user3@local.test']:
    u = db['users'].find_one({'email': email})
    print(email, '=>', u.get('subscription_tier') if u else 'missing')
client.close()
