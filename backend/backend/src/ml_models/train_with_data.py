"""
Script train SVM với dữ liệu từ CSV đã generate
"""
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.classifier import SVMContractClassifier


def load_training_data():
    """Load dữ liệu từ CSV"""
    csv_file = "src/ml_models/training_dataset.csv"
    
    print(f"📂 Đang đọc dữ liệu từ {csv_file}...")
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    print(f"✓ Đã load {len(df)} samples")
    print(f"✓ Các nhãn: {df['label'].unique().tolist()}")
    print(f"\n📊 Phân bố dữ liệu:")
    print(df['label'].value_counts())
    
    return df['text'].tolist(), df['label'].tolist()


def train_clause_classifier():
    """Train SVM classifier với dữ liệu thực"""
    print("\n" + "="*70)
    print("🎯 TRAINING SVM CLASSIFIER VỚI DỮ LIỆU THỰC")
    print("="*70)
    
    # Load data
    texts, labels = load_training_data()
    
    # Initialize classifier
    classifier = SVMContractClassifier(model_dir="models/svm_clauses")
    
    # Train với dữ liệu mới - dùng contract_type_model để phân loại điều khoản
    print("\n🚀 Bắt đầu training model phân loại điều khoản...")
    results = classifier.train_contract_type_classifier(
        texts=texts,
        labels=labels,
        test_size=0.2,
        use_grid_search=False  # Set True nếu muốn tìm best params (tốn thời gian)
    )
    
    print("\n" + "="*70)
    print("✅ TRAINING HOÀN TẤT!")
    print("="*70)
    print(f"\n🎯 Accuracy: {results['accuracy']:.2%}")
    
    # Test với vài mẫu
    print("\n" + "="*70)
    print("🧪 TESTING VỚI MẪU MỚI")
    print("="*70)
    
    test_cases = [
        "Lương cơ bản 15 triệu đồng mỗi tháng, thưởng Tết tối thiểu 1 tháng lương",
        "Làm việc 8 tiếng mỗi ngày, từ thứ 2 đến thứ 6, nghỉ thứ 7 chủ nhật",
        "Công ty đóng đầy đủ BHXH, BHYT, BHTN theo quy định",
        "Không được tiết lộ thông tin mật của công ty cho bên thứ 3",
        "Nếu muốn nghỉ việc phải báo trước 30 ngày",
    ]
    
    for text in test_cases:
        result = classifier.predict_contract_type(text)
        print(f"\n📝 Text: {text}")
        print(f"   ➜ Dự đoán: {result['predicted_type']}")
        print(f"   ➜ Độ tin cậy: {result['confidence']:.1%}")
        
        # Show top 3 predictions
        probs = sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"   ➜ Top 3:")
        for label, prob in probs:
            print(f"      - {label}: {prob:.1%}")
    
    print("\n✅ Hoàn tất!")
    return classifier


if __name__ == "__main__":
    train_clause_classifier()
