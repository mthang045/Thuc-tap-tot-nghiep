# Font Setup for Vietnamese PDF Support

## Required Fonts

Để hiển thị tiếng Việt có dấu trong PDF, bạn cần 3 file font Arial:

1. **arial.ttf** - Arial Regular (chữ thường)
2. **arialbd.ttf** - Arial Bold (chữ đậm)
3. **ariali.ttf** - Arial Italic (chữ nghiêng)

## Option 1: Copy từ Windows Fonts (KHUYẾN KHÍCH)

Trên Windows, các font Arial đã có sẵn tại: `C:\Windows\Fonts\`

### Cách làm:

```powershell
# Mở PowerShell tại thư mục backend/fonts/
cd "c:\Users\buimi\OneDrive\Documents\Thực tập\GenZ-Legal-AI-Final\backend\fonts"

# Copy 3 file font từ Windows Fonts
Copy-Item "C:\Windows\Fonts\arial.ttf" -Destination .
Copy-Item "C:\Windows\Fonts\arialbd.ttf" -Destination .
Copy-Item "C:\Windows\Fonts\ariali.ttf" -Destination .

# Verify
Get-ChildItem *.ttf
```

**Output mong đợi:**
```
arial.ttf      # ~750KB
arialbd.ttf    # ~750KB  
ariali.ttf     # ~650KB
```

##Option 2: Download từ Internet

Nếu không tìm thấy trong `C:\Windows\Fonts\`, bạn có thể:

1. Tìm kiếm "Arial font download" trên Google
2. Download 3 file .ttf
3. Copy vào thư mục `backend/fonts/`

## Verify Installation

Sau khi copy xong, test PDF generator:

```bash
cd backend
python pdf_generator.py
```

Nếu thành công, bạn sẽ thấy:
```
✅ Loaded arial.ttf
✅ Loaded arialbd.ttf (Bold)
✅ Loaded ariali.ttf (Italic)
✅ Vietnamese fonts loaded successfully!
✅ PDF generated successfully: test_report.pdf
```

## Troubleshooting

**❌ Lỗi: "Font files not found"**
- Kiểm tra xem 3 file .ttf đã ở đúng thư mục `backend/fonts/` chưa
- Chạy: `ls backend/fonts/*.ttf`

**❌ Lỗi: "Permission denied"**
- Chạy PowerShell với quyền Administrator
- Hoặc copy file thủ công bằng File Explorer

**⚠️ Fallback Mode**
- Nếu không có font, PDF vẫn được tạo nhưng tiếng Việt sẽ bị lỗi
- Hệ thống sẽ dùng Helvetica (không hỗ trợ tiếng Việt có dấu)

---

**Lưu ý:** Các font Arial thuộc bản quyền Microsoft. Chỉ sử dụng cho mục đích học tập/nghiên cứu.
