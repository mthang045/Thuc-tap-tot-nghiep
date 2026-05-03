import requests

# Frontend sẽ gọi /api/templates/... (proxy qua vite -> backend /api/templates/...)
r = requests.get('http://localhost:5000/api/templates/hop_dong_lao_dong/download', timeout=10)
print(f"Download: Status {r.status_code}, Size {len(r.content)} bytes")

# Frontend gọi /v1/templates (proxy -> backend /v1/templates)
r2 = requests.get('http://localhost:5000/v1/templates', timeout=10)
print(f"Templates list: Status {r2.status_code}")
