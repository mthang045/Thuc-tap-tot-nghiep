"""
Smart Template Filler - Precise field replacement
Uses regex to replace placeholder patterns in templates
"""

import json
import os
import re
import random
from datetime import datetime, timedelta

TEMPLATES_DIR = "static/templates"
OUTPUT_DIR = "training_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================== DATA POOLS ====================

COMPANY_NAMES = [
    "Công Ty TNHH Thương Mại Vạn Phát", "Công Ty Cổ Phần Đầu Tư Phát Triển Minh Quân",
    "Công Ty TNHH MTV Xây Dựng Hoàng Gia", "Công Ty Cổ Phần Sản Xuất Thương Mại Bình Minh",
    "Công Ty TNHH Thương Mại Dịch Vụ Tân Á", "Công Ty Cổ Phần Tập Đoàn Đông Á",
    "Công Ty TNHH MTV Kỹ Thuật Số Việt Nam", "Công Ty Cổ Phần Thương Mại Quốc Tế Thăng Long",
    "Công Ty TNHH Xây Lắp Điện Lực Miền Trung", "Công Ty Cổ Phần Năng Lượng Sạch Việt",
    "Công Ty TNHH Thương Mại Tổng Hợp Hùng Vương", "Công Ty Cổ Phần Vận Tải Biển Hải Âu",
    "Công Ty TNHH Dịch Vụ Logistics Toàn Cầu", "Công Ty Cổ Phần Xây Dựng Công Nghiệp D&D",
    "Công Ty TNHH Sản Xuất Bao Bì Minh Đức", "Công Ty Cổ Phần Chế Biến Thực Phẩm Á Châu",
    "Công Ty TNHH MTV Khai Thác Khoáng Sản Bắc Miền", "Công Ty Cổ Phần Bất Động Sản Golden Land",
    "Công Ty TNHH Thương Mại Điện Tử SmartBuy", "Công Ty Cổ Phần Giáo Dục Edubi",
    "Công Ty TNHH Công Nghệ Phần Mềm TechViet", "Công Ty Cổ Phần Y Tế Quốc Tế Hà Nội",
    "Công Ty TNHH Thời Trang May Mặc Phương Linh", "Công Ty Cổ Phần Nội Thất Gỗ Óc Chó Hải Phòng",
    "Công Ty TNHH Vệ Sinh Môi Trường Xanh Việt", "Công Ty Cổ Phần Sửa Chữa Ô Tô Quang Minh",
    "Công Ty TNHH Tư Vấn Luật Pháp Minh Thành", "Công Ty Cổ Phần In Ấn Quảng Cáo Phú Thịnh",
    "Công Ty TNHH Kinh Doanh Bất Động Sản An Gia", "Công Ty Cổ Phần Bảo Vệ An Ninh Toàn Cầu",
    "Công Ty TNHH MTV TM-DV Phú Hưng Phát", "Công Ty Cổ Phần Xây Dựng Và Kinh Doanh Nhà Hải Yến",
    "Công Ty TNHH Đầu Tư Bất Động Sản Thăng Long 99", "Công Ty Cổ Phần Sản Xuất Nhựa Thái Bình Dương",
]

VIETNAMESE_NAMES = [
    "Nguyễn Văn Minh", "Trần Thị Lan Anh", "Lê Hoàng Nam", "Phạm Minh Đức",
    "Hoàng Thị Hương", "Đặng Văn Hùng", "Vũ Thị Mai Phương", "Bùi Quang Thắng",
    "Đỗ Thị Thu Hà", "Lý Văn Tuấn", "Trịnh Thị Ngọc Bích", "Cao Văn Sơn",
    "Phan Thị Minh Châu", "Hồ Văn Quang", "Ngô Thị Lan Hương", "Dương Văn Hải",
    "Bành Thị Thu Trang", "Đinh Văn Lâm", "Tạ Thị Hồng Nhung", "Vương Văn Hùng",
    "Lương Thị Hồng Thắm", "Chu Văn Bằng", "Hà Thị Thu Minh", "Trương Văn Kiên",
    "Đào Thị Bích Ngọc", "Lâm Văn Toàn", "Trần Thị Hồng Giang", "Nguyễn Hoàng Long",
    "Phạm Thị Lan Chi", "Đặng Văn Đức Anh", "Vũ Thị Hồng Nhung", "Bùi Văn Hùng",
    "Trần Văn Phú", "Lê Thị Thu Hằng", "Hoàng Văn Minh Tuấn", "Phạm Văn Hùng",
    "Nguyễn Thị Thanh Hà", "Trần Văn Đức", "Vũ Thị Hương Giang", "Đặng Văn Thành Công",
    "Phan Văn Thắng", "Hồ Thị Thu Hà", "Ngô Văn Quang Huy", "Dương Thị Lan Chi",
    "Bành Văn Đức Minh", "Tạ Thị Thu Hương", "Vương Văn Bảo", "Lương Thị Hồng Vân",
    "Chu Văn Minh Khoa", "Hà Văn Tuấn Kiệt", "Trương Thị Ngọc Linh",
]

CITIES = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
          "Hải Dương", "Nam Định", "Thái Bình", "Quảng Ninh", "Bắc Ninh",
          "Vĩnh Phúc", "Hưng Yên", "Hà Nam", "Ninh Bình", "Thanh Hóa",
          "Nghệ An", "Hà Tĩnh", "Quảng Bình", "Quảng Trị", "Huế"]

DISTRICTS = {
    "Hà Nội": ["Ba Đình", "Hoàn Kiếm", "Hai Bà Trưng", "Đống Đa", "Tây Hồ", "Cầu Giấy", "Thanh Xuân", "Hoàng Mai", "Long Biên", "Gia Lâm"],
    "Hồ Chí Minh": ["Quận 1", "Quận 3", "Quận 5", "Quận 7", "Quận 10", "Bình Thạnh", "Phú Nhuận", "Tân Bình", "Gò Vấp", "Thủ Đức"],
    "Đà Nẵng": ["Hải Châu", "Thanh Khê", "Sơn Trà", "Ngũ Hành Sơn", "Liên Chiểu", "Cẩm Lệ", "Hòa Vang"],
    "Hải Phòng": ["Ngô Quyền", "Lê Chân", "Hồng Bàng", "An Dương", "An Lão"],
    "Cần Thơ": ["Ninh Kiều", "Bình Thủy", "Cái Răng", "Ô Môn", "Thốt Nốt"],
}

STREETS = ["Nguyễn Trãi", "Lê Lợi", "Trần Hưng Đạo", "Lý Thường Kiệt", "Trần Phú",
           "Hai Bà Trưng", "Điện Biên Phủ", "30 Tháng 4", "Phan Đình Giót",
           "Hoàng Quốc Việt", "Cầu Giấy", "Phạm Hùng", "Xuân Thủy", "Trần Duy Hưng",
           "Tôn Đức Thắng", "Lê Đại Hành", "Bà Triệu", "Thái Hà", "La Thành"]

BANKS = ["Vietcombank", "VietinBank", "BIDV", "Agribank", "TPBank", "MB Bank", "ACB", "VPBank", "Techcombank", "SHB"]

POSITIONS_COMPANY = ["Giám đốc", "Tổng Giám đốc", "Kế toán trưởng", "Trưởng phòng Kinh doanh",
                     "Trưởng phòng Nhân sự", "Trưởng phòng Kỹ thuật", "Trưởng phòng Marketing",
                     "Trưởng phòng Hành chính", "Quản lý Chi nhánh", "Phó Giám đốc"]

POSITIONS_EMPLOYEE = ["Nhân viên Kinh doanh", "Kỹ sư phần mềm", "Nhân viên Kế toán", "Nhân viên Hành chính",
                      "Nhân viên Marketing", "Kỹ thuật viên IT", "Nhân viên Chăm sóc khách hàng",
                      "Chuyên viên Pháp chế", "Nhân viên Nhân sự", "Kế toán tổng hợp"]

PRODUCTS = [
    ("Máy tính xách tay Dell Latitude 5520, CPU i5-1135G7, RAM 8GB, SSD 256GB", "chiếc", 18500000),
    ("Máy in laser HP LaserJet Pro M404dn, tốc độ 38 trang/phút", "chiếc", 8200000),
    ("Điều hòa không khí Panasonic 12000BTU Inverter", "chiếc", 12300000),
    ("Bộ nội thất văn phòng gỗ MDF cao cấp, 6 món", "bộ", 45000000),
    ("Máy photocopy Ricoh MP 5055, đa chức năng", "chiếc", 185000000),
    ("Camera giám sát Hikvision DS-2CD1043G2, 4MP", "chiếc", 2750000),
    ("Máy chủ Dell PowerEdge R750, Xeon Gold, 64GB RAM", "bộ", 180000000),
    ("Ghế văn phòng ERGOHUMAN cao cấp, da thật", "chiếc", 8500000),
    ("Màn hình LED Samsung 32 inch UR55, 4K UHD", "chiếc", 8400000),
    ("Máy lọc nước RO Karofi 9 lõi, tự động", "chiếc", 6400000),
    ("Thiết bị mạng Cisco Catalyst 2960-X 48 port", "chiếc", 22000000),
    ("Phần mềm Microsoft 365 Business Standard, bản quyền 1 năm", "licence", 3400000),
    ("Máy tính để bàn Dell OptiPlex 7090, i7-10700, 16GB RAM", "bộ", 22000000),
    ("Máy chiếu Sony VPL-XW270, 4K HDR, laser", "chiếc", 35000000),
    ("Tủ hồ sơ Kim Tân 4 ngăn, sơn tĩnh điện", "chiếc", 3100000),
]

