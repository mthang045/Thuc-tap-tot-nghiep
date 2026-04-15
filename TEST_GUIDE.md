# 🚀 TEST HỆ THỐNG - Hướng dẫn nhanh

## ✅ Trạng thái hiện tại:

```
✓ Backend API:     http://localhost:5000 (RUNNING)
✓ Frontend:        http://localhost:3000 (RUNNING)  
✓ MongoDB:         legal_AI_db (CONNECTED)
✓ User đã tạo:     2331540024@vaa.edu.vn
```

## 🔧 Các vấn đề đã fix:

1. ✅ **Lỗi API Key** - Có fallback mode, vẫn hoạt động khi chưa có API key
2. ✅ **Lưu lịch sử** - Tự động lưu vào MongoDB collection `analysis_history`
3. ✅ **API endpoints mới** - GET/DELETE lịch sử phân tích

## 📝 Hướng dẫn test ngay:

### Bước 1: Upload hợp đồng để tạo lịch sử
1. Mở trình duyệt: http://localhost:3000
2. Đăng nhập với: `2331540024@vaa.edu.vn` / `Buithang12`
3. Upload file hợp đồng bất kỳ (.docx, .pdf, .txt)
4. Xem kết quả phân tích

### Bước 2: Kiểm tra lịch sử trong MongoDB
```bash
# Chạy trong terminal backend (đã activate venv):
python check_mongodb.py
```

### Bước 3: Test API lịch sử
```bash
# Lấy token từ browser (F12 > Application > Local Storage > token)
# Sau đó test API:

# GET lịch sử
curl http://localhost:5000/api/history/ -H "Authorization: Bearer YOUR_TOKEN"

# GET chi tiết 1 lịch sử
curl http://localhost:5000/api/history/HISTORY_ID -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔑 Để bật AI phân tích đầy đủ:

**Hiện tại:** Hệ thống chạy ở **Basic Mode** (không có AI chi tiết)

**Nâng cấp lên AI Mode:**
1. Truy cập: https://console.groq.com/keys
2. Đăng nhập (miễn phí) bằng Google/GitHub
3. Tạo API key mới
4. Mở file `.env` và cập nhật:
   ```env
   GROQ_API_KEY=gsk_your_actual_key_here
   ```
5. Restart backend:
   - Ctrl+C trong terminal backend
   - Chạy lại: `python simple_api.py`

## 📊 Xem dữ liệu MongoDB:

### Cách 1: Script Python
```bash
cd backend
.\venv\Scripts\Activate.ps1
python check_mongodb.py
```

### Cách 2: VS Code Extension
1. Install "MongoDB for VS Code" extension
2. Connect to: `mongodb://localhost:27017`
3. Browse database `legal_AI_db`
4. Xem collections: `users`, `analysis_history`

### Cách 3: MongoDB Compass (nếu có)
- Connection string: `mongodb://localhost:27017`
- Database: `legal_AI_db`

## 🎯 Tính năng mới có thể test:

### 1. Upload hợp đồng (đã có từ trước, nâng cấp)
- ✅ Fallback khi không có AI
- ✅ Tự động lưu lịch sử
- ✅ Link với user qua token

### 2. Xem lịch sử phân tích (MỚI)
```javascript
// Frontend có thể gọi:
fetch('http://localhost:5000/api/history/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

### 3. Xem chi tiết 1 lịch sử (MỚI)
```javascript
fetch('http://localhost:5000/api/history/HISTORY_ID', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

### 4. Xóa lịch sử (MỚI)
```javascript
fetch('http://localhost:5000/api/history/HISTORY_ID', {
  method: 'DELETE',
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

## 📦 Cấu trúc lịch sử trong MongoDB:

Mỗi lần upload, hệ thống lưu:
```json
{
  "user_email": "2331540024@vaa.edu.vn",
  "filename": "contract.docx",
  "file_size": 25779,
  "upload_time": "2026-03-06T21:57:14",
  "contract_type": "Hợp đồng vận chuyển",
  "risk_level": "medium",
  "has_violation": false,
  "summary": "...",
  "ai_analysis": "...",
  "issues_count": 3,
  "issues": ["🚨 Vấn đề 1", "⚡ Vấn đề 2", "ℹ️ Vấn đề 3"],
  "created_at": "2026-03-06T21:57:14.123Z"
}
```

## ⚡ Quick Commands:

```bash
# Kiểm tra MongoDB
cd backend
.\venv\Scripts\Activate.ps1
python check_mongodb.py

# Restart backend
# Ctrl+C trong terminal backend
python simple_api.py

# Kiểm tra health
curl http://localhost:5000/health

# Test API (cần token)
$token = "YOUR_TOKEN_HERE"
Invoke-RestMethod -Uri "http://localhost:5000/api/history/" -Headers @{"Authorization"="Bearer $token"}
```

## 🐛 Troubleshooting:

### Lỗi "Không thể phân tích chi tiết"
✅ **Đã fix!** Hệ thống bây giờ có fallback mode
- Upload vẫn hoạt động
- Phân tích cơ bản vẫn có
- Lịch sử vẫn được lưu
- Để nâng cấp: thêm GROQ_API_KEY

### Collection analysis_history chưa có
✅ **Bình thường!** Collection tự động tạo khi có upload đầu tiên
- Upload 1 file → collection sẽ xuất hiện
- Chạy `check_mongodb.py` để xác nhận

### Token hết hạn
- Đăng nhập lại để lấy token mới
- Token có thời hạn 7 ngày

## 📚 Tài liệu tham khảo:

- [FIXED_ISSUES.md](FIXED_ISSUES.md) - Chi tiết các fix và cải tiến
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Hướng dẫn setup ban đầu
- [README.md](README.md) - Tổng quan dự án

---

**🎉 Hệ thống đã sẵn sàng để test!**

Hãy upload một vài hợp đồng và kiểm tra xem lịch sử có được lưu vào MongoDB không.
