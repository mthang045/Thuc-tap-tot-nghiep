"""
Script to import legal documents from source_laws to MongoDB
"""
import os
import pymongo
from datetime import datetime
import re

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
db = client['legal_AI_db']
legal_docs_collection = db['legal_documents']

# Path to OCR text files
SOURCE_DIR = r"C:\Users\buimi\OneDrive\Documents\Thực tập\GenZ-Legal-AI-Final\backend\data\source_laws\ocr_text"

print("="*80)
print("📚 IMPORTING LEGAL DOCUMENTS TO MONGODB")
print("="*80)

# Category mapping
CATEGORY_MAP = {
    'co_ban': 'Cơ bản',
    'doanh_nghiep': 'Doanh nghiệp',
    'khac': 'Khác',
    'ngan_hang_tin_dung': 'Ngân hàng & Tín dụng',
    'bao_mat': 'Bảo mật',
    'so_huu_tri_tue': 'Sở hữu trí tuệ',
    'tai_chinh_thue': 'Tài chính & Thuế',
    'tranh_chap': 'Tranh chấp',
    'xay_dung_bds': 'Xây dựng & BĐS'
}

def parse_filename(filename):
    """
    Parse filename to extract metadata
    Format: category_Law_Name_Year.txt
    Example: co_ban_Bo_luat_Dan_su_2015.txt
    """
    name_without_ext = filename.replace('.txt', '')
    parts = name_without_ext.split('_', 1)  # Split at first underscore
    
    if len(parts) >= 2:
        category = parts[0]
        rest = parts[1]
        
        # Extract year (last 4 digits)
        year_match = re.search(r'(\d{4})$', rest)
        year = int(year_match.group(1)) if year_match else None
        
        # Get law name (everything before year)
        if year:
            law_name = rest[:-(len(str(year))+1)].replace('_', ' ')
        else:
            law_name = rest.replace('_', ' ')
        
        return {
            'category': CATEGORY_MAP.get(category, category),
            'category_code': category,
            'law_name': law_name,
            'year': year
        }
    
    return {
        'category': 'Khác',
        'category_code': 'khac',
        'law_name': name_without_ext.replace('_', ' '),
        'year': None
    }

def split_into_sections(content, max_chars=5000):
    """
    Split long content into sections for better querying
    """
    sections = []
    lines = content.split('\n')
    current_section = []
    current_length = 0
    current_title = "Phần đầu"
    
    for line in lines:
        # Check if line is a section header (starts with specific patterns)
        if re.match(r'^(PHẦN|CHƯƠNG|MỤC|Điều \d+)', line.strip()):
            # Save previous section if it has content
            if current_section:
                sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_section).strip()
                })
                current_section = []
                current_length = 0
            current_title = line.strip()
        
        current_section.append(line)
        current_length += len(line)
        
        # Split if section gets too large
        if current_length > max_chars and current_section:
            sections.append({
                'title': current_title,
                'content': '\n'.join(current_section).strip()
            })
            current_section = []
            current_length = 0
            current_title = f"{current_title} (tiếp)"
    
    # Add last section
    if current_section:
        sections.append({
            'title': current_title,
            'content': '\n'.join(current_section).strip()
        })
    
    return sections

def import_documents():
    """Import all legal documents from source_laws"""
    
    # Clear existing documents
    print("\n🗑️  Clearing existing documents...")
    result = legal_docs_collection.delete_many({})
    print(f"   Deleted {result.deleted_count} old documents")
    
    # Get all .txt files
    txt_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.txt')]
    print(f"\n📁 Found {len(txt_files)} legal documents to import")
    
    total_imported = 0
    total_sections = 0
    
    for filename in txt_files:
        filepath = os.path.join(SOURCE_DIR, filename)
        
        try:
            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse metadata
            metadata = parse_filename(filename)
            
            # Get file stats
            file_size = os.path.getsize(filepath)
            char_count = len(content)
            
            # Split into sections
            sections = split_into_sections(content)
            
            # Create document
            document = {
                'filename': filename,
                'law_name': metadata['law_name'],
                'category': metadata['category'],
                'category_code': metadata['category_code'],
                'year': metadata['year'],
                'full_content': content,
                'char_count': char_count,
                'file_size': file_size,
                'sections': sections,
                'section_count': len(sections),
                'imported_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Insert into MongoDB
            result = legal_docs_collection.insert_one(document)
            
            print(f"   ✅ {metadata['law_name']} ({metadata['year']}) - {len(sections)} sections")
            total_imported += 1
            total_sections += len(sections)
            
        except Exception as e:
            print(f"   ❌ Error importing {filename}: {e}")
    
    print(f"\n{'='*80}")
    print(f"✅ IMPORT COMPLETE!")
    print(f"{'='*80}")
    print(f"📊 Statistics:")
    print(f"   - Total documents: {total_imported}")
    print(f"   - Total sections: {total_sections}")
    print(f"   - Average sections per document: {total_sections/total_imported:.1f}")
    
    # Create indexes for better search performance
    print(f"\n🔍 Creating indexes...")
    legal_docs_collection.create_index([('law_name', 'text'), ('full_content', 'text')])
    legal_docs_collection.create_index('category_code')
    legal_docs_collection.create_index('year')
    print(f"   ✅ Indexes created")
    
    # Show sample documents
    print(f"\n📚 Sample documents by category:")
    pipeline = [
        {'$group': {
            '_id': '$category',
            'count': {'$sum': 1},
            'laws': {'$push': '$law_name'}
        }},
        {'$sort': {'count': -1}}
    ]
    
    for category in legal_docs_collection.aggregate(pipeline):
        print(f"   - {category['_id']}: {category['count']} documents")
        for law in category['laws'][:2]:  # Show first 2
            print(f"     • {law}")

if __name__ == '__main__':
    try:
        import_documents()
        print(f"\n{'='*80}")
        print("🎉 LEGAL DOCUMENTS SUCCESSFULLY IMPORTED TO MONGODB!")
        print(f"{'='*80}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