PROPERTY_ADDRESSES = [
    "Số 15, Ngõ 45, Đường Láng Hạ, Quận Đống Đa, Hà Nội",
    "Tầng 5, Tòa nhà ABC Tower, 123 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh",
    "Căn hộ 302, Chung cư Sunrise City, 23 Nguyễn Hữu Thọ, Quận 7, TP. HCM",
    "Số 5, Ngõ 12, Đường Cầu Giấy, Phường Dịch Vọng, Quận Cầu Giấy, Hà Nội",
    "Tầng 3, Tòa nhà Hoàng Anh, 456 Lê Duẩn, TP. Đà Nẵng",
    "Căn hộ 1205, Chung cư Green Pearl, 378 Minh Khai, Quận Hai Bà Trưng, Hà Nội",
    "Số 89, Đường Nguyễn Trãi, Phường 2, Quận 5, TP. Hồ Chí Minh",
    "Tầng 2, Tòa nhà Petro Tower, 1 Lê Lợi, TP. Hải Phòng",
    "Nhà mặt phố, Số 34 Đường Điện Biên Phủ, Quận Thanh Khê, TP. Đà Nẵng",
    "Căn hộ 505, Chung cư Grandeur, 88 Xuân Thủy, Quận Cầu Giấy, Hà Nội",
    "Số 201, Đường 3 Tháng 2, Phường 11, Quận 10, TP. Hồ Chí Minh",
    "Tầng 8, Tòa nhà Indochina Tower, 4 Nguyễn Đình Chiểu, Quận 1, TP. HCM",
]


# ==================== HELPERS ====================

def ri(a, b): return random.randint(a, b)
def rf(a, b): return round(random.uniform(a, b), 2)
def r(): return random.choice

def pick(lst): return random.choice(lst)
def pick_n(lst, n): return random.sample(lst, min(n, len(lst)))

