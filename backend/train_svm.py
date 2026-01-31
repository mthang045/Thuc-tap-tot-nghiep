"""
Script để train SVM Classifier cho phân loại hợp đồng pháp lý
Sử dụng dữ liệu mẫu để demo
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.classifier import SVMContractClassifier


# ============================================
# DỮ LIỆU MẪU ĐỂ TRAINING
# ============================================

# 1. Dữ liệu phân loại LOẠI HỢP ĐỒNG
CONTRACT_TYPE_SAMPLES = [
    # Hợp đồng lao động
    ("Người lao động cam kết làm việc toàn thời gian từ 8h đến 17h. Mức lương cơ bản 10 triệu đồng, thưởng theo hiệu quả công việc. Thời gian thử việc 2 tháng.", "labor"),
    ("Bên A tuyển dụng Bên B vào vị trí nhân viên kinh doanh với thời hạn hợp đồng 1 năm. Lương khởi điểm 8 triệu, hoa hồng 5% doanh số.", "labor"),
    ("Công ty cam kết trả lương đúng hạn, bảo hiểm xã hội đầy đủ. Người lao động được nghỉ phép 12 ngày/năm.", "labor"),
    ("Thử việc 60 ngày, lương thử việc 85% lương chính thức. Sau thử việc sẽ ký hợp đồng không xác định thời hạn.", "labor"),
    ("Thời gian làm việc 8 tiếng/ngày, 6 ngày/tuần. Làm thêm giờ được trả lương theo quy định pháp luật.", "labor"),
    
    # Hợp đồng mua bán
    ("Bên A đồng ý bán cho Bên B căn nhà số 123 đường XYZ với giá 2 tỷ đồng. Thanh toán 30% khi ký, 70% khi bàn giao.", "sales"),
    ("Sản phẩm bao gồm 100 chiếc laptop với giá 20 triệu/chiếc. Giao hàng trong vòng 15 ngày kể từ ngày ký hợp đồng.", "sales"),
    ("Bên mua cam kết thanh toán đủ số tiền trong vòng 30 ngày. Bên bán chịu trách nhiệm bảo hành 12 tháng.", "sales"),
    ("Chuyển nhượng toàn bộ quyền sở hữu xe ô tô biển số 51A-12345 với giá 500 triệu đồng, thanh toán 1 lần.", "sales"),
    ("Mua bán 1000 tấn gạo xuất khẩu, giá FOB 450 USD/tấn, giao hàng tháng 12/2025.", "sales"),
    
    # Hợp đồng dịch vụ
    ("Bên A cung cấp dịch vụ tư vấn pháp lý cho Bên B với phí 5 triệu/tháng, thời hạn 6 tháng.", "service"),
    ("Dịch vụ bảo trì hệ thống IT trọn gói, phí 10 triệu/tháng, thời gian phản hồi tối đa 4 giờ.", "service"),
    ("Cung cấp dịch vụ thiết kế website với chi phí 30 triệu đồng, hoàn thành trong 45 ngày.", "service"),
    ("Dịch vụ vận chuyển hàng hóa từ Hà Nội đến TP.HCM, giá 2 triệu/chuyến, thanh toán sau khi giao hàng.", "service"),
    ("Hợp đồng thuê văn phòng diện tích 100m2, giá 20 triệu/tháng, thời hạn 2 năm.", "service"),
    
    # Hợp đồng đại lý/phân phối
    ("Bên A chỉ định Bên B là đại lý độc quyền phân phối sản phẩm tại khu vực miền Bắc với chiết khấu 15%.", "distribution"),
    ("Đại lý cam kết đặt hàng tối thiểu 1000 sản phẩm/tháng, được hỗ trợ marketing từ nhà sản xuất.", "distribution"),
    ("Phân phối độc quyền sản phẩm trong 3 năm, doanh số tối thiểu 500 triệu/năm.", "distribution"),
    
    # Hợp đồng xây dựng
    ("Xây dựng nhà cấp 4 diện tích 100m2, tổng giá trị 800 triệu, thời gian thi công 4 tháng.", "construction"),
    ("Bên A thi công hạng mục móng và thô nhà theo bản vẽ thiết kế, thanh toán theo tiến độ.", "construction"),
    ("Sửa chữa, cải tạo nhà cũ với chi phí 200 triệu đồng, bảo hành 2 năm kết cấu.", "construction"),
]

# 2. Dữ liệu phân loại MỨC ĐỘ RỦI RO
RISK_LEVEL_SAMPLES = [
    # Rủi ro cao
    ("Nếu nghỉ việc trước thời hạn phải bồi thường 100 triệu đồng cho công ty.", "high"),
    ("Người lao động làm việc 12 tiếng mỗi ngày không có ngày nghỉ.", "high"),
    ("Lương thử việc chỉ bằng 40% lương chính thức, thời gian thử việc 6 tháng.", "high"),
    ("Công ty không mua bảo hiểm xã hội, bảo hiểm y tế cho người lao động.", "high"),
    ("Nếu vi phạm quy định bảo mật sẽ bị phạt 500 triệu đồng và chịu trách nhiệm hình sự.", "high"),
    ("Toàn bộ tài sản của người lao động làm vật bảo đảm cho hợp đồng.", "high"),
    
    # Rủi ro trung bình
    ("Thời gian thử việc 3 tháng, lương thử việc 80% lương chính thức.", "medium"),
    ("Nếu chấm dứt hợp đồng trước hạn phải báo trước 30 ngày.", "medium"),
    ("Người lao động chịu trách nhiệm bồi thường thiệt hại do lỗi cố ý gây ra.", "medium"),
    ("Công ty có quyền đơn phương chấm dứt hợp đồng nếu nhân viên vi phạm nội quy 3 lần.", "medium"),
    ("Thưởng cuối năm tùy thuộc vào tình hình kinh doanh của công ty.", "medium"),
    
    # Rủi ro thấp
    ("Lương cơ bản 10 triệu, thưởng Tết tối thiểu 1 tháng lương, bảo hiểm đầy đủ.", "low"),
    ("Thời gian làm việc 8 tiếng/ngày, 5 ngày/tuần, nghỉ phép 12 ngày/năm theo quy định.", "low"),
    ("Công ty đóng bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp đầy đủ.", "low"),
    ("Thử việc 60 ngày, lương thử việc 85% lương chính thức.", "low"),
    ("Hai bên có thể chấm dứt hợp đồng bằng thỏa thuận, báo trước 30 ngày.", "low"),
    ("Được hưởng đầy đủ các chế độ theo luật lao động: thai sản, ốm đau, tai nạn lao động.", "low"),
]

# 3. Dữ liệu phát hiện VI PHẠM PHÁP LUẬT
VIOLATION_SAMPLES = [
    # Vi phạm (label = 1)
    ("Thời gian làm việc 14 tiếng mỗi ngày, 7 ngày trong tuần không có ngày nghỉ.", 1),
    ("Lương thử việc 30% lương chính thức.", 1),
    ("Thời gian thử việc 8 tháng.", 1),
    ("Công ty không mua bảo hiểm xã hội cho người lao động.", 1),
    ("Nếu nghỉ việc phải bồi thường gấp 50 lần lương tháng.", 1),
    ("Người lao động không được quyền nghỉ phép trong 2 năm đầu.", 1),
    ("Phạt 10 triệu nếu đi làm muộn quá 3 lần.", 1),
    ("Trừ lương nếu không đạt doanh số bắt buộc.", 1),
    ("Buộc người lao động phải làm thêm giờ không được trả công.", 1),
    ("Công ty giữ bằng cấp, giấy tờ tùy thân của người lao động.", 1),
    
    # Không vi phạm (label = 0)
    ("Thời gian làm việc 8 tiếng/ngày, 6 ngày/tuần theo quy định pháp luật.", 0),
    ("Lương thử việc 85% lương chính thức, thời gian thử việc 60 ngày.", 0),
    ("Công ty đóng đầy đủ bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp.", 0),
    ("Người lao động được nghỉ phép 12 ngày/năm, nghỉ lễ tết theo quy định.", 0),
    ("Làm thêm giờ được trả lương gấp 1.5 lần ngày thường, 2 lần ngày nghỉ.", 0),
    ("Hai bên có thể chấm dứt hợp đồng bằng thỏa thuận, báo trước 30 ngày.", 0),
    ("Thưởng cuối năm tùy theo hiệu quả kinh doanh nhưng tối thiểu 1 tháng lương.", 0),
    ("Được hưởng đầy đủ chế độ thai sản, ốm đau theo luật lao động.", 0),
    ("Công ty cung cấp trang thiết bị làm việc và bảo hộ lao động đầy đủ.", 0),
]


def create_training_data():
    """Tạo dữ liệu training từ samples"""
    
    # Contract Type Data
    contract_texts = [text for text, _ in CONTRACT_TYPE_SAMPLES]
    contract_labels = [label for _, label in CONTRACT_TYPE_SAMPLES]
    
    # Risk Level Data  
    risk_texts = [text for text, _ in RISK_LEVEL_SAMPLES]
    risk_labels = [label for _, label in RISK_LEVEL_SAMPLES]
    
    # Violation Data
    violation_texts = [text for text, _ in VIOLATION_SAMPLES]
    violation_labels = [label for _, label in VIOLATION_SAMPLES]
    
    return {
        'contract_type': (contract_texts, contract_labels),
        'risk_level': (risk_texts, risk_labels),
        'violation': (violation_texts, violation_labels)
    }


def train_all_models():
    """Train tất cả các SVM models"""
    
    print("=" * 60)
    print("🎯 TRAINING SVM CLASSIFIER CHO HỢP ĐỒNG PHÁP LÝ")
    print("=" * 60)
    
    # Khởi tạo classifier
    classifier = SVMContractClassifier(model_dir="models/svm")
    
    # Lấy dữ liệu training
    training_data = create_training_data()
    
    # 1. Train Contract Type Classifier
    print("\n" + "=" * 60)
    contract_texts, contract_labels = training_data['contract_type']
    contract_results = classifier.train_contract_type_classifier(
        contract_texts, 
        contract_labels,
        test_size=0.2,
        use_grid_search=False  # Set True để tìm best params (tốn thời gian hơn)
    )
    
    # 2. Train Risk Level Classifier
    print("\n" + "=" * 60)
    risk_texts, risk_labels = training_data['risk_level']
    risk_results = classifier.train_risk_level_classifier(
        risk_texts,
        risk_labels,
        test_size=0.2
    )
    
    # 3. Train Violation Detector
    print("\n" + "=" * 60)
    violation_texts, violation_labels = training_data['violation']
    violation_results = classifier.train_violation_detector(
        violation_texts,
        violation_labels,
        test_size=0.2
    )
    
    print("\n" + "=" * 60)
    print("✅ ĐÃ HOÀN TẤT TRAINING TẤT CẢ MODELS!")
    print("=" * 60)
    
    # Summary
    print("\n📊 TỔNG KẾT KẾT QUẢ:")
    print(f"  Contract Type Accuracy: {contract_results['accuracy']:.4f}")
    print(f"  Risk Level Accuracy: {risk_results['accuracy']:.4f}")
    print(f"  Violation Detection Accuracy: {violation_results['accuracy']:.4f}")
    
    return classifier


def test_predictions(classifier):
    """Test các predictions với dữ liệu mẫu"""
    
    print("\n" + "=" * 60)
    print("🧪 TESTING PREDICTIONS")
    print("=" * 60)
    
    # Test 1: Hợp đồng lao động có vấn đề
    test_contract_1 = """
    Người lao động làm việc 10 tiếng mỗi ngày, từ thứ 2 đến thứ 7.
    Lương thử việc 3 tháng hưởng 70% lương chính thức.
    Nếu nghỉ việc trước 1 năm phải bồi thường 30 triệu đồng.
    """
    
    print("\n📄 Test Contract 1:")
    print(test_contract_1)
    print("\n🔍 Kết quả phân tích:")
    results_1 = classifier.analyze_contract(test_contract_1)
    
    if 'contract_type' in results_1:
        ct = results_1['contract_type']
        print(f"  Loại hợp đồng: {ct['predicted_type']} (confidence: {ct['confidence']:.2%})")
    
    if 'risk_assessment' in results_1:
        ra = results_1['risk_assessment']
        print(f"  Mức độ rủi ro: {ra['predicted_risk']} (confidence: {ra['confidence']:.2%})")
    
    if 'violation_check' in results_1:
        vc = results_1['violation_check']
        print(f"  Vi phạm: {'Có' if vc['has_violation'] else 'Không'} (probability: {vc['violation_probability']:.2%})")
    
    # Test 2: Hợp đồng mua bán
    test_contract_2 = """
    Bên A bán cho Bên B căn nhà 3 tầng tại 123 đường ABC với giá 3 tỷ đồng.
    Thanh toán 40% khi ký hợp đồng, 60% khi bàn giao nhà.
    Bàn giao trong vòng 30 ngày kể từ ngày thanh toán đợt 1.
    """
    
    print("\n" + "-" * 60)
    print("📄 Test Contract 2:")
    print(test_contract_2)
    print("\n🔍 Kết quả phân tích:")
    results_2 = classifier.analyze_contract(test_contract_2)
    
    if 'contract_type' in results_2:
        ct = results_2['contract_type']
        print(f"  Loại hợp đồng: {ct['predicted_type']} (confidence: {ct['confidence']:.2%})")
    
    if 'risk_assessment' in results_2:
        ra = results_2['risk_assessment']
        print(f"  Mức độ rủi ro: {ra['predicted_risk']} (confidence: {ra['confidence']:.2%})")
    
    if 'violation_check' in results_2:
        vc = results_2['violation_check']
        print(f"  Vi phạm: {'Có' if vc['has_violation'] else 'Không'} (probability: {vc['violation_probability']:.2%})")
    
    # Test 3: Điều khoản vi phạm rõ ràng
    test_clause = "Người lao động làm việc 14 tiếng mỗi ngày, không có ngày nghỉ, lương thử việc 6 tháng hưởng 40%."
    
    print("\n" + "-" * 60)
    print("📄 Test Clause (Vi phạm):")
    print(test_clause)
    print("\n🔍 Kết quả kiểm tra vi phạm:")
    violation_result = classifier.detect_violation(test_clause)
    print(f"  Vi phạm: {'Có' if violation_result['has_violation'] else 'Không'}")
    print(f"  Xác suất vi phạm: {violation_result['violation_probability']:.2%}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Train models
    classifier = train_all_models()
    
    # Test predictions
    test_predictions(classifier)
    
    print("\n✅ Hoàn tất! Models đã được lưu tại: models/svm/")
