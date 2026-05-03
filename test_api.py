
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

s = requests.Session()
s.get('http://127.0.0.1:5000/api/csrf/')
r = s.post('http://127.0.0.1:5000/api/login', json={'email': 'testadmin@test.com', 'password': 'TestAdmin123'})
print('Login:', r.status_code)

r2 = s.get('http://127.0.0.1:5000/api/admin/analyses')
analyses = r2.json().get('analyses', [])
print('Total analyses:', len(analyses))

# Test first 5
passed = 0
failed = 0
for a in analyses[:5]:
    aid = a['id']
    r3 = s.get('http://127.0.0.1:5000/api/admin/analyses/' + aid)
    ok = r3.status_code == 200
    status = 'PASS' if ok else 'FAIL'
    fname = ''
    issues = 0
    if ok:
        data = r3.json().get('analysis', {})
        fname = data.get('fileName', '')
        issues = data.get('issues', 0)
        passed += 1
    else:
        failed += 1
    print(status, '| id:', aid[:16], '| fname:', fname, '| issues:', issues)

    # Test download
    r4 = s.get('http://127.0.0.1:5000/api/admin/analyses/' + aid + '/download')
    dstatus = 'PASS' if r4.status_code == 200 else 'FAIL'
    print('  Download:', dstatus, '| size:', len(r4.content) if r4.status_code == 200 else 'N/A')

print()
print('Results:', passed, 'passed,', failed, 'failed')