def rdate(y1=2023, y2=2025):
    start = datetime(y1, 1, 1)
    end = datetime(y2, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def rid(): return str(ri(100000000, 999999999))
def rphone(): return f"0{ri(900000000, 999999999)}"
def remail(name):
    p = name.lower().split()
    return f"{p[0]}.{p[-1]}{ri(1,99)}@gmail.com" if len(p) >= 2 else f"{p[0]}{ri(1,99)}@gmail.com"
def rbank(): return str(ri(1000000000, 9999999999))

def num_to_words(num):
    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    tens = ["", "mười", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
    hundreds = ["", "một trăm", "hai trăm", "ba trăm", "bốn trăm", "năm trăm", "sáu trăm", "bảy trăm", "tám trăm", "chín trăm"]
    def three_digit(n):
        if n < 10: return units[n]
        elif n < 100:
            m = n % 10
            return tens[n // 10] + (" " + units[m] if m != 0 else "")
        else:
            m = n % 100
            return hundreds[n // 100] + (" " + three_digit(m) if m != 0 else "")
    if num == 0: return "không đồng"
    if num >= 1_000_000_000:
        b = num // 1_000_000_000
        rem = num % 1_000_000_000
        s = three_digit(b) + " tỷ"
        if rem >= 1_000_000: s += " " + three_digit(rem // 1_000_000) + " triệu"
        if rem % 1_000_000 >= 1000: s += " " + three_digit((rem % 1_000_000) // 1000) + " nghìn"
        if rem % 1000 != 0: s += " " + three_digit(rem % 1000)
        return s
    elif num >= 1_000_000:
        m = num // 1_000_000
        rem = num % 1_000_000
        s = three_digit(m) + " triệu"
        if rem % 1_000_000 >= 1000: s += " " + three_digit((rem % 1_000_000) // 1000) + " nghìn"
        if rem % 1000 != 0: s += " " + three_digit(rem % 1000)
        return s
    elif num >= 1000:
        t = num // 1000
        rem = num % 1000
        return three_digit(t) + " nghìn" + (" " + three_digit(rem) if rem != 0 else "")
    return three_digit(num)


# ==================== SMART FILL ENGINE ====================

def underscores(n):
    """Generate n underscores matching template patterns"""
    return "_" * n

def fill_field(text, pattern, value):
    """Replace field pattern: 'Label: ____' or 'Label: ____...___' with filled value"""
    # Try to match 'Label: ' followed by underscores
    m = re.search(re.escape(pattern) + r':\s*' + r'_+\s*', text)
    if m:
        # Replace just the label + colon + spaces + underscores
        old = m.group(0)
        # Only replace the part after the colon up to first real text
        # Actually just replace the whole match with new value
        text = text.replace(old, pattern + ": " + value, 1)
    return text

def fill_inline_field(text, label, value):
    """Replace 'Label: ______VALUE______' pattern where underscores wrap the field"""
    # Pattern: label + colon + spaces + underscores + value + underscores
    pattern = re.escape(label) + r':\s*_' + r'_([^_\n]+)' + r'_+\s*'
    m = re.search(pattern, text)
    if m:
        text = re.sub(pattern, label + ": " + value + " ", text, count=1)
    else:
        # Try simpler: label followed by multiple underscores on same line
        pattern2 = re.escape(label) + r':\s*' + r'_+\s*'
        m2 = re.search(pattern2, text)
        if m2:
            text = text.replace(m2.group(0), label + ": " + value, 1)
    return text

def fill_label_value(text, label, value):
    """Fill a 'Label: ____' or 'Label: ______' pattern with a value"""
    # Try: 'Label: ____' (label + colon + space + underscores on same line)
    p1 = re.escape(label) + r': (' + r'_+\s*)$'
    m = re.search(p1, text, re.MULTILINE)
    if m:
        text = re.sub(p1, label + ': ' + value, text, count=1, flags=re.MULTILINE)
        return text

    # Try: 'Label: ____text' (underscores then more text - strip underscores)
    p2 = re.escape(label) + r': _+\S*\s*'
    m2 = re.search(p2, text)
    if m2:
        text = text.replace(m2.group(0), label + ": " + value + " ", 1)
        return text

    # Try: 'Label: ____' anywhere (single line)
    p3 = re.escape(label) + r':\s*' + r'_\s+'
    m3 = re.search(p3, text)
    if m3:
        old = m3.group(0)
        new_val = label + ": " + value + " " + "_" * max(0, len(old) - len(label) - 2 - len(value) - 1)
        text = text.replace(old, new_val, 1)
        return text

    return text

def strip_underscores_after(text, label, replacement):
    """After replacing a label, remove trailing underscores on the same line"""
    # Find the replacement we just made and clean up remaining underscores after value
    pattern = re.escape(label) + r':\s*' + re.escape(replacement) + r'\s*' + r'_+\s*'
    m = re.search(pattern, text)
    if m:
        text = text[:m.end()] + "\n" + text[m.end():]
        text = text.replace(m.group(0), label + ": " + replacement)
    return text

def fill_doc_date(text, d):
    """Fill date placeholders"""
    date_str = d.strftime("%d/%m/%Y")
    date_full = f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}"
    text = re.sub(r'Ngày \.\.\. tháng \.\.\. năm \.\.\.\.\.\.\.\.', date_full, text)
    text = re.sub(r'Ngày \.\.\./\.\.\./\.\.\.\.\.\.\.\.', date_str, text)
    text = re.sub(r'\.\.\./\.\.\./\.\.\.\.\.\.\.\.', date_str, text)
    text = re.sub(r'\.\.\.\./\.\.\.\./\.\.\.\.\.\.\.\.', date_str, text)
    text = re.sub(r'\.\.\./\.\.\./\.\.\.\.\.\.\.\.', date_str, text)
    return text


# ==================== CONTRACT FILLERS ====================

def fill_t1(template, idx):
    d = rdate(2023, 2025)
    cn = f"HĐMB-{ri(100,999)}/HĐMB-{d.year}"
    city = pick(CITIES)
    dist = pick(DISTRICTS.get(city, ["Quận 1"]))
    street = pick(STREETS)

    seller = pick([c for c in COMPANY_NAMES])
    buyer = pick([c for c in COMPANY_NAMES if c != seller])
    rep_s = pick(VIETNAMESE_NAMES)
    rep_b = pick([n for n in VIETNAMESE_NAMES if n != rep_s])
    pos_s = pick(POSITIONS_COMPANY)
    pos_b = pick(POSITIONS_COMPANY)
    bank = pick(BANKS)

    product, unit, price = pick(PRODUCTS)
    qty = ri(5, 200)
    total = price * qty
    delivery_days = ri(7, 60)
    warranty = ri(6, 36)
    late_pct = rf(0.05, 0.15)
    late_cap = rf(0.08, 0.20)

    pay_methods = [
        f"Chuyển khoản trước {ri(20,50)}% giá trị đơn hàng, {100-ri(20,50)}% còn lại thanh toán sau khi nhận hàng trong vòng 07 ngày làm việc.",
        "Thanh toán 100% bằng chuyển khoản ngay khi nhận hàng trong vòng 05 ngày làm việc.",
        f"Thanh toán theo từng đợt: Đợt 1: {ri(30,50)}% ngay khi ký hợp đồng; Đợt 2: {ri(30,50)}% sau khi giao hàng; Đợt 3: Phần còn lại trong 07 ngày sau nghiệm thu."
    ]

    text = template

    # Contract number and date
    text = re.sub(r'Số:?\s*_+/HĐMB-2026', f"Số: {cn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tại\s*_+', f"Tại {city}", text)

    # Seller block (first occurrence)
    text = re.sub(r'BÊN BÁN:?\s*_+', f"BÊN BÁN: {seller}", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Mã số thuế:?\s*_+\s*\n', f"Mã số thuế: {rid()}\n", text, count=1)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep_s}\n", text, count=1)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: {pos_s}\n", text, count=1)
    text = re.sub(r'Số tài khoản:?\s*_+\s*\n', f"Số tài khoản: {rbank()}\n", text, count=1)

    # Buyer block (second occurrence)
    text = re.sub(r'BÊN MUA:?\s*_+', f"BÊN MUA: {buyer}", text, count=1)
    # For buyer address, find the line after "BÊN MUA"
    m = re.search(r'BÊN MUA:' + re.escape(buyer) + r'\n(Địa chỉ:?\s*_+)\s*\n', text)
    if m:
        text = text.replace(m.group(1), f"Địa chỉ: Số {ri(1,299)}, {street}, {dist}, {city}")
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Mã số thuế:?\s*_+\s*\n', f"Mã số thuế: {rid()}\n", text, count=1)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep_b}\n", text, count=1)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: {pos_b}\n", text, count=1)
    text = re.sub(r'Số tài khoản:?\s*_+\s*\n', f"Số tài khoản: {rbank()}\n", text, count=1)

    # Product section
    text = re.sub(r'Tên hàng hóa:?\s*_+', f"Tên hàng hóa: {product}", text)
    text = re.sub(r'Quy cách, chủng loại:?\s*_+', "Quy cách, chủng loại: Theo tiêu chuẩn nhà sản xuất", text)
    text = re.sub(r'Số lượng:?\s*_+\s*\([^)]+\)', f"Số lượng: {qty} ({unit})", text)
    text = re.sub(r'Đơn giá:?\s*_+\s*VNĐ\s*\([^)]+\)', f"Đơn giá: {price:,.0f} VNĐ (Bằng chữ: {num_to_words(price)})", text)
    text = re.sub(r'Tổng giá trị hợp đồng:?\s*_+\s*VNĐ', f"Tổng giá trị hợp đồng: {total:,.0f} VNĐ", text)
    m = re.search(r'\(Bằng chữ:?\s*_+\)', text)
    if m:
        text = text.replace(m.group(0), f"(Bằng chữ: {num_to_words(total)} đồng)", 1)

    # Payment
    text = re.sub(r'Phương thức thanh toán:\s*\[[\s\S]*?\]', f"Phương thức thanh toán: {pick(pay_methods)}", text)
    text = re.sub(r'Thanh toán trong vòng\s*_\s*ngày', "Thanh toán trong vòng 07 ngày", text)
    text = re.sub(r'Thanh toán bằng:.*', "Thanh toán bằng: [x] Chuyển khoản / [ ] Tiền mặt", text)
    text = re.sub(r'Ngân hàng:?\s*_+\s*\n', f"Ngân hàng: {bank}\n", text)
    text = re.sub(r'Ngân hàng:?\s*_+\s*\n', f"Ngân hàng: {pick(BANKS)}\n", text)
    text = re.sub(r'Chủ tài khoản:?\s*_+\s*\n', f"Chủ tài khoản: {rep_s}\n", text, count=1)

    # Delivery
    text = re.sub(r'Thời gian giao hàng:?\s*Trong vòng\s*_\s*ngày', f"Thời gian giao hàng: Trong vòng {delivery_days} ngày", text)
    text = re.sub(r'Địa điểm giao hàng:?\s*_+', f"Địa điểm giao hàng: Tại {pick([city, 'Kho hàng Bên Bán', f'Địa chỉ Bên Mua'])}", text)
    text = re.sub(r'Chi phí vận chuyển:?\s*\[[\s\S]*?\]', "Chi phí vận chuyển: [x] Do Bên Bán chịu / [ ] Do Bên Mua chịu", text)
    text = re.sub(r'Bên mua tiến hành nghiệm thu trong vòng\s*_\s*ngày', f"Bên mua tiến hành nghiệm thu trong vòng {ri(3,7)} ngày", text)

    # Warranty
    text = re.sub(r'Bên bán bảo hành hàng hóa trong thời hạn\s*_\s*tháng', f"Bên bán bảo hành hàng hóa trong thời hạn {warranty} tháng", text)
    text = re.sub(r'kể từ ngày nghiệm thu\.\s*Bên bán có trách nhiệm', "kể từ ngày nghiệm thu. Bên bán có trách nhiệm", text)

    # Penalties
    text = re.sub(r'bằng\s*_%/ngày', f"bằng {late_pct*100:.0f}%/ngày", text)
    text = re.sub(r'\(tối đa\s*_%', f"(tối đa {late_cap*100:.0f}%", text)
    text = re.sub(r'nhưng không quá\s*_%', f"nhưng không quá {late_cap*100:.0f}%", text)
    text = re.sub(r'mà không khắc phục trong vòng\s*_\s*ngày', f"mà không khắc phục trong vòng {ri(15,30)} ngày", text)
    text = re.sub(r'trọng tài trong vòng\s*_\s*ngày', f"trọng tài trong vòng {ri(15,30)} ngày", text)

    # Confidentiality
    text = re.sub(r'trong thời hạn\s*_\s*năm', f"trong thời hạn {ri(2,5)} năm", text)
    text = re.sub(r'mà không có sự đồng ý của bên kia', "mà không có sự đồng ý của bên kia", text)

    # Footer signature dates
    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}   ", text)

    # Signature blocks
    text = re.sub(r'BÊN BÁN\s*\(ký, ghi rõ họ tên\)', f"BÊN BÁN (ký, ghi rõ họ tên)\n{rep_s}", text, count=1)
    text = re.sub(r'BÊN MUA\s*\(ký, ghi rõ họ tên\)', f"BÊN MUA (ký, ghi rõ họ tên)\n{rep_b}", text, count=1)
    text = re.sub(r'Họ tên:\s*_\s*', f"Họ tên: {rep_s}   ", text)
    text = re.sub(r'Họ tên:\s*_\s*', f"Họ tên: {rep_b}   ", text)

    return {
        "id": f"hop_dong_mua_ban_hang_hoa_{idx:05d}",
        "template_id": "t1",
        "contract_type": "Hợp đồng mua bán hàng hóa",
        "contract_no": cn, "date": d.strftime("%d/%m/%Y"),
        "seller": seller, "buyer": buyer,
        "product": product, "quantity": qty, "unit": unit,
        "unit_price": price, "total_price": total,
        "delivery_days": delivery_days, "warranty_months": warranty,
        "risk_level": pick(["low", "medium", "high"]),
        "has_violation": random.random() < 0.25,
        "text": text,
    }


def fill_t2(template, idx):
    """Hợp đồng lao động"""
    d = rdate(2023, 2024)
    cn = f"HĐLĐ-{ri(100,999)}/HĐLĐ-{d.year}"
    city = pick(CITIES)
    dist = pick(DISTRICTS.get(city, ["Quận 1"]))
    street = pick(STREETS)

    company = pick(COMPANY_NAMES)
    rep = pick(VIETNAMESE_NAMES)
    emp = pick(VIETNAMESE_NAMES)
    pos = pick(POSITIONS_EMPLOYEE)
    dept = pick(["Phòng Kinh doanh", "Phòng Nhân sự", "Phòng Kỹ thuật", "Phòng Marketing", "Phòng Tài chính - Kế toán", "Phòng Hành chính"])

    ctypes = ["Thử việc", "Có thời hạn dưới 12 tháng", "Có thời hạn từ 12 tháng trở lên", "Không xác định thời hạn"]
    ctype = pick(ctypes)
    dur = ri(1, 2) if ctype == "Thử việc" else (ri(3, 11) if "dưới 12" in ctype else ri(12, 60))
    salaries = [8500000, 12000000, 18000000, 25000000, 35000000, 50000000, 80000000, 120000000, 150000000]
    salary = pick(salaries)
    income_tax = int(salary * 0.1)
    shi = int(salary * 0.08)
    hi = int(salary * 0.015)
    ui = int(salary * 0.01)
    notice = 24 if ctype == "Thử việc" else (30 if dur < 12 else 45)

    work_hours = pick([
        "Từ 08 giờ 00 phút đến 17 giờ 00 phút, từ thứ 2 đến thứ 6 hàng tuần.",
        "Từ 08 giờ 30 phút đến 17 giờ 30 phút, từ thứ 2 đến thứ 7 hàng tuần.",
        "Ca sáng: 06 giờ 00 phút đến 14 giờ 00 phút; Ca chiều: 14 giờ 00 phút đến 22 giờ 00 phút, luân phiên."
    ])
    schedule = pick(["Toàn thời gian", "Bán thời gian", "Theo ca"])

    text = template
    text = re.sub(r'Số:?\s*_+/HĐLĐ-2026', f"Số: {cn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tên Doanh Nghiệp:?\s*_+\s*\n', f"Tên Doanh Nghiệp: {company}\n", text)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {dist}, {city}\n", text)
    text = re.sub(r'Mã số thuế:?\s*_+\s*\n', f"Mã số thuế: {rid()}\n", text)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep}\n", text)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: Giám đốc\n", text)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text)

    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {emp}\n", text)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1975,2002).strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text)
    text = re.sub(r'Ngày cấp:?\s*_+\s*\n', f"Ngày cấp: {rdate(2015,2022).strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Nơi cấp:?\s*_+\s*\n', f"Nơi cấp: {pick(CITIES)}\n", text)
    text = re.sub(r'Địa chỉ thường trú:?\s*_+\s*\n', f"Địa chỉ thường trú: Số {ri(1,99)}, {street}, {dist}, {city}\n", text)
    text = re.sub(r'Số điện thoại:?\s*_+\s*\n', f"Số điện thoại: {rphone()}\n", text)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: {remail(emp)}\n", text)
    text = re.sub(r'Số TK:?\s*_+\s*\n', f"Số TK: {rbank()}\n", text)
    text = re.sub(r'Tại Ngân hàng:?\s*_+\s*\n', f"Tại Ngân hàng: {pick(BANKS)}\n", text)

    text = re.sub(r'Vị trí:?\s*_+\s*\n', f"Vị trí: {pos}\n", text)
    text = re.sub(r'Phòng ban:?\s*_+\s*\n', f"Phòng ban: {dept}\n", text)
    text = re.sub(r'Địa điểm làm việc:?\s*_+\s*\n', f"Địa điểm làm việc: {city}\n", text)
    text = re.sub(r'Thời gian làm việc theo:?\s*_+\s*\n', f"Thời gian làm việc theo: {schedule}\n", text)
    text = re.sub(r'Từ\s*_\s*giờ\s*_\s*phút\s*đến\s*_\s*giờ\s*_\s*phút', work_hours, text)

    text = re.sub(r'Loại hợp đồng:?\s*_+\s*\n', f"Loại hợp đồng: {ctype}\n", text)
    text = re.sub(r'Thời hạn:?\s*_+\s*\n', f"Thời hạn: {dur} tháng\n", text)
    text = re.sub(r'Từ ngày:?\s*_+\s*\n', f"Từ ngày: {d.strftime('%d/%m/%Y')}\n", text)
    end_d = (d + timedelta(days=dur * 30)).strftime("%d/%m/%Y") if ctype != "Không xác định thời hạn" else "Không xác định"
    text = re.sub(r'Đến ngày:?\s*_+\s*\n', f"Đến ngày: {end_d}\n", text)

    text = re.sub(r'Mức lương:?\s*_+\s*\(VNĐ\)', f"Mức lương: {salary:,.0f} (VNĐ)", text)
    m = re.search(r'\(Bằng chữ:?\s*_+\)', text)
    if m:
        text = text.replace(m.group(0), f"(Bằng chữ: {num_to_words(salary)} đồng)", 1)
    text = re.sub(r'Thuế TNCN \(10%\):?\s*_+\s*\n', f"Thuế TNCN (10%): {income_tax:,.0f} VNĐ\n", text)
    text = re.sub(r'Bảo hiểm xã hội \(8%\):?\s*_+\s*\n', f"Bảo hiểm xã hội (8%): {shi:,.0f} VNĐ\n", text)
    text = re.sub(r'Bảo hiểm y tế \(1,5%\):?\s*_+\s*\n', f"Bảo hiểm y tế (1,5%): {hi:,.0f} VNĐ\n", text)
    text = re.sub(r'Bảo hiểm thất nghiệp \(1%\):?\s*_+\s*\n', f"Bảo hiểm thất nghiệp (1%): {ui:,.0f} VNĐ\n", text)
    text = re.sub(r'Thanh toán vào ngày mồng\s*_\s*', f"Thanh toán vào ngày mồng {ri(5,15)}", text)
    text = re.sub(r'Phương thức thanh toán:?\s*_+\s*\n', "Phương thức thanh toán: Chuyển khoản ngân hàng\n", text)

    if random.random() > 0.5:
        text = re.sub(r'Làm thêm giờ:?\s*Có/Không', "Làm thêm giờ: Có", text)
        text = re.sub(r'Được thu xếp\s*_\s*%', f"Được thu xếp {ri(150,200)}%", text)
    else:
        text = re.sub(r'Làm thêm giờ:?\s*Có/Không', "Làm thêm giờ: Không", text)

    if ri(0, 1):
        text = re.sub(r'Phụ cấp tiền ăn:?\s*_+\s*\n', f"Phụ cấp tiền ăn: {ri(300,1500)*1000:,.0f} VNĐ/tháng\n", text)
    if random.random() > 0.5:
        text = re.sub(r'Phụ cấp xăng xe:?\s*_+\s*\n', f"Phụ cấp xăng xe: {ri(500,2000)*1000:,.0f} VNĐ/tháng\n", text)
    if random.random() > 0.5:
        text = re.sub(r'Phụ cấp điện thoại:?\s*_+\s*\n', f"Phụ cấp điện thoại: {ri(200,800)*1000:,.0f} VNĐ/tháng\n", text)

    text = re.sub(r'Số ngày nghỉ hàng năm:?\s*_+\s*\n', f"Số ngày nghỉ hàng năm: {pick([12,14,15,18,20])} ngày\n", text)
    text = re.sub(r'Lý do:?\s*_+\s*\n', "Lý do: Theo thỏa thuận giữa hai bên\n", text)

    if ctype == "Thử việc":
        text = re.sub(r'Mức lương thử việc:?\s*_+\s*\(VNĐ\)', f"Mức lương thử việc: {int(salary*0.85):,.0f} (VNĐ)", text)
        text = re.sub(r'Thời gian thử việc:?\s*_\s*tháng', f"Thời gian thử việc: {ri(1,2)} tháng", text)

    text = re.sub(r'Thông báo trước:?\s*_\s*ngày', f"Thông báo trước: {notice} ngày", text)
    text = re.sub(r'Bồi thường:?\s*_+\s*\n', f"Bồi thường: {ri(1,2)} tháng lương nếu vi phạm thời hạn báo trước\n", text)

    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}  ", text)

    return {
        "id": f"hop_dong_lao_dong_{idx:05d}",
        "template_id": "t2",
        "contract_type": "Hợp đồng lao động",
        "contract_no": cn, "date": d.strftime("%d/%m/%Y"),
        "company": company, "employee": emp, "position": pos,
        "salary": salary, "contract_type": ctype, "duration_months": dur,
        "risk_level": pick(["low", "medium", "high"]),
        "has_violation": random.random() < 0.25,
        "text": text,
    }


def fill_t3(template, idx):
    """Thỏa thuận bảo mật NDA"""
    d = rdate()
    cn = f"NDA-{ri(100,999)}/NDA-{d.year}"
    city = pick(CITIES)
    dist = pick(DISTRICTS.get(city, ["Quận 1"]))
    street = pick(STREETS)

    parties = pick_n(COMPANY_NAMES, 2)
    pa_name = parties[0]
    pb_name = parties[1]
    rep_a = pick(VIETNAMESE_NAMES)
    rep_b = pick([n for n in VIETNAMESE_NAMES if n != rep_a])

    purposes = [
        "đàm phán và thảo luận về khả năng hợp tác kinh doanh giữa hai bên",
        "chia sẻ thông tin công nghệ, bí quyết kỹ thuật và giải pháp phần mềm",
        "đánh giá tính khả thi của dự án đầu tư chung",
        "trao đổi thông tin kỹ thuật, thương mại và tài chính liên quan đến hợp tác",
        "phát triển và nghiên cứu sản phẩm công nghệ chung"
    ]
    purpose = pick(purposes)
    confidential_years = ri(2, 5)
    penalty = ri(5, 20) * 10000000

    conf_types = pick_n([
        "chiến lược kinh doanh và kế hoạch phát triển dài hạn của Công ty",
        "danh sách khách hàng, nhà cung cấp và đối tác chiến lược",
        "báo cáo tài chính, doanh thu, lợi nhuận và các chỉ số kinh doanh",
        "mã nguồn phần mềm, công nghệ độc quyền và bí quyết kỹ thuật",
        "bản vẽ thiết kế kỹ thuật, quy trình sản xuất và công thức sản phẩm",
        "hợp đồng, thỏa thuận với bên thứ ba chưa công bố",
        "thông tin về tranh chấp pháp lý và các vấn đề pháp chế",
        "kế hoạch mở rộng, sáp nhập và mua bán doanh nghiệp",
        "bí quyết thương mại, mô hình pricing và chiến lược marketing"
    ], ri(4, 6))

    text = template
    text = re.sub(r'Số:?\s*_+/NDA-2026', f"Số: {cn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tại\s*_+', f"Tại {city}", text)

    # Party A
    text = re.sub(r'Tên Doanh Nghiệp/ Cá Nhân:?\s*_+\s*\n', f"Tên Doanh Nghiệp/ Cá Nhân: {pa_name}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep_a}\n", text, count=1)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: {pick(POSITIONS_COMPANY)}\n", text, count=1)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: contact@{pa_name.lower().replace(' ','')}.com\n", text, count=1)

    # Party B
    text = re.sub(r'Tên Doanh Nghiệp/ Cá Nhân:?\s*_+\s*\n', f"Tên Doanh Nghiệp/ Cá Nhân: {pb_name}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep_b}\n", text, count=1)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: {pick(POSITIONS_COMPANY)}\n", text, count=1)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: contact@{pb_name.lower().replace(' ','')}.com\n", text, count=1)

    # Purpose
    text = re.sub(r'Mục đích:?\s*_+', f"Mục đích: {purpose}", text)
    text = re.sub(r'mục đích:?\s*_+', f"mục đích: {purpose}", text)

    # Confidential info types
    for i, ct in enumerate(conf_types):
        text = re.sub(r'\(\d+\)\s*_+', f"({i+1}) {ct}", text, count=1)

    # Duration and penalties
    text = re.sub(r'Thời hạn bảo mật:?\s*\(\s*_\s*năm\s*\)', f"Thời hạn bảo mật: ({confidential_years} năm)", text)
    text = re.sub(r'\(\s*_\s*năm sau khi chấm dứt HĐ\)', f"({ri(1,3)} năm sau khi chấm dứt HĐ)", text)
    text = re.sub(r'Mức phạt:?\s*_+\s*\n', f"Mức phạt: {penalty:,.0f} VNĐ cho mỗi lần vi phạm\n", text)
    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}  ", text)

    return {
        "id": f"thoa_thuan_bao_mat_nda_{idx:05d}",
        "template_id": "t3",
        "contract_type": "Thỏa thuận bảo mật (NDA)",
        "contract_no": cn, "date": d.strftime("%d/%m/%Y"),
        "party_a": pa_name, "party_b": pb_name,
        "purpose": purpose,
        "confidential_period_years": confidential_years,
        "risk_level": pick(["low", "medium"]),
        "has_violation": random.random() < 0.15,
        "text": text,
    }


def fill_t4(template, idx):
    """Hợp đồng thuê nhà ở"""
    d = rdate()
    cn = f"HĐTN-{ri(100,999)}/HĐTN-{d.year}"
    lessor = pick(VIETNAMESE_NAMES)
    tenant = pick([n for n in VIETNAMESE_NAMES if n != lessor])
    prop_addr = pick(PROPERTY_ADDRESSES)
    city = pick(CITIES)
    if city not in DISTRICTS:
        city = "Hà Nội"
    dist = pick(DISTRICTS.get(city, ["Quận 1"]))
    street = pick(STREETS)

    area = ri(25, 300)
    floors = ri(1, 5)
    bedrooms = ri(1, 4)
    bathrooms = ri(1, 3)
    rent = ri(3, 50) * 1000000
    deposit = rent * ri(1, 3)
    duration = ri(6, 36)
    prop_type = pick(["Nhà ở riêng lẻ", "Căn hộ chung cư", "Phòng trọ có WC riêng"])

    text = template
    text = re.sub(r'Số:?\s*_+/HĐTN-2026', f"Số: {cn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tại\s*Địa\s*điểm', f"Tại {city}", text)

    # Lessor
    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {lessor}\n", text, count=1)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1960,1985).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text, count=1)
    text = re.sub(r'Ngày cấp:?\s*_+\s*\n', f"Ngày cấp: {rdate(2015,2022).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Nơi cấp:?\s*_+\s*\n', f"Nơi cấp: {pick(CITIES)}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,99)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Số điện thoại:?\s*_+\s*\n', f"Số điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: {remail(lessor)}\n", text, count=1)

    # Tenant
    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {tenant}\n", text, count=1)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1980,2000).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,99)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Số điện thoại:?\s*_+\s*\n', f"Số điện thoại: {rphone()}\n", text, count=1)

    # Property
    text = re.sub(r'Loại tài sản:?\s*_+\s*\n', f"Loại tài sản: {prop_type}\n", text)
    text = re.sub(r'Địa chỉ tài sản:?\s*_+', f"Địa chỉ tài sản: {prop_addr}", text)
    text = re.sub(r'Diện tích:?\s*_\s*m²', f"Diện tích: {area} m²", text)
    text = re.sub(r'Số tầng:?\s*_\s*\n', f"Số tầng: {floors}\n", text)
    text = re.sub(r'Phòng ngủ:?\s*_\s*\n', f"Phòng ngủ: {bedrooms}\n", text)
    text = re.sub(r'Nhà bếp:?\s*_\s*\n', f"Nhà bếp: {ri(1,2)}\n", text)
    text = re.sub(r'Nhà vệ sinh:?\s*_\s*\n', f"Nhà vệ sinh: {bathrooms}\n", text)

    # Lease
    text = re.sub(r'Thời hạn:?\s*_\s*tháng', f"Thời hạn: {duration} tháng", text)
    text = re.sub(r'Từ ngày:?\s*_+\s*\n', f"Từ ngày: {d.strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Đến ngày:?\s*_+\s*\n', f"Đến ngày: {(d + timedelta(days=duration*30)).strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Tiền thuê:?\s*_+\s*\(VNĐ\)', f"Tiền thuê: {rent:,.0f} (VNĐ)", text)
    m = re.search(r'\(Bằng chữ:?\s*_+\)', text)
    if m:
        text = text.replace(m.group(0), f"(Bằng chữ: {num_to_words(rent)} đồng)", 1)
    text = re.sub(r'Thanh toán vào ngày mồng\s*_\s*', f"Thanh toán vào ngày mồng {ri(1,5)}", text)
    text = re.sub(r'Phương thức:?\s*_+\s*\n', f"Phương thức: {pick(['Tiền mặt', 'Chuyển khoản ngân hàng'])}\n", text)
    text = re.sub(r'Đặt cọc:?\s*_+\s*\(Bằng chữ:?\s*_+\)', f"Đặt cọc: {deposit:,.0f} VNĐ (Bằng chữ: {num_to_words(deposit)} đồng)", text)

    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}  ", text)

    return {
        "id": f"hop_dong_thue_nha_o_{idx:05d}",
        "template_id": "t4",
        "contract_type": "Hợp đồng thuê nhà ở",
        "contract_no": cn, "date": d.strftime("%d/%m/%Y"),
        "lessor": lessor, "tenant": tenant,
        "property_address": prop_addr,
        "area": area, "monthly_rent": rent, "deposit": deposit, "duration_months": duration,
        "risk_level": pick(["low", "medium", "high"]),
        "has_violation": random.random() < 0.25,
        "text": text,
    }


def fill_t5(template, idx):
    """Hợp đồng cung cấp dịch vụ"""
    d = rdate()
    cn = f"HĐDV-{ri(100,999)}/HĐDV-{d.year}"
    city = pick(CITIES)
    dist = pick(DISTRICTS.get(city, ["Quận 1"]))
    street = pick(STREETS)

    client = pick(COMPANY_NAMES)
    provider = pick([c for c in COMPANY_NAMES if c != client])
    rep_c = pick(VIETNAMESE_NAMES)
    rep_p = pick([n for n in VIETNAMESE_NAMES if n != rep_c])

    services = [
        "Dịch vụ tư vấn pháp lý doanh nghiệp", "Dịch vụ thiết kế đồ họa và xây dựng thương hiệu",
        "Dịch vụ bảo vệ an ninh và tuần tra", "Dịch vụ vệ sinh công nghiệp chuyên nghiệp",
        "Dịch vụ kế toán thuế và tư vấn tài chính", "Dịch vụ nhân sự và tuyển dụng chuyên nghiệp",
        "Dịch vụ logistics và vận chuyển hàng hóa", "Dịch vụ bảo trì và sửa chữa hệ thống máy tính",
        "Dịch vụ thiết kế và phát triển website", "Dịch vụ truyền thông marketing tổng thể",
    ]
    service = pick(services)
    total = ri(2, 200) * 10000000
    vat = int(total * 0.1)
    gross = total + vat
    days = ri(30, 180)
    warranty = ri(3, 12)

    text = template
    text = re.sub(r'Số:?\s*_+/HĐDV-2026', f"Số: {cn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tại\s*Địa\s*điểm', f"Tại {city}", text)

    text = re.sub(r'Tên Doanh Nghiệp:?\s*_+\s*\n', f"Tên Doanh Nghiệp: {client}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Mã số thuế:?\s*_+\s*\n', f"Mã số thuế: {rid()}\n", text, count=1)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep_c}\n", text, count=1)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: Giám đốc\n", text, count=1)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: contact@{client.lower().replace(' ','')}.com\n", text, count=1)

    text = re.sub(r'Tên Doanh Nghiệp:?\s*_+\s*\n', f"Tên Doanh Nghiệp: {provider}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Mã số thuế:?\s*_+\s*\n', f"Mã số thuế: {rid()}\n", text, count=1)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep_p}\n", text, count=1)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: Giám đốc\n", text, count=1)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: contact@{provider.lower().replace(' ','')}.com\n", text, count=1)

    text = re.sub(r'Dịch vụ:?\s*_+', f"Dịch vụ: {service}", text)
    text = re.sub(r'Tổng giá trị dịch vụ:?\s*_+\s*\(VNĐ\)', f"Tổng giá trị dịch vụ: {total:,.0f} (VNĐ)", text)
    m = re.search(r'\(Bằng chữ:?\s*_+\)', text)
    if m:
        text = text.replace(m.group(0), f"(Bằng chữ: {num_to_words(total)} đồng)", 1)
    text = re.sub(r'Thuế VAT \(10%\):?\s*_+\s*\n', f"Thuế VAT (10%): {vat:,.0f} VNĐ\n", text)
    text = re.sub(r'Tổng cộng \(đã bao gồm VAT\):?\s*_+\s*\n', f"Tổng cộng (đã bao gồm VAT): {gross:,.0f} VNĐ\n", text)
    text = re.sub(r'Thời gian bắt đầu:?\s*_+\s*\n', f"Thời gian bắt đầu: {d.strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Thời gian kết thúc:?\s*_+\s*\n', f"Thời gian kết thúc: {(d+timedelta(days=days)).strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Tổng số ngày thực hiện:?\s*_\s*ngày', f"Tổng số ngày thực hiện: {days} ngày", text)
    text = re.sub(r'Thanh toán trong vòng\s*_\s*ngày', f"Thanh toán trong vòng {ri(7,30)} ngày", text)
    text = re.sub(r'Ngân hàng:?\s*_+\s*\n', f"Ngân hàng: {pick(BANKS)}\n", text, count=1)
    text = re.sub(r'STK:?\s*_+\s*\n', f"STK: {rbank()}\n", text, count=1)
    text = re.sub(r'Thời gian bảo hành:?\s*_\s*tháng', f"Thời gian bảo hành: {warranty} tháng", text)

    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}  ", text)

    return {
        "id": f"hop_dong_cung_cap_dich_vu_{idx:05d}",
        "template_id": "t5",
        "contract_type": "Hợp đồng cung cấp dịch vụ",
        "contract_no": cn, "date": d.strftime("%d/%m/%Y"),
        "client": client, "provider": provider,
        "service": service, "total_value": total,
        "warranty_months": warranty, "project_days": days,
        "risk_level": pick(["low", "medium", "high"]),
        "has_violation": random.random() < 0.25,
        "text": text,
    }


def fill_t6(template, idx):
    """Hợp đồng giao khoán"""
    d = rdate()
    cn = f"HĐGK-{ri(100,999)}/HĐGK-{d.year}"
    city = pick(CITIES)
    dist = pick(DISTRICTS.get(city, ["Quận 1"]))
    street = pick(STREETS)

    assignor = pick(COMPANY_NAMES)
    contractor = pick(VIETNAMESE_NAMES)
    rep = pick(VIETNAMESE_NAMES)

    works = pick([
        "In ấn và gia công các loại biểu mẫu văn phòng", "Sản xuất và đóng gói sản phẩm theo mẫu",
        "May mặc và gia công thời trang theo thiết kế", "Lắp ráp linh kiện điện tử và bo mạch",
        "Gia công cơ khí chính xác các chi tiết máy", "Sản xuất bao bì carton các loại",
        "Gia công nội thất gỗ theo bản vẽ thiết kế", "In ấn và gia công sản phẩm quảng cáo"
    ])
    total = ri(1, 50) * 10000000
    vat = int(total * 0.1)
    work_days = ri(15, 90)
    accept_days = ri(3, 7)

    text = template
    text = re.sub(r'Số:?\s*_+/HĐGK-2026', f"Số: {cn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tại\s*Địa\s*điểm', f"Tại {city}", text)

    text = re.sub(r'Tên Doanh Nghiệp:?\s*_+\s*\n', f"Tên Doanh Nghiệp: {assignor}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Mã số thuế:?\s*_+\s*\n', f"Mã số thuế: {rid()}\n", text, count=1)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep}\n", text, count=1)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: {pick(POSITIONS_COMPANY)}\n", text, count=1)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: contact@{assignor.lower().replace(' ','')}.com\n", text, count=1)

    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {contractor}\n", text, count=1)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1975,2000).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text, count=1)
    text = re.sub(r'Ngày cấp:?\s*_+\s*\n', f"Ngày cấp: {rdate(2015,2022).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Nơi cấp:?\s*_+\s*\n', f"Nơi cấp: {pick(CITIES)}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,99)}, {street}, {dist}, {city}\n", text, count=1)
    text = re.sub(r'Số TK:?\s*_+\s*\n', f"Số TK: {rbank()}\n", text, count=1)
    text = re.sub(r'Tại Ngân hàng:?\s*_+\s*\n', f"Tại Ngân hàng: {pick(BANKS)}\n", text, count=1)

    text = re.sub(r'Công việc:?\s*_+', f"Công việc: {works}", text)
    text = re.sub(r'Tổng giá trị giao khoán:?\s*_+\s*\(VNĐ\)', f"Tổng giá trị giao khoán: {total:,.0f} (VNĐ)", text)
    m = re.search(r'\(Bằng chữ:?\s*_+\)', text)
    if m:
        text = text.replace(m.group(0), f"(Bằng chữ: {num_to_words(total)} đồng)", 1)
    text = re.sub(r'Thuế VAT \(10%\):?\s*_+\s*\n', f"Thuế VAT (10%): {vat:,.0f} VNĐ\n", text)
    text = re.sub(r'Tổng cộng \(đã bao gồm VAT\):?\s*_+\s*\n', f"Tổng cộng (đã bao gồm VAT): {total+vat:,.0f} VNĐ\n", text)
    text = re.sub(r'Thời gian bắt đầu:?\s*_+\s*\n', f"Thời gian bắt đầu: {d.strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Thời gian kết thúc:?\s*_+\s*\n', f"Thời gian kết thúc: {(d+timedelta(days=work_days)).strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Tổng số ngày thực hiện:?\s*_\s*ngày', f"Tổng số ngày thực hiện: {work_days} ngày", text)
    text = re.sub(r'Nghiệm thu trong vòng\s*_\s*ngày', f"Nghiệm thu trong vòng {accept_days} ngày", text)
    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}  ", text)

    return {
        "id": f"hop_dong_giao_khoan_{idx:05d}",
        "template_id": "t6",
        "contract_type": "Hợp đồng giao khoán",
        "contract_no": cn, "date": d.strftime("%d/%m/%Y"),
        "assignor": assignor, "contractor": contractor,
        "work_type": works, "total_value": total, "work_days": work_days,
        "risk_level": pick(["low", "medium", "high"]),
        "has_violation": random.random() < 0.25,
        "text": text,
    }


def fill_t7(template, idx):
    """Quy chế nội bộ công ty"""
    d = rdate()
    dn = f"QĐ-{ri(100,999)}/2026-QCPX"
    city = pick(CITIES)
    street = pick(STREETS)
    company = pick(COMPANY_NAMES)
    rep = pick(VIETNAMESE_NAMES)

    depts = pick_n([
        ("Phòng Kinh doanh", ri(3, 15), pick(VIETNAMESE_NAMES)),
        ("Phòng Nhân sự", ri(2, 8), pick(VIETNAMESE_NAMES)),
        ("Phòng Kỹ thuật / IT", ri(3, 10), pick(VIETNAMESE_NAMES)),
        ("Phòng Marketing", ri(2, 8), pick(VIETNAMESE_NAMES)),
        ("Phòng Tài chính - Kế toán", ri(3, 10), pick(VIETNAMESE_NAMES)),
        ("Phòng Hành chính - Văn thư", ri(2, 6), pick(VIETNAMESE_NAMES)),
        ("Phòng Sản xuất", ri(5, 20), pick(VIETNAMESE_NAMES)),
        ("Phòng Pháp chế", ri(1, 4), pick(VIETNAMESE_NAMES)),
    ], ri(4, 7))

    text = template
    text = re.sub(r'Số:?\s*QĐ-_\+/2026-QCPX', f"Số: {dn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tên Công Ty:?\s*_+\s*\n', f"Tên Công Ty: {company}\n", text)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {pick(DISTRICTS.get(city,['Quận 1']))}, {city}\n", text)
    text = re.sub(r'GP-ĐKHD số:?\s*_+\s*\n', f"GP-ĐKHD số: {rid()}\n", text)
    text = re.sub(r'Ngày:?\s*_+\s*\n', f"Ngày: {rdate(2018,2023).strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: info@{company.lower().replace(' ','')}.com\n", text)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep}\n", text)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: Giám đốc\n", text)

    for i, (dname, cnt, dhead) in enumerate(depts):
        text = re.sub(r'Tên Phòng/Ban \(\d\):?\s*_+\s*\n', f"Tên Phòng/Ban ({i+1}): {dname}\n", text, count=1)
        text = re.sub(r'Trưởng phòng:?\s*_+\s*\n', f"Trưởng phòng: {dhead}\n", text, count=1)
        text = re.sub(r'Số lượng nhân viên:?\s*_\s*\n', f"Số lượng nhân viên: {cnt}\n", text, count=1)
        text = re.sub(r'Ngày ký:?\s*_+\s*\n', f"Ngày ký: {d.strftime('%d/%m/%Y')}\n", text, count=1)

    text = re.sub(r'Từ\s*_\s*giờ\s*_\s*phút\s*đến\s*_\s*giờ\s*_\s*phút',
                  "Từ 08 giờ 00 phút đến 17 giờ 00 phút", text)

    return {
        "id": f"quy_che_noi_bo_cong_ty_{idx:05d}",
        "template_id": "t7",
        "contract_type": "Quy chế nội bộ công ty",
        "decision_no": dn, "date": d.strftime("%d/%m/%Y"),
        "company": company,
        "num_departments": len(depts),
        "risk_level": pick(["low", "medium"]),
        "has_violation": random.random() < 0.10,
        "text": text,
    }


def fill_t8(template, idx):
    """Giấy ủy quyền"""
    d = rdate()
    dn = f"UQ-{ri(100,999)}/2026"
    city = pick(CITIES)
    street = pick(STREETS)
    grantor = pick(VIETNAMESE_NAMES)
    attorney = pick([n for n in VIETNAMESE_NAMES if n != grantor])
    scope_type = pick(["đại diện pháp lý", "thủ tục hành chính", "giao dịch dân sự", "ngân hàng và tài sản"])
    duration_type = pick(["Một lần", "Có thời hạn", "Không có thời hạn"])
    dur_months = ri(6, 36) if duration_type == "Có thời hạn" else None
    redelegate = random.random() < 0.3
    tx_limit = ri(5, 50) * 10000000

    text = template
    text = re.sub(r'Số:?\s*UQ-_\+/2026', f"Số: {dn}", text)
    text = fill_doc_date(text, d)

    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {grantor}\n", text, count=1)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1960,1985).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text, count=1)
    text = re.sub(r'Ngày cấp:?\s*_+\s*\n', f"Ngày cấp: {rdate(2015,2022).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Nơi cấp:?\s*_+\s*\n', f"Nơi cấp: {pick(CITIES)}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,99)}, {street}, {pick(DISTRICTS.get(city,['Quận 1']))}, {city}\n", text, count=1)
    text = re.sub(r'Số điện thoại:?\s*_+\s*\n', f"Số điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: {remail(grantor)}\n", text, count=1)

    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {attorney}\n", text, count=1)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1975,2000).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,99)}, {street}, {pick(DISTRICTS.get(city,['Quận 1']))}, {city}\n", text, count=1)
    text = re.sub(r'Số điện thoại:?\s*_+\s*\n', f"Số điện thoại: {rphone()}\n", text, count=1)

    text = re.sub(r'Loại ủy quyền:?\s*_+', f"Loại ủy quyền: {scope_type}", text)
    text = re.sub(r'Thời hạn ủy quyền:?\s*_+', f"Thời hạn ủy quyền: {duration_type}", text)
    text = re.sub(r'Cho phép ủy quyền lại:?\s*_+', f"Cho phép ủy quyền lại: {'Có' if redelegate else 'Không'}", text)
    text = re.sub(r'Hạn mức giao dịch:?\s*_+', f"Hạn mức giao dịch: {tx_limit:,.0f} VNĐ", text)

    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}  ", text)

    return {
        "id": f"giay_uy_quyen_{idx:05d}",
        "template_id": "t8",
        "contract_type": "Giấy ủy quyền",
        "doc_no": dn, "date": d.strftime("%d/%m/%Y"),
        "grantor": grantor, "attorney": attorney,
        "scope_type": scope_type, "duration_type": duration_type,
        "risk_level": pick(["low", "medium", "high"]),
        "has_violation": random.random() < 0.20,
        "text": text,
    }


