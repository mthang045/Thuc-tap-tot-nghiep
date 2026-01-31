# 📂 Hướng dẫn thêm file luật vào hệ thống

## 🎯 Vị trí lưu các file PDF luật

```
C:\Users\buimi\OneDrive\Documents\Thuc_tap\backend\data\source_laws\
```

## 📁 Cấu trúc thư mục:

### 1️⃣ **co_ban/** - Bộ luật cơ bản (Ưu tiên tải trước)
Thêm 5 file PDF này vào thư mục `co_ban/`:
- `Bo_luat_Dan_su_2015.pdf`
- `Luat_Thuong_mai_2005.pdf`
- `Bo_luat_Lao_dong_2019.pdf`
- `Luat_Dat_dai_2013.pdf`
- `Luat_Nha_o_2014.pdf`

### 2️⃣ **doanh_nghiep/** - Liên quan doanh nghiệp
- `Luat_Doanh_nghiep_2020.pdf`
- `Luat_Dau_tu_2020.pdf`
- `Luat_Hop_tac_xa_2012.pdf`

### 3️⃣ **so_huu_tri_tue/** - Sở hữu trí tuệ
- `Luat_So_huu_tri_tue_2019.pdf`
- `Luat_Cong_nghe_thong_tin_2006.pdf`

### 4️⃣ **tai_chinh_thue/** - Tài chính - Thuế
- `Luat_Thue_GTGT_2008.pdf`
- `Luat_Thue_TNDN_2008.pdf`
- `Luat_Ke_toan_2015.pdf`

### 5️⃣ **ngan_hang_tin_dung/** - Ngân hàng
- `Luat_Cac_to_chuc_tin_dung_2010.pdf`
- `Luat_Chung_khoan_2019.pdf`

### 6️⃣ **xay_dung_bds/** - Xây dựng - BĐS
- `Luat_Xay_dung_2014.pdf`
- `Luat_Kinh_doanh_BDS_2014.pdf`

### 7️⃣ **bao_mat/** - Bảo mật
- `Luat_An_toan_thong_tin_mang_2015.pdf`
- `Luat_Bao_ve_bi_mat_nha_nuoc_2018.pdf`

### 8️⃣ **tranh_chap/** - Giải quyết tranh chấp
- `Luat_Trong_tai_thuong_mai_2010.pdf`
- `Bo_luat_To_tung_dan_su_2015.pdf`

### 9️⃣ **khac/** - Các luật khác
- `Luat_Giao_duc_2019.pdf`
- `Luat_Y_te_2009.pdf`
- `Luat_Bao_hiem_xa_hoi_2014.pdf`

---

## 🚀 HƯỚNG DẪN TỪNG BƯỚC

### Bước 1: Tải file PDF từ Thư viện pháp luật

#### Cách 1: Tải từ ThuvienPhapLuat.vn (Khuyến nghị)
1. Truy cập: https://thuvienphapluat.vn
2. Tìm kiếm: "Bộ luật Dân sự 2015"
3. Click vào kết quả → Click "Tải về PDF"
4. Lưu file với tên chuẩn: `Bo_luat_Dan_su_2015.pdf`

#### Cách 2: Tải từ Cổng thông tin điện tử Chính phủ
1. Truy cập: https://chinhphu.vn
2. Menu "Văn bản pháp luật"
3. Tìm kiếm và tải về

### Bước 2: Copy file PDF vào đúng thư mục

#### Cách 1: Dùng File Explorer (Đơn giản nhất)
```
1. Mở File Explorer
2. Dán đường dẫn này vào thanh địa chỉ:
   C:\Users\buimi\OneDrive\Documents\Thuc_tap\backend\data\source_laws

3. Mở thư mục tương ứng (vd: co_ban)
4. Copy-paste file PDF vào đó
```

#### Cách 2: Dùng PowerShell
```powershell
# Ví dụ: Copy file Bộ luật Dân sự vào thư mục co_ban
Copy-Item "C:\Downloads\Bo_luat_Dan_su_2015.pdf" "C:\Users\buimi\OneDrive\Documents\Thuc_tap\backend\data\source_laws\co_ban\"
```

#### Cách 3: Kéo thả (Drag & Drop)
```
1. Mở thư mục Downloads (nơi file PDF đã tải)
2. Mở thư mục đích trong cửa sổ khác
3. Kéo thả file PDF vào thư mục đích
```

### Bước 3: Kiểm tra file đã copy thành công

Chạy lệnh này trong PowerShell:
```powershell
cd "C:\Users\buimi\OneDrive\Documents\Thuc_tap"
Get-ChildItem backend\data\source_laws\* -Include *.pdf -Recurse
```

Kết quả sẽ hiện danh sách tất cả file PDF đã thêm.

