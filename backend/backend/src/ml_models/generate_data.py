"""
Script sinh dữ liệu training tự động bằng AI
Sử dụng GROQ (miễn phí) thay vì OpenAI để tạo các mẫu văn bản đa dạng cho training SVM
"""
import csv
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Cấu hình các nhãn bạn muốn phân loại
LABELS = [
    "Lương & Thưởng",
    "Thời gian làm việc & Nghỉ ngơi",
    "Bảo hiểm & Phúc lợi",
    "Bảo mật & Cam kết",
    "Chấm dứt hợp đồng",
    "Thông tin chung (Tiêu đề/Đại diện)",
    "Quyền & Nghĩa vụ chung"
]

# Số lượng mẫu muốn sinh cho MỖI nhãn (Ví dụ 20 -> Tổng sẽ có 140 mẫu)
# Tăng lên 50 hoặc 100 nếu muốn model xịn hơn
SAMPLES_PER_LABEL = 20 

def generate_synthetic_data():
    """Dùng LLM để sinh dữ liệu training - Sử dụng GROQ (miễn phí)"""
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"), temperature=0.9) # Temp cao để văn phong đa dạng
    
    output_file = "src/ml_models/training_dataset.csv"
    
    # Kiểm tra file tồn tại chưa, nếu chưa thì tạo header
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['text', 'label']) # Header
            
        print(f"🚀 Bắt đầu sinh {SAMPLES_PER_LABEL * len(LABELS)} mẫu dữ liệu...")
        
        for label in LABELS:
            print(f"⏳ Đang sinh dữ liệu cho nhãn: {label}...")
            
            prompt = ChatPromptTemplate.from_template(
                """Bạn là chuyên gia soạn thảo hợp đồng.
                Nhiệm vụ: Hãy viết {num} câu văn bản khác nhau thuộc về điều khoản: "{category}" trong Hợp đồng lao động.
                
                Yêu cầu:
                1. Văn phong đa dạng: từ trang trọng đến bình dân, ngắn gọn đến chi tiết.
                2. Có chứa các con số, mốc thời gian giả định.
                3. Định dạng trả về: Mỗi câu một dòng, không đánh số thứ tự, không gạch đầu dòng.
                4. Chỉ trả về nội dung tiếng Việt.
                """
            )
            
            chain = prompt | llm
            result = chain.invoke({"category": label, "num": SAMPLES_PER_LABEL})
            
            # Xử lý kết quả trả về
            lines = result.content.strip().split('\n')
            
            # Ghi vào file CSV
            count = 0
            for line in lines:
                clean_line = line.strip().strip('-').strip('"').strip()
                if clean_line:
                    writer.writerow([clean_line, label])
                    count += 1
            
            print(f"   ✅ Đã thêm {count} mẫu cho {label}")
            
    print(f"\n🎉 Hoàn tất! Dữ liệu đã lưu tại {output_file}")

if __name__ == "__main__":
    generate_synthetic_data()
