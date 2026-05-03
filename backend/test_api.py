"""Test API with correct database"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Login as the actual admin user
print("=== Testing Login ===")
login_resp = requests.post(f"{BASE_URL}/login", json={
    "email": "Buiminhthang834@gmail.com",
    "password": "admin123"
})
print(f"Login status: {login_resp.status_code}")
login_data = login_resp.json()
print(f"Success: {login_data.get('success')}")
print(f"is_admin: {login_data.get('is_admin')}")

if not login_data.get('success'):
    print("Login failed!")
    exit(1)

# Save session cookie
cookies = login_resp.cookies

# Test admin analyses list
print("\n=== Testing /admin/analyses ===")
analyses_resp = requests.get(f"{BASE_URL}/admin/analyses", cookies=cookies)
print(f"Status: {analyses_resp.status_code}")
data = analyses_resp.json()
print(f"Success: {data.get('success')}")
if data.get('success'):
    analyses = data.get('analyses', [])
    print(f"Found {len(analyses)} analyses")

    # Test detail with first analysis
    if analyses:
        first_id = analyses[0].get('id')
        print(f"\n=== Testing /admin/analyses/{first_id} ===")
        detail_resp = requests.get(f"{BASE_URL}/admin/analyses/{first_id}", cookies=cookies)
        print(f"Status: {detail_resp.status_code}")
        detail_data = detail_resp.json()
        print(f"Success: {detail_data.get('success')}")

        if detail_data.get('success'):
            analysis = detail_data.get('analysis', {})
            print(f"fileName: {analysis.get('fileName')}")
            print(f"aiAnalysis length: {len(analysis.get('aiAnalysis', '') or '')}")
            print(f"issuesList count: {len(analysis.get('issuesList', []))}")
        else:
            print(f"Error: {detail_data.get('message')}")