### Bước 4: Chạy script ingest để train AI

```powershell
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Chạy ingest
cd backend
python ingest.py

# 3. Test xem đã train thành công chưa
python test_agent.py
```

---

## 📋 CHECKLIST - Bộ luật ưu tiên cao nhất

### ✅ BẮT ĐẦU VỚI 5 FILE NÀY (Đủ cho 80% hợp đồng):

- [ ] `co_ban/Bo_luat_Dan_su_2015.pdf`
- [ ] `co_ban/Luat_Thuong_mai_2005.pdf`
- [ ] `co_ban/Bo_luat_Lao_dong_2019.pdf`
- [ ] `co_ban/Luat_Dat_dai_2013.pdf`
- [ ] `co_ban/Luat_Nha_o_2014.pdf`

### 📊 Sau khi test thấy ok, thêm tiếp:

- [ ] `doanh_nghiep/Luat_Doanh_nghiep_2020.pdf`
- [ ] `doanh_nghiep/Luat_Dau_tu_2020.pdf`
- [ ] `so_huu_tri_tue/Luat_So_huu_tri_tue_2019.pdf`
- [ ] `tranh_chap/Luat_Trong_tai_thuong_mai_2010.pdf`

---

## 🔍 KIỂM TRA SAU KHI THÊM FILE

### 1. Kiểm tra file đã có chưa:
```powershell
# Xem tất cả file PDF
Get-ChildItem "C:\Users\buimi\OneDrive\Documents\Thuc_tap\backend\data\source_laws" -Recurse -Filter *.pdf | Select-Object FullName

# Đếm số lượng file
(Get-ChildItem "C:\Users\buimi\OneDrive\Documents\Thuc_tap\backend\data\source_laws" -Recurse -Filter *.pdf).Count
```

### 2. Kiểm tra dung lượng file:
```powershell
Get-ChildItem "C:\Users\buimi\OneDrive\Documents\Thuc_tap\backend\data\source_laws" -Recurse -Filter *.pdf | 
    Measure-Object -Property Length -Sum | 
    Select-Object @{Name="TotalSizeMB";Expression={[math]::Round($_.Sum / 1MB, 2)}}
```

### 3. Kiểm tra file có đọc được không:
```powershell
cd backend
python -c "import PyPDF2; f = open('data/source_laws/co_ban/Bo_luat_Dan_su_2015.pdf', 'rb'); reader = PyPDF2.PdfReader(f); print(f'Pages: {len(reader.pages)}'); print(reader.pages[0].extract_text()[:200])"
```

---

## ⚡ NHANH HƠN: Tải hàng loạt

Nếu muốn tải nhiều file cùng lúc, tôi có thể tạo script Python tự động:

```python
# download_laws.py
import requests
from pathlib import Path

laws = {
    'co_ban': [
        ('Bo_luat_Dan_su_2015.pdf', 'https://thuvienphapluat.vn/...'),
        ('Luat_Thuong_mai_2005.pdf', 'https://thuvienphapluat.vn/...'),
        # ... thêm URL
    ]
}

for folder, files in laws.items():
    for filename, url in files:
        # Download logic
        pass
```

---

## 🐛 XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi 1: File PDF bị scan không OCR được
**Giải pháp:** Dùng tool OCR để convert:
```bash
pip install pdf2image pytesseract
python ocr_pdf.py input.pdf output.pdf
```

### Lỗi 2: File PDF bị mã hóa/password
**Giải pháp:** Dùng tool unlock PDF online hoặc:
```bash
pip install pikepdf
python unlock_pdf.py input.pdf output.pdf
```

### Lỗi 3: File không phải PDF chuẩn
**Giải pháp:** Convert lại từ DOC/DOCX:
```bash
# Dùng Microsoft Word hoặc LibreOffice
# File → Save As → PDF
```

---

## 📞 HỖ TRỢ

Nếu gặp khó khăn:
1. Check file LAWS_NEEDED.md để xem danh sách đầy đủ
2. Check file DEVELOPMENT.md để xem cách train AI
3. Chạy `python ingest.py --help` để xem options

---

## 📈 THEO DÕI TIẾN ĐỘ

Tạo file tracking đơn giản:
```powershell
# Tạo file progress.txt
$total = 25  # Tổng số bộ luật
$current = (Get-ChildItem "backend\data\source_laws" -Recurse -Filter *.pdf).Count
Write-Host "Progress: $current/$total ($([math]::Round($current/$total*100))%)"
```

---

**Ghi chú:** 
- ✅ Thư mục đã được tạo sẵn
- ✅ Chỉ cần copy file PDF vào là xong
- ✅ Đặt tên file đúng như hướng dẫn để dễ quản lý
