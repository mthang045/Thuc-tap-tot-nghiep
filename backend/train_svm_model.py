"""
SVM Contract Classification Model Training Script
Train SVM để phân loại hợp đồng thành các categories khác nhau
"""

import os
import joblib
import numpy as np
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score
import pymongo
from datetime import datetime

# MongoDB connection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['legal_AI_db']

# Contract categories mapping
CONTRACT_CATEGORIES = {
    'mua_ban': 'Hợp đồng mua bán',
    'thue': 'Hợp đồng thuê',
    'lao_dong': 'Hợp đồng lao động',
    'dich_vu': 'Hợp đồng dịch vụ',
    'xay_dung': 'Hợp đồng xây dựng',
    'van_chuyen': 'Hợp đồng vận chuyển',
    'cung_ung': 'Hợp đồng cung ứng',
    'dai_ly': 'Hợp đồng đại lý',
    'bao_hiem': 'Hợp đồng bảo hiểm',
    'khac': 'Hợp đồng khác'
}

# Training data với các mẫu hợp đồng điển hình
TRAINING_DATA = [
    # Mua bán
    ("Hai bên thỏa thuận mua bán hàng hóa với giá trị thanh toán ngay", "mua_ban"),
    ("Bên bán cam kết giao hàng đúng chất lượng, bên mua thanh toán theo hóa đơn", "mua_ban"),
    ("Hợp đồng mua bán nhà đất, giao dịch quyền sở hữu", "mua_ban"),
    ("Mua bán sản phẩm với điều khoản thanh toán và bảo hành", "mua_ban"),
    ("Chuyển nhượng quyền sử dụng đất và tài sản gắn liền", "mua_ban"),
    
    # Thuê
    ("Hai bên thỏa thuận cho thuê bất động sản với giá thuê hàng tháng", "thue"),
    ("Hợp đồng thuê văn phòng, thời hạn 12 tháng, tiền thuê trả đầu tháng", "thue"),
    ("Cho thuê nhà ở với tiền cọc và điều khoản gia hạn", "thue"),
    ("Thuê mặt bằng kinh doanh khu vực trung tâm", "thue"),
    ("Thỏa thuận cho thuê thiết bị máy móc theo tháng", "thue"),
    
    # Lao động
    ("Hợp đồng lao động xác định thời hạn 24 tháng, lương cơ bản", "lao_dong"),
    ("Hai bên cam kết quyền và nghĩa vụ người lao động người sử dụng", "lao_dong"),
    ("Thỏa thuận làm việc với chế độ bảo hiểm xã hội đầy đủ", "lao_dong"),
    ("Hợp đồng thử việc 2 tháng với mức lương thử việc", "lao_dong"),
    ("Thời gian làm việc 8 tiếng mỗi ngày nghỉ thứ 7 chủ nhật", "lao_dong"),
    
    # Dịch vụ
    ("Cung cấp dịch vụ tư vấn pháp lý với chi phí theo giờ", "dich_vu"),
    ("Hợp đồng dịch vụ bảo trì hệ thống theo định kỳ", "dich_vu"),
    ("Dịch vụ marketing và quảng cáo trên các nền tảng", "dich_vu"),
    ("Cung cấp dịch vụ kế toán và báo cáo tài chính", "dich_vu"),
    ("Dịch vụ thiết kế và phát triển website theo yêu cầu", "dich_vu"),
    
    # Xây dựng
    ("Thi công xây dựng công trình theo thiết kế được duyệt", "xay_dung"),
    ("Hợp đồng xây nhà trọn gói với tiến độ từng giai đoạn", "xay_dung"),
    ("Thi công hạ tầng giao thông với phạm vi công việc cụ thể", "xay_dung"),
    ("Sửa chữa và cải tạo công trình hiện hữu", "xay_dung"),
    ("Xây dựng theo hình thức khoán gọn bao gồm vật tư", "xay_dung"),
    
    # Vận chuyển
    ("Vận chuyển hàng hóa từ kho đến địa điểm giao hàng", "van_chuyen"),
    ("Hợp đồng logistics với thời gian giao hàng cam kết", "van_chuyen"),
    ("Dịch vụ vận tải đường bộ với trách nhiệm bảo quản", "van_chuyen"),
    ("Chuyển phát nhanh với bảo hiểm hàng hóa", "van_chuyen"),
    ("Vận chuyển hàng container qua cảng biển", "van_chuyen"),
    
    # Cung ứng
    ("Cung cấp nguyên vật liệu theo đơn đặt hàng định kỳ", "cung_ung"),
    ("Hợp đồng cung ứng thiết bị văn phòng hàng tháng", "cung_ung"),
    ("Cung cấp suất ăn công nghiệp cho nhà máy", "cung_ung"),
    ("Cung ứng linh kiện điện tử với thời gian giao hàng", "cung_ung"),
    ("Cung cấp hàng hóa với điều khoản thanh toán công nợ", "cung_ung"),
    
    # Đại lý
    ("Đại lý phân phối sản phẩm trên địa bàn tỉnh thành", "dai_ly"),
    ("Hợp đồng đại diện thương mại với hoa hồng theo doanh thu", "dai_ly"),
    ("Đại lý bán hàng độc quyền khu vực miền Bắc", "dai_ly"),
    ("Thỏa thuận phân phối với mục tiêu doanh số hàng quý", "dai_ly"),
    ("Đại diện bán hàng với hoa hồng và thưởng hiệu quả", "dai_ly"),
    
    # Bảo hiểm
    ("Hợp đồng bảo hiểm nhân thọ với quyền lợi được bảo vệ", "bao_hiem"),
    ("Bảo hiểm xe ô tô bao gồm bắt buộc và tự nguyện", "bao_hiem"),
    ("Bảo hiểm tài sản với phạm vi bồi thường rủi ro", "bao_hiem"),
    ("Bảo hiểm y tế với các gói khám chữa bệnh", "bao_hiem"),
    ("Bảo hiểm trách nhiệm dân sự cho doanh nghiệp", "bao_hiem"),
    
    # Khác
    ("Thỏa thuận hợp tác kinh doanh chia sẻ lợi nhuận", "khac"),
    ("Hợp đồng bảo mật thông tin giữa hai bên", "khac"),
    ("Cam kết không cạnh tranh sau khi chấm dứt quan hệ", "khac"),
    ("Thỏa thuận chuyển giao công nghệ và bí quyết", "khac"),
    ("Hợp đồng nhượng quyền thương hiệu franchise", "khac"),
]

