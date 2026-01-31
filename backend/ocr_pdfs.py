"""
Script OCR tự động cho các file PDF bị scan
Sử dụng Tesseract OCR để chuyển ảnh thành text
"""
import os
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from tqdm import tqdm
import io

# Cấu hình Tesseract (cần cài Tesseract-OCR trên Windows)
# Download: https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set TESSDATA_PREFIX để tìm file ngôn ngữ Vietnamese
os.environ['TESSDATA_PREFIX'] = os.path.join(os.path.expanduser('~'), 'tessdata')

def ocr_pdf(input_path, output_path, lang='vie'):
    """
    OCR một file PDF
    
    Args:
        input_path: Đường dẫn file PDF gốc (scan)
        output_path: Đường dẫn file text output
        lang: Ngôn ngữ OCR (vie=Tiếng Việt, eng=English)
    """
    print(f"\n📄 Đang OCR: {input_path.name}")
    
    # Mở PDF
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    all_text = []
    all_text.append(f"# {input_path.stem}\n")
    all_text.append("=" * 80 + "\n\n")
    
    # OCR từng trang
    for page_num in tqdm(range(total_pages), desc="OCR pages"):
        page = doc[page_num]
        
        # Render page thành ảnh (độ phân giải cao hơn = OCR tốt hơn)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # OCR ảnh
        try:
            text = pytesseract.image_to_string(img, lang=lang)
            
            if text.strip():
                all_text.append(f"--- Trang {page_num + 1} ---\n")
                all_text.append(text)
                all_text.append("\n\n")
        except Exception as e:
            print(f"   ⚠️ Lỗi trang {page_num + 1}: {e}")
    
    doc.close()
    
    # Lưu text
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(all_text)
    
    total_chars = sum(len(t) for t in all_text)
    print(f"   ✅ Hoàn thành: {total_chars:,} ký tự")
    
    return total_chars

def ocr_all_pdfs():
    """OCR tất cả PDF trong các thư mục con của source_laws"""
    script_dir = Path(__file__).parent
    source_base = script_dir / 'data' / 'source_laws'
    output_dir = script_dir / 'data' / 'source_laws' / 'ocr_text'
    
    if not source_base.exists():
        print(f"❌ Thư mục không tồn tại: {source_base}")
        return
    
    # Tìm tất cả PDF trong các thư mục con (trừ ocr_text)
    pdf_files = []
    for folder in source_base.iterdir():
        if folder.is_dir() and folder.name != 'ocr_text':
            pdf_files.extend(folder.glob('*.pdf'))
    
    if not pdf_files:
        print(f"❌ Không tìm thấy file PDF")
        return
    
    print(f"\n🔍 Tìm thấy {len(pdf_files)} file PDF")
    print("="*80)
    
    total_processed = 0
    total_skipped = 0
    
    for pdf_file in pdf_files:
        # Tạo tên file output với prefix thư mục để tránh trùng
        folder_name = pdf_file.parent.name
        output_file = output_dir / f"{folder_name}_{pdf_file.stem}.txt"
        
        # Skip nếu đã OCR rồi
        if output_file.exists():
            print(f"⏭️  Bỏ qua: {folder_name}/{pdf_file.name} (đã OCR)")
            total_skipped += 1
            continue
        
        print(f"\n📁 {folder_name}/{pdf_file.name}")
        
        try:
            chars = ocr_pdf(pdf_file, output_file, lang='vie')
            total_processed += 1
            
            if chars < 1000:
                print(f"   ⚠️  Cảnh báo: Ít text ({chars} ký tự), có thể OCR kém")
        
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
    
    print("\n" + "="*80)
    print(f"✅ Đã OCR: {total_processed} file")
    print(f"⏭️  Đã có sẵn: {total_skipped} file")
    print(f"📊 Tổng: {total_processed + total_skipped}/{len(pdf_files)} file")
    print(f"📂 Text đã lưu tại: {output_dir}")
    print("\n💡 Bước tiếp theo:")
    print("   python train_simple.py")

if __name__ == '__main__':
    # Check Tesseract
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
    except:
        print("❌ Tesseract chưa cài đặt!")
        print("   Download tại: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Sau khi cài, chạy lại script này")
        exit(1)
    
    ocr_all_pdfs()
