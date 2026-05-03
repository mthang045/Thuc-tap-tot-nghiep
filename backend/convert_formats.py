"""
Script chuyen doi cac file .doc/.docx thanh .txt trong thu muc templates
"""
import os
import re

# Thu muc templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'templates')

# Danh sach cac file can chuyen doi
# Map: ten file cu -> ten file moi (.txt)
FILES_TO_CONVERT = {
    'Biên bản họp.doc': 'bien_ban_hop.txt',
    'Đơn xin nghỉ việc.docx': 'don_xin_nghi_viec.txt',
    'Giấy ủy quyền.docx': 'giay_uy_quyen.txt',
    'HỢP ĐỒNG BẢO MẬT THÔNG TIN.docx': 'hop_dong_bao_mat.txt',
    'HỢP ĐỒNG CHO VAY TIỀN.doc': 'hop_dong_cho_vay_tien.txt',
    'Hợp đồng cung cấp dịch vụ.doc': 'hop_dong_cung_cap_dich_vu.txt',
    'Hợp đồng lao động.doc': 'hop_dong_lao_dong.txt',
    'Hợp đồng mua bán hàng hóa.doc': 'hop_dong_mua_ban_hang_hoa.txt',
    'Hợp đồng thuê nhà.doc': 'hop_dong_thue_nha.txt',
    'Quyết định bổ nhiệm.docx': 'quyet_dinh_bo_nhiem.txt',
}


def convert_docx_to_text(filepath):
    """Chuyen doi file .docx sang text bang python-docx"""
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = []
        for para in doc.paragraphs:
            paragraphs.append(para.text)
        return '\n'.join(paragraphs)
    except ImportError:
        print("  python-docx chua duoc cai dat. Thu cai dat bang: pip install python-docx")
        return None
    except Exception as e:
        print(f"  Loi khi doc file: {e}")
        return None


def convert_doc_to_text(filepath):
    """Chuyen doi file .doc (Word 97-2003) sang text bang Microsoft Word qua win32com"""
    try:
        import win32com.client
        import pythoncom
        # Initialize COM for this thread
        pythoncom.CoInitialize()
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(os.path.abspath(filepath))
            content = doc.Content.Text
            doc.Close(False)
            word.Quit()
            return content
        finally:
            pythoncom.CoUninitialize()
    except ImportError:
        print("  pywin32 chua duoc cai dat. Thu cai dat bang: pip install pywin32")
        return None
    except Exception as e:
        print(f"  Loi win32com: {e}")
        return None


def convert_file(filename, output_name):
    """Chuyen doi mot file"""
    input_path = os.path.join(TEMPLATES_DIR, filename)
    output_path = os.path.join(TEMPLATES_DIR, output_name)

    if not os.path.exists(input_path):
        print(f"[X] File khong ton tai: {filename}")
        return False

    ext = os.path.splitext(filename)[1].lower()

    if ext == '.docx':
        print(f"  Dang chuyen doi .docx: {filename}")
        content = convert_docx_to_text(input_path)
    elif ext == '.doc':
        print(f"  Dang chuyen doi .doc: {filename}")
        content = convert_doc_to_text(input_path)
    else:
        print(f"  Bo qua (khong phai .doc/.docx): {filename}")
        return False

    if content is None:
        print(f"  Loi: Khong the chuyen doi {filename}")
        return False

    # Ghi file txt
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  OK - Da luu: {output_name}")
    return True


def delete_old_templates():
    """Xoa cac file cu tu t1.txt den t13.txt"""
    import glob
    deleted = []
    for i in range(1, 14):
        pattern = os.path.join(TEMPLATES_DIR, f't{i}.txt')
        files = glob.glob(pattern)
        for f in files:
            try:
                os.remove(f)
                deleted.append(os.path.basename(f))
                print(f"  Da xoa: {os.path.basename(f)}")
            except Exception as e:
                print(f"  Loi xoa {f}: {e}")
    return deleted


def main():
    import sys
    import io
    # Fix UTF-8 output cho Windows PowerShell
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("=" * 60)
    print("CHUYEN DOI FILE MAU TU .doc/.docx SANG .txt")
    print("=" * 60)

    # Buoc 1: Chuyen doi cac file moi
    print("\n[BUOC 1] Chuyen doi cac file Word moi...")
    converted = []
    for filename, output_name in FILES_TO_CONVERT.items():
        if convert_file(filename, output_name):
            converted.append(output_name)

    # Buoc 2: Xoa cac file cu
    print("\n[BUOC 2] Xoa cac file cu (t1.txt - t13.txt)...")
    deleted = delete_old_templates()

    # Buoc 3: In ket qua
    print("\n" + "=" * 60)
    print("KET QUA")
    print("=" * 60)
    print(f"\nCac file da chuyen doi ({len(converted)}):")
    for f in converted:
        print(f"  OK: {f}")

    print(f"\nCac file da xoa ({len(deleted)}):")
    for f in deleted:
        print(f"  DA XOA: {f}")

    print("\nLuu y: Vui long kiem tra noi dung cac file .txt")
    print("neu giao dien hien tai su dung ten file cu (t1, t2, ...)")
    print("thi can cap nhat lai code backend.")


if __name__ == "__main__":
    main()