def prepare_training_data():
    """Chuẩn bị dữ liệu training từ training data + MongoDB"""
    print("📚 Chuẩn bị dữ liệu training...")
    
    texts = []
    labels = []
    
    # Thêm training data cơ bản
    for text, label in TRAINING_DATA:
        texts.append(text)
        labels.append(label)
    
    print(f"✅ Đã load {len(texts)} mẫu training data")
    
    # Có thể mở rộng: load từ analysis_history nếu đã có dữ liệu labeled
    try:
        history_collection = db['analysis_history']
        labeled_data = history_collection.find({'contract_type': {'$exists': True, '$ne': ''}})
        
        history_count = 0
        for record in labeled_data:
            if 'ai_analysis' in record and 'contract_type' in record:
                # Lấy summary hoặc một phần analysis
                text_sample = record.get('summary', record.get('ai_analysis', ''))[:500]
                contract_type = record['contract_type']
                
                if contract_type in CONTRACT_CATEGORIES:
                    texts.append(text_sample)
                    labels.append(contract_type)
                    history_count += 1
        
        if history_count > 0:
            print(f"✅ Đã bổ sung {history_count} mẫu từ lịch sử phân tích")
    except Exception as e:
        print(f"⚠️ Không thể load từ history: {e}")
    
    return texts, labels

