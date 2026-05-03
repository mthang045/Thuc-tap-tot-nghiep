"""
PDF Report Generator for Legal Contract Analysis
Supports Vietnamese characters with Unicode fonts (fpdf2 + markdown)
"""

import os
import re
import markdown
from fpdf import FPDF
from bs4 import BeautifulSoup
from datetime import datetime

# Đường dẫn tới thư mục chứa font chữ
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')


class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.fonts_loaded = False
        self.page_width = 210  # A4 width in mm
        self.page_height = 297  # A4 height in mm
        self.margin = 15
        self.content_width = self.page_width - 2 * self.margin

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
        pass

    def footer(self):
        if not self.fonts_loaded:
            return
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Trang {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.set_text_color(0, 0, 0)


def add_cover_header(pdf, contract_name, upload_date):
    """Add professional cover header to PDF"""
    if not pdf.fonts_loaded:
        return

    pdf.set_fill_color(30, 41, 59)
    pdf.rect(0, 0, pdf.page_width, 45, 'F')

    pdf.set_y(10)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'BÁO CÁO RÀ SOÁT HỢP ĐỒNG', 0, 1, 'C')

    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(203, 213, 225)
    truncated_name = contract_name[:50] + '...' if len(contract_name) > 50 else contract_name
    pdf.cell(0, 8, truncated_name, 0, 1, 'C')

    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 6, f'Ngày phân tích: {upload_date}', 0, 1, 'C')

    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)


def add_statistics_table(pdf, high_risk, medium_risk, low_risk, total_issues, safety_score):
    """Add risk statistics table to PDF"""
    if not pdf.fonts_loaded:
        return

    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(0, 10, 'THỐNG KÊ RỦI RO', 0, 1, 'L')
    pdf.ln(3)

    col_widths = [50, 30, 30, 30, 30]
    header_y = pdf.get_y()

    pdf.set_fill_color(239, 68, 68)
    pdf.rect(pdf.margin, header_y, col_widths[0], 8, 'F')
    pdf.set_xy(pdf.margin, header_y)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col_widths[0], 8, '  Nghiêm Trọng', 0, 0, 'L')

    pdf.set_fill_color(234, 179, 8)
    pdf.rect(pdf.margin + col_widths[0], header_y, col_widths[1], 8, 'F')
    pdf.set_xy(pdf.margin + col_widths[0], header_y)
    pdf.cell(col_widths[1], 8, str(medium_risk), 0, 0, 'C')

    pdf.set_fill_color(59, 130, 246)
    pdf.rect(pdf.margin + col_widths[0] + col_widths[1], header_y, col_widths[2], 8, 'F')
    pdf.set_xy(pdf.margin + col_widths[0] + col_widths[1], header_y)
    pdf.cell(col_widths[2], 8, str(low_risk), 0, 0, 'C')

    pdf.set_fill_color(100, 116, 139)
    pdf.rect(pdf.margin + col_widths[0] + col_widths[1] + col_widths[2], header_y, col_widths[3], 8, 'F')
    pdf.set_xy(pdf.margin + col_widths[0] + col_widths[1] + col_widths[2], header_y)
    pdf.cell(col_widths[3], 8, 'Tổng', 0, 0, 'C')

    pdf.set_fill_color(30, 41, 59)
    pdf.rect(pdf.margin + sum(col_widths[:4]), header_y, col_widths[4], 8, 'F')
    pdf.set_xy(pdf.margin + sum(col_widths[:4]), header_y)
    pdf.cell(col_widths[4], 8, 'Điểm AT', 0, 0, 'C')

    pdf.set_text_color(0, 0, 0)

    data_y = header_y + 8
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(pdf.margin, data_y, sum(col_widths), 10, 'F')
    pdf.set_xy(pdf.margin, data_y)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(col_widths[0], 10, f'  {high_risk}', 0, 0, 'L')
    pdf.cell(col_widths[1], 10, str(medium_risk), 0, 0, 'C')
    pdf.cell(col_widths[2], 10, str(low_risk), 0, 0, 'C')
    pdf.cell(col_widths[3], 10, str(total_issues), 0, 0, 'C')
    pdf.cell(col_widths[4], 10, f'{safety_score}/100', 0, 0, 'C')

    pdf.ln(20)


