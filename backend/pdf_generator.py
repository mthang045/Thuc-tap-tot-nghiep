"""
PDF Report Generator for Legal Contract Analysis
Supports Vietnamese characters with Unicode fonts (fpdf2 + markdown)
"""

import os
import re
import markdown
from fpdf import FPDF
from bs4 import BeautifulSoup

# Đường dẫn tới thư mục chứa font chữ
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        # Load fonts trong __init__
        self.fonts_loaded = False
        try:
            arial_path = os.path.join(FONT_DIR, 'arial.ttf')
            arialbd_path = os.path.join(FONT_DIR, 'arialbd.ttf')
            ariali_path = os.path.join(FONT_DIR, 'ariali.ttf')
            
            if os.path.exists(arial_path):
                self.add_font('Arial', '', arial_path, uni=True)
                self.fonts_loaded = True
            if os.path.exists(arialbd_path):
                self.add_font('Arial', 'B', arialbd_path, uni=True)
            if os.path.exists(ariali_path):
                self.add_font('Arial', 'I', ariali_path, uni=True)
        except Exception as e:
            print(f"⚠️ Warning loading fonts: {e}")
            
    def header(self):
        # Thiết lập header cho mỗi trang
        if self.fonts_loaded:
            self.set_font("Arial", 'B', 15)
        else:
            return  # Skip header if no fonts
        # Di chuyển con trỏ sang phải
        self.cell(80)
        # Tiêu đề
        self.cell(30, 10, 'BÁO CÁO RÀ SOÁT HỢP ĐỒNG LAO ĐỘNG', 0, 0, 'C')
        # Xuống dòng
        self.ln(20)

    def footer(self):
        if not self.fonts_loaded:
            return  # Skip footer if no fonts
        # Đặt vị trí cách đáy 1.5 cm
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        # Số trang
        self.cell(0, 10, f'Trang {self.page_no()}/{{nb}}', 0, 0, 'C')

def restructure_html_numbering(html_content: str) -> str:
    """
    Restructure HTML to match exact format:
    - Major sections (h2, h3): No numbers, just title with colon (e.g., "TÓM TẮT TỔNG QUAN:")
    - List items: Keep as bullet points
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all major headings (h2, h3 only - not h1)
        major_sections = soup.find_all(['h2', 'h3'])
        
        for heading in major_sections:
            original_text = heading.get_text().strip()
            # Remove existing numbering like "1.", "2.", "##", etc.
            cleaned_text = re.sub(r'^[\d\#]+[\.\:\s]*', '', original_text).strip()
            
            # Remove trailing colon if exists, we'll add it back
            cleaned_text = cleaned_text.rstrip(':')
            
            # Clear và set lại content - NO numbers, just text + colon
            heading.clear()
            heading.string = f"{cleaned_text}:"
        
        # Convert ALL ordered lists (ol) to unordered lists (ul) for bullet points
        for ol_tag in soup.find_all('ol'):
            ol_tag.name = 'ul'  # Change tag from <ol> to <ul>
        
        # Remove numbering from all list items (keep text only, fpdf2 will add bullets)
        for li in soup.find_all('li'):
            li_text = li.get_text().strip()
            # Remove existing numbering
            cleaned_li = re.sub(r'^[\d]+[\.\:\s]*', '', li_text).strip()
            # Remove bullet characters if any
            cleaned_li = re.sub(r'^[\-\*\•]+\s*', '', cleaned_li).strip()
            
            # Clear và set lại content (no numbers, just text)
            li.clear()
            li.string = cleaned_li
        
        return str(soup)
    except Exception as e:
        print(f"⚠️ Warning restructuring numbering: {e}")
        import traceback
        traceback.print_exc()
        return html_content


def generate_pdf_report(markdown_content: str, output_filename: str = "Bao_Cao_Hop_Dong.pdf"):
    """
    Hàm nhận nội dung Markdown từ LLM và xuất ra file PDF tiếng Việt có dấu.
    
    Args:
        markdown_content: Nội dung phân tích từ AI (Markdown format)
        output_filename: Tên file PDF output
        
    Returns:
        str: Đường dẫn file PDF đã tạo
    """
    pdf = PDFReport()  # Fonts được load trong __init__
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Check if fonts loaded
    if not pdf.fonts_loaded:
        print("❌ Vietnamese fonts not loaded!")
        print(f"⚠️ Please add fonts to: {FONT_DIR}")
        return None
    
    print("✅ Vietnamese fonts loaded successfully!")
    pdf.set_font("Arial", size=12)
    
    # 2. Chuyển đổi Markdown của AI thành HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=['extra', 'nl2br']  # Support tables, newline to br
    )
    
    # 3. Restructure numbering (I, II, III for sections; 1, 2, 3 for items)
    html_content = restructure_html_numbering(html_content)
    
    # 4. Thêm khoảng trống giữa các section (thêm nhiều <br> để giãn dòng)
    html_content = html_content.replace('</h1>', '</h1><br><br>')
    html_content = html_content.replace('</h2>', '</h2><br>')
    html_content = html_content.replace('</h3>', '</h3><br>')
    html_content = html_content.replace('</p>', '</p><br>')
    html_content = html_content.replace('</ul>', '</ul><br>')
    html_content = html_content.replace('</ol>', '</ol><br>')
    html_content = html_content.replace('</li>', '</li><br>')
    
    # 5. Ghi nội dung HTML vào PDF
    try:
        pdf.write_html(html_content)
        print("✅ HTML content written to PDF")
    except Exception as e:
        print(f"❌ Error writing HTML to PDF: {e}")
        print("⚠️ Fallback to plain text mode...")
        # Fallback: Write plain text
        lines = markdown_content.split('\n')
        for line in lines:
            if line.strip():
                try:
                    pdf.multi_cell(0, 10, line)
                    pdf.ln(4)  # Increased line spacing
                except:
                    # Skip lines that can't be rendered
                    pass
    
    # 5. Lưu file
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    pdf.output(output_path)
    print(f"✅ PDF generated successfully: {output_path}")
    return output_path


def test_pdf_generator():
    """Test function to verify PDF generation works"""
    test_content = """