def train_svm_model():
    """Train SVM model với TF-IDF features"""
    print("\n🚀 Bắt đầu training SVM model...")
    
    # Chuẩn bị dữ liệu
    texts, labels = prepare_training_data()
    
    if len(texts) < 10:
        print("❌ Không đủ dữ liệu để training (cần ít nhất 10 mẫu)")
        return None, None, None
    
    # TF-IDF Vectorization
    print("📊 Tạo TF-IDF features...")
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.9,
        strip_accents='unicode'
    )
    
    X = vectorizer.fit_transform(texts)
    y = np.array(labels)
    
    print(f"📈 Feature matrix shape: {X.shape}")
    print(f"📋 Số lượng categories: {len(set(labels))}")
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train SVM với GridSearch để tìm hyperparameters tốt nhất
    print("🔍 GridSearch để tìm hyperparameters tối ưu...")
    param_grid = {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto']
    }
    
    svm = SVC(probability=True)
    grid_search = GridSearchCV(
        svm, param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    # Best model
    best_model = grid_search.best_estimator_
    print(f"\n✨ Best parameters: {grid_search.best_params_}")
    print(f"✨ Best CV score: {grid_search.best_score_:.4f}")
    
    # Evaluate
    y_pred = best_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n🎯 Test Accuracy: {accuracy:.4f}")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=list(set(labels))))
    
    return best_model, vectorizer, accuracy

def save_model(model, vectorizer, accuracy):
    """Lưu model và vectorizer vào thư mục models/"""
    print("\n💾 Lưu model...")
    
    # Tạo thư mục models nếu chưa có
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Lưu model
    model_path = os.path.join(models_dir, 'svm_contract_classifier.pkl')
    joblib.dump(model, model_path)
    print(f"✅ Đã lưu model: {model_path}")
    
    # Lưu vectorizer
    vectorizer_path = os.path.join(models_dir, 'tfidf_vectorizer.pkl')
    joblib.dump(vectorizer, vectorizer_path)
    print(f"✅ Đã lưu vectorizer: {vectorizer_path}")
    
    # Lưu metadata
    metadata = {
        'accuracy': float(accuracy),
        'categories': CONTRACT_CATEGORIES,
        'trained_date': datetime.now().isoformat(),
        'n_samples': len(TRAINING_DATA),
        'model_type': 'SVM',
        'vectorizer_type': 'TfidfVectorizer'
    }
    
    metadata_path = os.path.join(models_dir, 'model_metadata.pkl')
    joblib.dump(metadata, metadata_path)
    print(f"✅ Đã lưu metadata: {metadata_path}")
    
    return model_path, vectorizer_path, metadata_path

def test_prediction(model, vectorizer):
    """Test model với một số mẫu"""
    print("\n🧪 Test predictions:")
    
    test_samples = [
        "Hai bên thỏa thuận mua bán nhà đất với giá 5 tỷ đồng",
        "Hợp đồng lao động với lương 15 triệu mỗi tháng",
        "Cho thuê căn hộ tại quận 1 với giá 10 triệu/tháng",
        "Vận chuyển hàng từ Hà Nội vào Sài Gòn",
        "Cung cấp dịch vụ tư vấn pháp lý cho doanh nghiệp"
    ]
    
    for text in test_samples:
        X = vectorizer.transform([text])
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        confidence = max(probabilities)
        
        print(f"\nText: {text}")
        print(f"Prediction: {CONTRACT_CATEGORIES[prediction]}")
        print(f"Confidence: {confidence:.2%}")

def main():
    """Main function"""
    print("="*60)
    print("   SVM CONTRACT CLASSIFICATION MODEL TRAINING")
    print("="*60)
    
    # Train model
    model, vectorizer, accuracy = train_svm_model()
    
    if model is None:
        print("❌ Training thất bại!")
        return
    
    # Save model
    model_path, vectorizer_path, metadata_path = save_model(model, vectorizer, accuracy)
    
    # Test predictions
    test_prediction(model, vectorizer)
    
    print("\n" + "="*60)
    print("✅ HOÀN THÀNH TRAINING!")
    print(f"📊 Accuracy: {accuracy:.2%}")
    print(f"📁 Model: {model_path}")
    print(f"📁 Vectorizer: {vectorizer_path}")
    print(f"📁 Metadata: {metadata_path}")
    print("="*60)

if __name__ == '__main__':
    main()