def fill_t9(template, idx):
    """Biên bản họp"""
    d = rdate()
    dn = f"BB-{ri(100,999)}/2026"
    city = pick(CITIES)
    mt_types = pick(["Họp Hội đồng Quản trị", "Đại hội đồng cổ đông", "Họp Ban Giám đốc",
                      "Họp tổng kết quý", "Họp phòng ban", "Họp lãnh đạo"])
    mname = f"Biên bản {mt_types} tháng {ri(1,12)} năm {d.year}"
    chair = pick(VIETNAMESE_NAMES)
    secretary = pick([n for n in VIETNAMESE_NAMES if n != chair])
    attendees = pick_n(VIETNAMESE_NAMES, ri(5, 12))
    absentees = pick_n([n for n in VIETNAMESE_NAMES if n not in attendees], ri(0, 3))

    text = template
    text = re.sub(r'Biên bản họp:?\s*_+', f"Biên bản họp: {mname}", text)
    text = re.sub(r'Số:?\s*BB-_\+/2026', f"Số: {dn}", text)
    text = re.sub(r'Ngày:?\s*_+\s*\n', f"Ngày: {d.strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Giờ:?\s*_\+:\d+\s*đến\s*_\+:\d+', f"Giờ: {ri(8,14):02d}:00 đến {ri(16,19):02d}:00", text)
    text = re.sub(r'Địa điểm:?\s*_+', f"Địa điểm: Phòng họp số {ri(1,10)}, Tầng {ri(1,5)}, {pick(COMPANY_NAMES[:3])}, {city}", text)
    text = re.sub(r'Chủ trì:?\s*_+', f"Chủ trì: {chair}", text)
    text = re.sub(r'Thư ký:?\s*_+', f"Thư ký: {secretary}", text)
    text = re.sub(r'Tổng số thành viên tham dự:?\s*_\s*\n', f"Tổng số thành viên tham dự: {len(attendees)} người\n", text)
    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}  ", text)

    return {
        "id": f"bien_ban_hop_{idx:05d}",
        "template_id": "t9",
        "contract_type": "Biên bản họp",
        "meeting_name": mname,
        "doc_no": dn, "date": d.strftime("%d/%m/%Y"),
        "chair": chair, "secretary": secretary,
        "num_attendees": len(attendees),
        "risk_level": "low",
        "has_violation": False,
        "text": text,
    }