def add_issues_list(pdf, issues):
    """Add detailed issues list to PDF"""
    if not pdf.fonts_loaded or not issues:
        return

    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(0, 10, 'CHI TIẾT CÁC VẤN ĐỀ PHÁT HIỆN', 0, 1, 'L')
    pdf.ln(3)

    for idx, issue in enumerate(issues[:15]):
        severity = issue.get('severity', 'info')
        title = issue.get('title', '')
        description = issue.get('description', '')
        reference = issue.get('reference', '')
        suggestion = issue.get('suggestion', '')

        if severity == 'high':
            pdf.set_draw_color(239, 68, 68)
            pdf.set_text_color(185, 28, 28)
            label = '[NGHIÊM TRỌNG]'
        elif severity == 'medium':
            pdf.set_draw_color(234, 179, 8)
            pdf.set_text_color(146, 64, 14)
            label = '[TRUNG BÌNH]'
        else:
            pdf.set_draw_color(59, 130, 246)
            pdf.set_text_color(29, 78, 216)
            label = '[THẤP]'

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, f'{idx + 1}. {label} {title}', 0, 1, 'L')
        pdf.set_text_color(0, 0, 0)

        if description:
            pdf.set_font("Arial", '', 10)
            pdf.set_x(pdf.margin + 5)
            pdf.multi_cell(pdf.content_width - 5, 5, description)

        if reference:
            pdf.set_font("Arial", 'I', 9)
            pdf.set_text_color(100, 116, 139)
            pdf.set_x(pdf.margin + 5)
            pdf.multi_cell(pdf.content_width - 5, 4, f'Điều luật: {reference}')
            pdf.set_text_color(0, 0, 0)

        if suggestion:
            pdf.set_font("Arial", '', 10)
            pdf.set_fill_color(240, 253, 244)
            pdf.set_x(pdf.margin + 5)
            pdf.multi_cell(pdf.content_width - 5, 5, f'Khuyến nghị: {suggestion}')

        pdf.ln(5)


def add_ai_analysis(pdf, ai_analysis):
    """Add AI analysis section to PDF"""
    if not pdf.fonts_loaded or not ai_analysis:
        return

    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(0, 10, 'PHÂN TÍCH CHI TIẾT TỪ AI', 0, 1, 'L')
    pdf.ln(3)

    cleaned_text = ai_analysis
    cleaned_text = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned_text)
    cleaned_text = re.sub(r'\*(.*?)\*', r'\1', cleaned_text)
    cleaned_text = re.sub(r'^#{1,6}\s+', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'^\s*-\s+', '• ', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'^\s*\d+\.\s+', '• ', cleaned_text, flags=re.MULTILINE)

    pdf.set_font("Arial", '', 11)
    lines = cleaned_text.split('\n')
    for line in lines:
        if line.strip():
            pdf.multi_cell(pdf.content_width, 6, line.strip())
            pdf.ln(2)

    pdf.ln(10)


def add_footer_note(pdf):
    """Add footer disclaimer to PDF"""
    if not pdf.fonts_loaded:
        return

    pdf.ln(10)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.margin, pdf.get_y(), pdf.page_width - pdf.margin, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(100, 116, 139)
    footer_text = ("Lưu ý quan trọng: Đây là kết quả phân tích tự động bởi AI với công nghệ RAG. "
                   "Để đảm bảo tính chính xác cao nhất và tuân thủ pháp luật, vui lòng tham khảo ý kiến "
                   "của luật sư hoặc chuyên gia pháp lý trước khi ký kết hợp đồng. "
                   "Hệ thống chỉ mang tính chất tham khảo, cảnh báo sớm và hỗ trợ ra quyết định.")
    pdf.multi_cell(pdf.content_width, 5, footer_text)
    pdf.set_text_color(0, 0, 0)


