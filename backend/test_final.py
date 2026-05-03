import requests

# Test với /v1 prefix (frontend gọi)
r = requests.get('http://localhost:5000/v1/api/templates/hop_dong_lao_dong/download', timeout=10)
print(f"With /v1 prefix: Status {r.status_code}")
print(f"Response: {r.text[:200]}")

# Test không có /v1
r2 = requests.get('http://localhost:5000/api/templates/hop_dong_lao_dong/download', timeout=10)
print(f"\nWithout /v1: Status {r2.status_code}")
print(f"Size: {len(r2.content)} bytes")