def fill_t10(template, idx):
    """Hợp đồng vay tiền"""
    d = rdate()
    cn = f"HĐV-{ri(100,999)}/HĐV-{d.year}"
    city = pick(CITIES)
    street = pick(STREETS)
    lender = pick(VIETNAMESE_NAMES)
    borrower = pick([n for n in VIETNAMESE_NAMES if n != lender])
    has_guarantor = random.random() > 0.4
    guarantor = pick([n for n in VIETNAMESE_NAMES if n not in [lender, borrower]]) if has_guarantor else None

    amount = ri(5, 500) * 10000000
    interest = round(rf(1.0, 3.0), 1)
    months = ri(6, 60)
    monthly_int = int(amount * interest / 100)
    monthly_pay = int(amount / months)
    schedule = pick(["Trả góp đều hàng tháng", "Trả lãi hàng tháng, gốc cuối kỳ", "Trả một lần khi đáo hạn"])

    text = template
    text = re.sub(r'Số:?\s*_+/HĐV-2026', f"Số: {cn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tại\s*Địa\s*điểm', f"Tại {city}", text)

    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {lender}\n", text, count=1)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1960,1985).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text, count=1)
    text = re.sub(r'Ngày cấp:?\s*_+\s*\n', f"Ngày cấp: {rdate(2015,2022).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Nơi cấp:?\s*_+\s*\n', f"Nơi cấp: {pick(CITIES)}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,99)}, {street}, {pick(DISTRICTS.get(city,['Quận 1']))}, {city}\n", text, count=1)
    text = re.sub(r'Số điện thoại:?\s*_+\s*\n', f"Số điện thoại: {rphone()}\n", text, count=1)

    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {borrower}\n", text, count=1)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1975,2000).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text, count=1)
    text = re.sub(r'Nghề nghiệp:?\s*_+\s*\n', f"Nghề nghiệp: {pick(['Kinh doanh tự do', 'Nhân viên văn phòng', 'Công nhân', 'Giám đốc doanh nghiệp'])}\n", text)

    text = re.sub(r'Số tiền:?\s*_+\s*\(VNĐ\)', f"Số tiền: {amount:,.0f} (VNĐ)", text)
    m = re.search(r'\(Bằng chữ:?\s*_+\)', text)
    if m:
        text = text.replace(m.group(0), f"(Bằng chữ: {num_to_words(amount)} đồng)", 1)
    text = re.sub(r'Lãi suất:?\s*_\s*%', f"Lãi suất: {interest}%", text)
    text = re.sub(r'Thời hạn vay:?\s*_\s*tháng', f"Thời hạn vay: {months} tháng", text)
    text = re.sub(r'Ngày đáo hạn:?\s*_+\s*\n', f"Ngày đáo hạn: {(d+timedelta(days=months*30)).strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Hình thức trả:?\s*_+', f"Hình thức trả: {schedule}", text)
    text = re.sub(r'Tiền lãi hàng tháng:?\s*_+\s*\n', f"Tiền lãi hàng tháng: {monthly_int:,.0f} VNĐ\n", text)
    text = re.sub(r'Số tiền trả hàng tháng:?\s*_+\s*\n', f"Số tiền trả hàng tháng: {monthly_pay:,.0f} VNĐ\n", text)
    text = re.sub(r'Ngày\s*_\s*tháng\s*_\s*năm\s*_\s*', f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}  ", text)

    return {
        "id": f"hop_dong_vay_tien_{idx:05d}",
        "template_id": "t10",
        "contract_type": "Hợp đồng vay tiền",
        "contract_no": cn, "date": d.strftime("%d/%m/%Y"),
        "lender": lender, "borrower": borrower, "guarantor": guarantor,
        "loan_amount": amount, "interest_rate": interest, "loan_months": months,
        "risk_level": pick(["low", "medium", "high"]),
        "has_violation": random.random() < 0.25,
        "text": text,
    }


def fill_t11(template, idx):
    """Quyết định bổ nhiệm"""
    d = rdate()
    dn = f"QĐ-{ri(100,999)}/2026-BN"
    city = pick(CITIES)
    street = pick(STREETS)
    company = pick(COMPANY_NAMES)
    rep = pick(VIETNAMESE_NAMES)
    appointee = pick(VIETNAMESE_NAMES)
    new_pos = pick(["Trưởng phòng Kinh doanh", "Trưởng phòng Nhân sự", "Trưởng phòng Kỹ thuật",
                     "Trưởng phòng Marketing", "Kế toán trưởng", "Trưởng phòng Hành chính",
                     "Trưởng phòng Sản xuất", "Quản lý Chi nhánh", "Giám đốc Chi nhánh"])
    appt_type = pick(["Không có thời hạn", "Có thời hạn", "Thử việc"])
    sal_coef = round(rf(2.0, 8.0), 2)
    base_sal = ri(15, 80) * 1000000
    pos_allow = ri(3, 15) * 1000000

    text = template
    text = re.sub(r'Số:?\s*QĐ-_\+/2026-BN', f"Số: {dn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tên Công Ty:?\s*_+\s*\n', f"Tên Công Ty: {company}\n", text)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,299)}, {street}, {pick(DISTRICTS.get(city,['Quận 1']))}, {city}\n", text)
    text = re.sub(r'Điện thoại:?\s*_+\s*\n', f"Điện thoại: {rphone()}\n", text)
    text = re.sub(r'Email:?\s*_+\s*\n', f"Email: hr@{company.lower().replace(' ','')}.com\n", text)
    text = re.sub(r'Đại diện:?\s*_+\s*\n', f"Đại diện: {rep}\n", text)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: Giám đốc\n", text)

    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {appointee}\n", text)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1975,1995).strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text)
    text = re.sub(r'Bổ nhiệm giữ chức vụ:?\s*_+', f"Bổ nhiệm giữ chức vụ: {new_pos}", text)
    text = re.sub(r'Loại bổ nhiệm:?\s*_+', f"Loại bổ nhiệm: {appt_type}", text)
    text = re.sub(r'Có hiệu lực từ ngày:?\s*_+\s*\n', f"Có hiệu lực từ ngày: {d.strftime('%d/%m/%Y')}\n", text)
    text = re.sub(r'Hệ số lương:?\s*_\s*\n', f"Hệ số lương: {sal_coef}\n", text)
    text = re.sub(r'Mức lương:?\s*_+\s*\n', f"Mức lương: {base_sal:,.0f} VNĐ/tháng\n", text)
    text = re.sub(r'Phụ cấp chức vụ:?\s*_+\s*\n', f"Phụ cấp chức vụ: {pos_allow:,.0f} VNĐ/tháng\n", text)
    text = re.sub(r'Bàn giao trong vòng\s*_\s*ngày', f"Bàn giao trong vòng {ri(5,15)} ngày", text)
    text = re.sub(r'Ngày ký:?\s*_+\s*\n', f"Ngày ký: {d.strftime('%d/%m/%Y')}\n", text)

    return {
        "id": f"quyet_dinh_bo_nhiem_{idx:05d}",
        "template_id": "t11",
        "contract_type": "Quyết định bổ nhiệm",
        "decision_no": dn, "date": d.strftime("%d/%m/%Y"),
        "company": company, "appointee": appointee,
        "new_position": new_pos, "appointment_type": appt_type,
        "risk_level": pick(["low", "medium"]),
        "has_violation": random.random() < 0.15,
        "text": text,
    }


def fill_t12(template, idx):
    """Đơn xin nghỉ việc"""
    d = rdate()
    dn = f"ĐXN-{ri(100,999)}/2026"
    city = pick(CITIES)
    street = pick(STREETS)
    company = pick(COMPANY_NAMES)
    emp = pick(VIETNAMESE_NAMES)
    reasons = pick([
        "Tìm được công việc mới phù hợp hơn với chuyên môn và định hướng nghề nghiệp",
        "Vì lý do gia đình cần chuyển nơi cư trú đến tỉnh khác",
        "Sức khỏe không đảm bảo để tiếp tục công việc hiện tại",
        "Công việc không phù hợp với mong đợi và định hướng phát triển cá nhân",
        "Muốn khởi nghiệp kinh doanh riêng theo đam mê",
    ])
    notice = ri(30, 45)
    hire = rdate(2020, 2024)

    text = template
    text = re.sub(r'Số:?\s*ĐXN-_\+/2026', f"Số: {dn}", text)
    text = fill_doc_date(text, d)
    text = re.sub(r'Tên Công Ty:?\s*_+\s*\n', f"Tên Công Ty: {company}\n", text)
    text = re.sub(r'Họ và tên:?\s*_+\s*\n', f"Họ và tên: {emp}\n", text, count=1)
    text = re.sub(r'Ngày sinh:?\s*_+\s*\n', f"Ngày sinh: {rdate(1980,2000).strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Số CCCD/CMND:?\s*_+\s*\n', f"Số CCCD/CMND: {rid()}\n", text, count=1)
    text = re.sub(r'Địa chỉ:?\s*_+\s*\n', f"Địa chỉ: Số {ri(1,99)}, {street}, {city}\n", text, count=1)
    text = re.sub(r'Số điện thoại:?\s*_+\s*\n', f"Số điện thoại: {rphone()}\n", text, count=1)
    text = re.sub(r'Phòng ban:?\s*_+\s*\n', f"Phòng ban: {pick(['Phòng Kinh doanh','Phòng Nhân sự','Phòng Kỹ thuật','Phòng Marketing']) }\n", text, count=1)
    text = re.sub(r'Chức vụ:?\s*_+\s*\n', f"Chức vụ: {pick(POSITIONS_EMPLOYEE)}\n", text, count=1)
    text = re.sub(r'Ngày vào làm:?\s*_+\s*\n', f"Ngày vào làm: {hire.strftime('%d/%m/%Y')}\n", text, count=1)
    text = re.sub(r'Mã nhân viên:?\s*_+\s*\n', f"Mã nhân viên: NV-{ri(1000,9999)}\n", text, count=1)

    # Find reason line (after "Lý do:")
    text = re.sub(r'Lý do:?\s*_+', f"Lý do: {reasons}", text)
    text = re.sub(r'_\s*ngày\s*(?!làm|trước)', f"{notice} ngày", text)
    text = re.sub(r'Ngày làm việc cuối cùng:?\s*_+\s*\n', f"Ngày làm việc cuối cùng: {(d+timedelta(days=notice)).strftime('%d/%m/%Y')}\n", text)

    return {
        "id": f"don_xin_nghi_viec_{idx:05d}",
        "template_id": "t12",
        "contract_type": "Đơn xin nghỉ việc",
        "doc_no": dn, "date": d.strftime("%d/%m/%Y"),
        "company": company, "employee": emp,
        "reason": reasons, "notice_days": notice,
        "risk_level": pick(["low", "medium"]),
        "has_violation": random.random() < 0.15,
        "text": text,
    }


def fill_t13(template, idx):
    """Hợp đồng thuê nhà (variable-based)"""
    d = rdate()
    cn = f"HĐTN-{ri(100,999)}/HĐTN-{d.year}"
    lessor = pick(VIETNAMESE_NAMES)
    tenant = pick([n for n in VIETNAMESE_NAMES if n != lessor])
    prop_addr = pick(PROPERTY_ADDRESSES)
    area = ri(25, 200)
    rent = ri(3, 30) * 1000000
    duration = ri(6, 24)
    cert_no = rid()
    cert_issuer = f"UBND {pick(CITIES)}"
    cert_date = rdate(2018, 2023).strftime("%d/%m/%Y")

    vars_ = {
        "contract_number": cn,
        "day": d.day, "month": d.month, "year": d.year,
        "location": d.strftime('%d/%m/%Y').split('/')[2].split()[0],
        "lessor_name": lessor,
        "lessor_birthday": rdate(1960, 1985).strftime("%d/%m/%Y"),
        "lessor_id": rid(),
        "lessor_id_date": rdate(2015, 2022).strftime("%d/%m/%Y"),
        "lessor_address": f"Số {ri(1,99)}, {pick(STREETS)}, {pick(CITIES)}",
        "property_address": prop_addr,
        "ownership_cert_no": cert_no,
        "ownership_cert_issuer": cert_issuer,
        "ownership_cert_date": cert_date,
        "tenant_name": tenant,
        "tenant_birthday": rdate(1980, 2000).strftime("%d/%m/%Y"),
        "tenant_id": rid(),
        "tenant_id_date": rdate(2015, 2022).strftime("%d/%m/%Y"),
        "tenant_address": f"Số {ri(1,99)}, {pick(STREETS)}, {pick(CITIES)}",
        "premises_location": prop_addr.split(",")[0],
        "area": area,
        "premises_description": f"Căn hộ {ri(1,5)} phòng ngủ, {ri(1,3)} nhà vệ sinh",
        "rental_purpose": pick(["Để ở", "Kinh doanh nhỏ", "Văn phòng đại diện"]),
        "duration": duration,
        "start_date": d.strftime("%d/%m/%Y"),
        "end_date": (d + timedelta(days=duration*30)).strftime("%d/%m/%Y"),
        "rental_price": f"{rent:,.0f}",
        "price_in_words": num_to_words(rent),
        "payment_method": pick(["Tiền mặt", "Chuyển khoản ngân hàng"]),
        "payment_date": str(ri(1, 5)),
    }

    text = template
    for key, val in vars_.items():
        text = text.replace(f"{{{key}}}", str(val))

    return {
        "id": f"hop_dong_thue_nha_{idx:05d}",
        "template_id": "t13",
        "contract_type": "Hợp đồng thuê nhà",
        "contract_no": cn, "date": d.strftime("%d/%m/%Y"),
        "lessor": lessor, "tenant": tenant,
        "property_address": prop_addr,
        "monthly_rent": rent,
        "risk_level": pick(["low", "medium", "high"]),
        "has_violation": random.random() < 0.25,
        "text": text,
    }


# ==================== CONFIG ====================

FILLERS = {
    "t1": fill_t1, "t2": fill_t2, "t3": fill_t3, "t4": fill_t4, "t5": fill_t5,
    "t6": fill_t6, "t7": fill_t7, "t8": fill_t8, "t9": fill_t9, "t10": fill_t10,
    "t11": fill_t11, "t12": fill_t12, "t13": fill_t13,
}

CONTRACT_NAMES = {
    "t1": "hop_dong_mua_ban_hang_hoa", "t2": "hop_dong_lao_dong",
    "t3": "thoa_thuan_bao_mat_nda", "t4": "hop_dong_thue_nha_o",
    "t5": "hop_dong_cung_cap_dich_vu", "t6": "hop_dong_giao_khoan",
    "t7": "quy_che_noi_bo_cong_ty", "t8": "giay_uy_quyen",
    "t9": "bien_ban_hop", "t10": "hop_dong_vay_tien",
    "t11": "quyet_dinh_bo_nhiem", "t12": "don_xin_nghi_viec",
    "t13": "hop_dong_thue_nha",
}

DISTRIBUTION = {
    "t1": 800, "t2": 800, "t3": 800, "t4": 800, "t5": 800,
    "t6": 800, "t7": 800, "t8": 800, "t9": 800, "t10": 800,
    "t11": 800, "t12": 800, "t13": 800,
}


def load_template(tid):
    with open(os.path.join(TEMPLATES_DIR, f"{tid}.txt"), "r", encoding="utf-8") as f:
        return f.read()


def main():
    all_records = []
    for tid, count in DISTRIBUTION.items():
        print(f"Generating {count} for {tid}...", end=" ", flush=True)
        template = load_template(tid)
        filler = FILLERS[tid]
        type_records = []
        for i in range(count):
            record = filler(template, i + 1)
            all_records.append(record)
            type_records.append(record)

        # Save JSONL
        out = os.path.join(OUTPUT_DIR, f"{CONTRACT_NAMES[tid]}.jsonl")
        with open(out, "w", encoding="utf-8") as f:
            for r in type_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("OK")

    # Combined
    with open(os.path.join(OUTPUT_DIR, "all_contracts.jsonl"), "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Metadata
    import datetime
    risk_dist = {"low": sum(1 for r in all_records if r["risk_level"] == "low"),
                 "medium": sum(1 for r in all_records if r["risk_level"] == "medium"),
                 "high": sum(1 for r in all_records if r["risk_level"] == "high")}
    viol_dist = {"has_violation": sum(1 for r in all_records if r["has_violation"]),
                 "no_violation": sum(1 for r in all_records if not r["has_violation"])}

    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_records": len(all_records),
            "risk_distribution": risk_dist,
            "violation_distribution": viol_dist,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n=== DONE: {len(all_records)} records ===")
    print(f"Risk: {risk_dist}")
    print(f"Violations: {viol_dist}")


if __name__ == "__main__":
    main()