# Báo Cáo Phân Tích Hợp Đồng

## Tóm Tắt Tổng Quan
Đây là hợp đồng lao động giữa hai bên với thời hạn xác định.

## Các Vấn Đề Phát Hiện

1. Thiếu điều khoản về bảo hiểm xã hội
2. Không quy định rõ về thời gian làm việc
3. Không rõ thời hạn thanh toán lương
4. Thiếu điều khoản bảo mật thông tin

## Phân Tích Chi Tiết

1. Điều khoản trách nhiệm chưa rõ ràng, đặc biệt là về việc xây ra tai nạn hoặc mất mát hàng hóa
2. Điều khoản thanh toán không rõ ràng: đặc biệt là về việc thanh toán chậm và lãi suất chậm thanh toán
3. Không có quy định về việc giải quyết tranh chấp giữa các bên

## Khuyến Nghị Cải Thiện

1. Bổ sung quy định về trách nhiệm của các bên trong trường hợp xảy ra tai nạn hoặc mất mát hàng hóa
2. Làm rõ điều khoản thanh toán, bao gồm việc thanh toán chậm và lãi suất chậm thanh toán
3. Thêm quy định về việc giải quyết tranh chấp giữa các bên
4. Bổ sung quy định về việc bảo mật thông tin và dữ liệu của các bên
5. Cần tham khảo các văn bản pháp luật có liên quan như Bộ luật Dân sự 2015

---

**Lưu ý:** Báo cáo này được tạo tự động bởi AI. Vui lòng tham khảo ý kiến chuyên gia pháp lý.
"""
    
    try:
        output = generate_pdf_report(test_content, "test_report.pdf")
        print(f"\n{'='*60}")
        print(f"✅ TEST SUCCESSFUL!")
        print(f"📄 File created: {output}")
        print(f"📋 Format: Headings with colon (:), bullet points for lists")
        print(f"{'='*60}\n")
        return True
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ TEST FAILED!")
        print(f"Error: {e}")
        print(f"{'='*60}\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing PDF Generator with Vietnamese Support...")
    print("="*60 + "\n")
    test_pdf_generator()
