import requests
import os

os.chdir(r"C:\Users\buimi\OneDrive\Documents\Thực tập\backend")

r = requests.get('http://localhost:5000/api/templates/hop_dong_lao_dong/download', timeout=10)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    with open('test_download.docx', 'wb') as f:
        f.write(r.content)
    print(f"SUCCESS! File saved, size: {len(r.content)} bytes")
else:
    # Get error from response
    print(f"Error: {r.text[:500]}")
