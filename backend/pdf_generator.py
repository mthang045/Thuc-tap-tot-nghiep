"""
PDF Report Generator for Legal Contract Analysis
Uses ReportLab to create professional PDF reports with Vietnamese support
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

class ContractPDFReport:
    def __init__(self, output_path):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # Register Vietnamese-compatible font (DejaVu Sans supports Vietnamese)
        try:
            # Try to use DejaVuSans if available
            from reportlab.pdfbase.ttfonts import TTFont
            font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
            if not os.path.exists(font_path):
                # Fallback: ReportLab's built-in fonts that support Latin Extended
                self.font_name = 'Helvetica'
                self.font_bold = 'Helvetica-Bold'
        except:
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
        
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles with proper encoding
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#06B6D4'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Helvetica',
            encoding='utf-8',
            leading=14
        ))
    
    def add_header(self, contract_name, upload_date):
        """Add report header"""
        # Title - use ASCII-safe version for display
        title_text = "BAO CAO PHAN TICH HOP DONG"
        title = Paragraph(title_text, self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Contract info - escape special characters
        contract_name_safe = self._escape_text(contract_name)
        upload_date_safe = self._escape_text(upload_date)
        
        info = Paragraph(
            f"<b>Ten hop dong:</b> {contract_name_safe}<br/>"
            f"<b>Ngay phan tich:</b> {upload_date_safe}",
            self.styles['CustomBody']
        )
        self.story.append(info)
        self.story.append(Spacer(1, 0.3*inch))
    
    def _escape_text(self, text):
        """Escape text for PDF rendering - convert Vietnamese to ASCII-safe"""
        if not text:
            return ""
        # Replace common Vietnamese characters with ASCII equivalents
        replacements = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'đ': 'd',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            # Uppercase
            'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
            'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
            'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
            'Đ': 'D',
            'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
            'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
            'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
            'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
            'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
            'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
            'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
            'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
            'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
        }
        result = text
        for viet, ascii_char in replacements.items():
            result = result.replace(viet, ascii_char)
        
        # Escape XML special characters
        result = result.replace('&', '&amp;')
        result = result.replace('<', '&lt;')
        result = result.replace('>', '&gt;')
        
        return result
    
    def add_summary_stats(self, high_risk, medium_risk, low_risk, total_issues):
        """Add summary statistics section"""
        heading = Paragraph("TONG QUAN", self.styles['CustomHeading'])
        self.story.append(heading)
        
        # Create stats table with ASCII-safe text
        data = [
            ['Muc do rui ro', 'So luong'],
            ['[Cao] Nghiem trong', str(high_risk)],
            ['[TB] Trung binh', str(medium_risk)],
            ['[Thap] Thap', str(low_risk)],
            ['Tong so van de', str(total_issues)]
        ]
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#06B6D4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F9FF')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_issues_section(self, issues):
        """Add detected issues section"""
        if not issues:
            return
            
        heading = Paragraph("CHI TIET CAC VAN DE PHAT HIEN", self.styles['CustomHeading'])
        self.story.append(heading)
        
        for idx, issue in enumerate(issues, 1):
            severity_colors = {
                'high': '#EF4444',
                'medium': '#F59E0B',
                'low': '#3B82F6'
            }
            severity_labels = {
                'high': '[CAO] Nghiem trong',
                'medium': '[TB] Trung binh',
                'low': '[THAP] Thap'
            }
            
            color = severity_colors.get(issue.get('severity', 'low'), '#3B82F6')
            label = severity_labels.get(issue.get('severity', 'low'), 'Thap')
            
            title_safe = self._escape_text(issue.get('title', 'Van de chua xac dinh'))
            desc_safe = self._escape_text(issue.get('description', 'Khong co mo ta'))
            
            issue_text = f"""
            <b><font color="{color}">{idx}. {label}</font></b><br/>
            <b>{title_safe}</b><br/>
            {desc_safe}
            """
            
            para = Paragraph(issue_text, self.styles['CustomBody'])
            self.story.append(para)
            self.story.append(Spacer(1, 0.15*inch))
    
    def add_ai_analysis(self, ai_analysis):
        """Add AI analysis section"""
        if not ai_analysis or ai_analysis == "Không thể phân tích chi tiết do lỗi hệ thống.":
            return
            
        heading = Paragraph("PHAN TICH CHI TIET TU AI", self.styles['CustomHeading'])
        self.story.append(heading)
        
        # Clean and escape AI analysis text
        ai_analysis_safe = self._escape_text(ai_analysis)
        
        # Format AI analysis text
        paragraphs = ai_analysis_safe.split('\n\n')
        for para_text in paragraphs:
            if para_text.strip():
                # Further clean line breaks
                clean_text = para_text.replace('\n', '<br/>')
                para = Paragraph(clean_text, self.styles['CustomBody'])
                self.story.append(para)
                self.story.append(Spacer(1, 0.1*inch))
    
    def add_recommendations(self, recommendations):
        """Add recommendations section"""
        if not recommendations:
            return
            
        heading = Paragraph("KIEN NGHI", self.styles['CustomHeading'])
        self.story.append(heading)
        
        for idx, rec in enumerate(recommendations, 1):
            rec_safe = self._escape_text(rec)
            rec_text = f"<b>{idx}.</b> {rec_safe}"
            para = Paragraph(rec_text, self.styles['CustomBody'])
            self.story.append(para)
            self.story.append(Spacer(1, 0.1*inch))
    
    def add_footer(self):
        """Add footer"""
        self.story.append(Spacer(1, 0.5*inch))
        footer_text = f"""
        <i>Bao cao duoc tao tu dong boi Legal Contract Reviewer<br/>
        Thoi gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        self.story.append(footer)
    
    def generate(self, data):
        """Generate the PDF report"""
        # Add all sections
        self.add_header(data.get('contract_name', 'Hợp đồng'), data.get('upload_date', ''))
        self.add_summary_stats(
            data.get('high_risk', 0),
            data.get('medium_risk', 0),
            data.get('low_risk', 0),
            data.get('total_issues', 0)
        )
        self.add_issues_section(data.get('issues', []))
        self.add_ai_analysis(data.get('ai_analysis', ''))
        self.add_recommendations(data.get('recommendations', []))
        self.add_footer()
        
        # Build PDF
        self.doc.build(self.story)
        return self.output_path