def generate_pdf_report(analysis_content: str, output_filename: str = "Bao_Cao_Hop_Dong.pdf", metadata: dict = None):
    """
    Hàm tạo báo cáo PDF đầy đủ từ dữ liệu phân tích hợp đồng

    Args:
        analysis_content: Nội dung phân tích từ AI (Markdown format)
        output_filename: Tên file PDF output
        metadata: Dictionary chứa thông tin bổ sung (contract_name, upload_date, high_risk, etc.)

    Returns:
        str: Đường dẫn file PDF đã tạo
    """
    pdf = PDFReport()
    pdf.alias_nb_pages()

    if not pdf.fonts_loaded:
        print("❌ Vietnamese fonts not loaded!")
        print(f"⚠️ Please add fonts to: {FONT_DIR}")
        return None

    print("✅ Vietnamese fonts loaded successfully!")

    contract_name = (metadata.get('contract_name', metadata.get('filename', 'Hop_Dong_Khong_Ten')) if metadata else 'Hop_Dong_Khong_Ten')
    upload_date = (metadata.get('upload_date', '') if metadata else '')
    high_risk = (metadata.get('high_risk', 0) if metadata else 0)
    medium_risk = (metadata.get('medium_risk', 0) if metadata else 0)
    low_risk = (metadata.get('low_risk', 0) if metadata else 0)
    total_issues = (metadata.get('total_issues', 0) if metadata else 0)
    issues = (metadata.get('issues', []) if metadata else [])
    safety_score = 100 - (high_risk * 10) - (medium_risk * 5) - (low_risk * 2)
    safety_score = max(0, min(100, safety_score))

    pdf.add_page()
    add_cover_header(pdf, contract_name, upload_date)
    add_statistics_table(pdf, high_risk, medium_risk, low_risk, total_issues, safety_score)
    add_issues_list(pdf, issues)

    if analysis_content:
        add_ai_analysis(pdf, analysis_content)

    add_footer_note(pdf)

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

1. Điều khoản trách nhiệm chưa rõ ràng, đặc biệt là về việc xảy ra tai nạn hoặc mất mát hàng hóa
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

    test_metadata = {
        'contract_name': 'Hợp Đồng Lao Động Mẫu 2024.pdf',
        'upload_date': '29/04/2026',
        'high_risk': 2,
        'medium_risk': 3,
        'low_risk': 1,
        'total_issues': 6,
        'issues': [
            {
                'severity': 'high',
                'title': 'Thiếu điều khoản về bảo hiểm xã hội',
                'description': 'Hợp đồng không quy định rõ về bảo hiểm xã hội, bảo hiểm y tế và các chế độ BHXH bắt buộc.',
                'reference': 'Điều 21, Bộ luật Lao động 2019',
                'suggestion': 'Bổ sung điều khoản về bảo hiểm xã hội, bảo hiểm y tế và các chế độ BHXH bắt buộc.'
            },
            {
                'severity': 'high',
                'title': 'Thời gian làm việc không rõ ràng',
                'description': 'Hợp đồng không quy định cụ thể về giờ làm việc, có thể dẫn đến tranh chấp sau này.',
                'reference': 'Điều 54, Bộ luật Lao động 2019',
                'suggestion': 'Xác định rõ giờ làm việc, số giờ làm thêm và cách tính lương tăng ca.'
            },
            {
                'severity': 'medium',
                'title': 'Không có điều khoản giải quyết tranh chấp',
                'description': 'Hợp đồng thiếu điều khoản về giải quyết tranh chấp khi xảy ra bất đồng ý.',
                'suggestion': 'Bổ sung điều khoản về giải quyết tranh chấp, ưu tiên thương lượng hoặc hòa giải.'
            }
        ]
    }

    try:
        output = generate_pdf_report(test_content, "test_report_full.pdf", test_metadata)
        print(f"\n{'='*60}")
        print(f"✅ TEST SUCCESSFUL!")
        print(f"📄 File created: {output}")
        print(f"📋 Format: Full report with header, statistics, issues, AI analysis")
        print(f"{'='*60}\n")
        return True
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ TEST FAILED!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing PDF Generator with Vietnamese Support...")
    print("="*60 + "\n")
    test_pdf_generator()
