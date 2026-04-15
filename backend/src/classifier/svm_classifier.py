"""
SVM Text Classification cho phân loại và phân tích hợp đồng pháp lý
Sử dụng TF-IDF vectorization và Support Vector Machine
Optimized: Lazy loading, memory efficient
"""
import os
import numpy as np
from pathlib import Path
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib


class SVMContractClassifier:
    """
    Classifier SVM để phân loại hợp đồng theo:
    - Loại hợp đồng (lao động, mua bán, dịch vụ, ...)
    - Mức độ rủi ro (cao, trung bình, thấp)
    - Vi phạm pháp luật (có/không)
    
    Tối ưu: Lazy loading models, chỉ load khi cần thiết
    """
    
    def __init__(self, model_dir="models/svm"):
        """
        Khởi tạo SVM Classifier với lazy loading
        
        Args:
            model_dir: Thư mục lưu trữ model
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Khởi tạo các components
        self.vectorizer = TfidfVectorizer(
            max_features=3000,  # Giảm từ 5000 -> 3000
            ngram_range=(1, 2),  # Giảm từ (1,3) -> (1,2)
            min_df=2,
            max_df=0.8,
            sublinear_tf=True
        )
        
        self.label_encoder = LabelEncoder()
        
        # SVM models - lazy loading, chỉ load khi invoke method
        self._contract_type_model = None
        self._risk_level_model = None
        self._violation_model = None
        self._risk_label_encoder = None
        
        # Flags để biết model đã được check
        self._checked_contract_type = False
        self._checked_risk = False
        self._checked_violation = False
    
    @property
    def contract_type_model(self):
        """Lazy load contract type model"""
        if not self._checked_contract_type:
            self._load_contract_type_model()
            self._checked_contract_type = True
        return self._contract_type_model
    
    @property
    def risk_level_model(self):
        """Lazy load risk level model"""
        if not self._checked_risk:
            self._load_risk_level_model()
            self._checked_risk = True
        return self._risk_level_model
    
    @property
    def violation_model(self):
        """Lazy load violation model"""
        if not self._checked_violation:
            self._load_violation_model()
            self._checked_violation = True
        return self._violation_model
    
    def _load_contract_type_model(self):
        """Load contract type model từ disk"""
        try:
            vectorizer_path = self.model_dir / "vectorizer.pkl"
            contract_type_path = self.model_dir / "contract_type_model.pkl"
            label_encoder_path = self.model_dir / "label_encoder.pkl"
            
            if vectorizer_path.exists() and contract_type_path.exists():
                self.vectorizer = joblib.load(vectorizer_path)
                self._contract_type_model = joblib.load(contract_type_path)
                if label_encoder_path.exists():
                    self.label_encoder = joblib.load(label_encoder_path)
                print(f"✓ Loaded contract type model")
        except Exception as e:
            print(f"⚠️ Could not load contract type model: {e}")
    
    def _load_risk_level_model(self):
        """Load risk level model từ disk"""
        try:
            risk_level_path = self.model_dir / "risk_level_model.pkl"
            risk_encoder_path = self.model_dir / "risk_label_encoder.pkl"
            
            if risk_level_path.exists():
                self._risk_level_model = joblib.load(risk_level_path)
                if risk_encoder_path.exists():
                    self._risk_label_encoder = joblib.load(risk_encoder_path)
                print(f"✓ Loaded risk level model")
        except Exception as e:
            print(f"⚠️ Could not load risk level model: {e}")
    
    def _load_violation_model(self):
        """Load violation model từ disk"""
        try:
            violation_path = self.model_dir / "violation_model.pkl"
            if violation_path.exists():
                self._violation_model = joblib.load(violation_path)
                print(f"✓ Loaded violation model")
        except Exception as e:
            print(f"⚠️ Could not load violation model: {e}")
    
    def train_contract_type_classifier(self, texts, labels, test_size=0.2, use_grid_search=True):
        """
        Train model phân loại loại hợp đồng
        
        Args:
            texts: List các văn bản hợp đồng
            labels: List nhãn loại hợp đồng (VD: 'labor', 'sales', 'service', ...)
            test_size: Tỷ lệ dữ liệu test
            use_grid_search: Có sử dụng GridSearch để tối ưu hyperparameters
            
        Returns:
            Dictionary chứa metrics và model
        """
        print("\n🚀 BẮT ĐẦU TRAIN MODEL PHÂN LOẠI LOẠI HỢP ĐỒNG...")
        
        # Encode labels
        y = self.label_encoder.fit_transform(labels)
        
        # Vectorize texts
        print("  📊 Vectorizing texts with TF-IDF...")
        X = self.vectorizer.fit_transform(texts)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"  📦 Training set: {X_train.shape[0]} samples")
        print(f"  📦 Test set: {X_test.shape[0]} samples")
        
        
        # Train SVM
        if use_grid_search:
            print("  🔍 Performing GridSearch for optimal hyperparameters...")
            # Giảm search space để nhanh hơn
            param_grid = {
                'C': [1, 10],  # Giảm từ [0.1, 1, 10, 100]
                'kernel': ['linear'],  # Chỉ dùng linear, nhanh hơn rbf
            }
            
            svm = SVC(random_state=42, probability=True)
            grid_search = GridSearchCV(
                svm, param_grid, cv=3, scoring='accuracy', n_jobs=2, verbose=1  # cv=3 thay vì 5, n_jobs=2
            )
            grid_search.fit(X_train, y_train)
            
            self._contract_type_model = grid_search.best_estimator_
            print(f"  ✓ Best parameters: {grid_search.best_params_}")
        else:
            print("  🔧 Training SVM with default parameters...")
            self._contract_type_model = SVC(
                kernel='linear', C=1.0, probability=True, random_state=42
            )
            self._contract_type_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self._contract_type_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ TRAINING COMPLETED!")
        print(f"  🎯 Accuracy: {accuracy:.4f}")
        print("\n📊 Classification Report:")
        print(classification_report(
            y_test, y_pred, 
            target_names=self.label_encoder.classes_
        ))
        
        # Save model
        self._save_models()
        
        return {
            'accuracy': accuracy,
            'model': self._contract_type_model,
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
    
    def train_risk_level_classifier(self, texts, risk_labels, test_size=0.2):
        """
        Train model phân loại mức độ rủi ro
        
        Args:
            texts: List các văn bản hợp đồng
            risk_labels: List nhãn mức độ rủi ro ('high', 'medium', 'low')
            test_size: Tỷ lệ dữ liệu test
            
        Returns:
            Dictionary chứa metrics và model
        """
        print("\n🚀 BẮT ĐẦU TRAIN MODEL PHÂN LOẠI MỨC ĐỘ RỦI RO...")
        
        # Encode labels
        label_encoder_risk = LabelEncoder()
        y = label_encoder_risk.fit_transform(risk_labels)
        
        # Vectorize (sử dụng vectorizer đã fit)
        X = self.vectorizer.transform(texts)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        
        # Train SVM
        print("  🔧 Training SVM for risk level...")
        self._risk_level_model = SVC(
            kernel='linear', C=10.0, probability=True, random_state=42  # Dùng linear thay vì rbf
        )
        self._risk_level_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self._risk_level_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ TRAINING COMPLETED!")
        print(f"  🎯 Accuracy: {accuracy:.4f}")
        print("\n📊 Classification Report:")
        print(classification_report(
            y_test, y_pred, 
            target_names=label_encoder_risk.classes_
        ))
        
        # Save label encoder riêng cho risk
        self._risk_label_encoder = label_encoder_risk
        joblib.dump(label_encoder_risk, self.model_dir / "risk_label_encoder.pkl")
        
        # Save model
        self._save_models()
        
        return {
            'accuracy': accuracy,
            'model': self._risk_level_model,
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'label_encoder': label_encoder_risk
        }
    
    def train_violation_detector(self, texts, violation_labels, test_size=0.2):
        """
        Train model phát hiện vi phạm pháp luật
        
        Args:
            texts: List các văn bản hợp đồng/điều khoản
            violation_labels: List nhãn vi phạm (0: không vi phạm, 1: vi phạm)
            test_size: Tỷ lệ dữ liệu test
            
        Returns:
            Dictionary chứa metrics và model
        """
        print("\n🚀 BẮT ĐẦU TRAIN MODEL PHÁT HIỆN VI PHẠM...")
        
        # Vectorize
        X = self.vectorizer.transform(texts)
        y = np.array(violation_labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        
        # Train SVM
        print("  🔧 Training SVM for violation detection...")
        self._violation_model = SVC(
            kernel='linear', C=1.0, probability=True, 
            class_weight='balanced', random_state=42
        )
        self._violation_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self._violation_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ TRAINING COMPLETED!")
        print(f"  🎯 Accuracy: {accuracy:.4f}")
        print("\n📊 Classification Report:")
        print(classification_report(
            y_test, y_pred, 
            target_names=['No Violation', 'Violation']
        ))
        
        # Save model
        self._save_models()
        
        return {
            'accuracy': accuracy,
            'model': self._violation_model,
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
    
    def predict_contract_type(self, text):
        """
        Dự đoán loại hợp đồng
        
        Args:
            text: Văn bản hợp đồng
            
        Returns:
            Dictionary chứa predicted type và probabilities
        """
        if self.contract_type_model is None:
            raise ValueError("Contract type model chưa được train!")
        
        X = self.vectorizer.transform([text])
        prediction = self.contract_type_model.predict(X)[0]
        probabilities = self.contract_type_model.predict_proba(X)[0]
        
        predicted_type = self.label_encoder.inverse_transform([prediction])[0]
        
        # Tạo dict với probabilities cho tất cả classes
        prob_dict = {
            label: float(prob) 
            for label, prob in zip(self.label_encoder.classes_, probabilities)
        }
        
        return {
            'predicted_type': predicted_type,
            'confidence': float(max(probabilities)),
            'probabilities': prob_dict
        }
    
    def predict_risk_level(self, text):
        """
        Dự đoán mức độ rủi ro
        
        Args:
            text: Văn bản hợp đồng
            
        Returns:
            Dictionary chứa predicted risk level và probabilities
        """
        if self.risk_level_model is None:
            raise ValueError("Risk level model chưa được train!")
        
        # Load risk label encoder
        risk_encoder_path = self.model_dir / "risk_label_encoder.pkl"
        if risk_encoder_path.exists():
            risk_encoder = joblib.load(risk_encoder_path)
        else:
            raise ValueError("Risk label encoder không tồn tại!")
        
        X = self.vectorizer.transform([text])
        prediction = self.risk_level_model.predict(X)[0]
        probabilities = self.risk_level_model.predict_proba(X)[0]
        
        predicted_risk = risk_encoder.inverse_transform([prediction])[0]
        
        # Tạo dict với probabilities cho tất cả classes
        prob_dict = {
            label: float(prob) 
            for label, prob in zip(risk_encoder.classes_, probabilities)
        }
        
        return {
            'predicted_risk': predicted_risk,
            'confidence': float(max(probabilities)),
            'probabilities': prob_dict
        }
    
    def detect_violation(self, text):
        """
        Phát hiện vi phạm pháp luật
        
        Args:
            text: Văn bản điều khoản hợp đồng
            
        Returns:
            Dictionary chứa violation status và probability
        """
        if self.violation_model is None:
            raise ValueError("Violation model chưa được train!")
        
        X = self.vectorizer.transform([text])
        prediction = self.violation_model.predict(X)[0]
        probabilities = self.violation_model.predict_proba(X)[0]
        
        return {
            'has_violation': bool(prediction),
            'violation_probability': float(probabilities[1]),
            'confidence': float(max(probabilities))
        }
    
    def analyze_contract(self, contract_text):
        """
        Phân tích toàn diện hợp đồng sử dụng tất cả các models
        
        Args:
            contract_text: Văn bản hợp đồng đầy đủ
            
        Returns:
            Dictionary chứa tất cả kết quả phân tích
        """
        results = {}
        
        # Phân loại loại hợp đồng
        if self.contract_type_model is not None:
            results['contract_type'] = self.predict_contract_type(contract_text)
        
        # Phân loại mức độ rủi ro
        if self.risk_level_model is not None:
            results['risk_assessment'] = self.predict_risk_level(contract_text)
        
        # Phát hiện vi phạm
        if self.violation_model is not None:
            results['violation_check'] = self.detect_violation(contract_text)
        
        return results
    
    def _save_models(self):
        """Lưu tất cả models và vectorizer"""
        print("\n💾 Saving models...")
        
        joblib.dump(self.vectorizer, self.model_dir / "vectorizer.pkl")
        joblib.dump(self.label_encoder, self.model_dir / "label_encoder.pkl")
        
        if self._contract_type_model is not None:
            joblib.dump(
                self._contract_type_model, 
                self.model_dir / "contract_type_model.pkl"
            )
        
        if self._risk_level_model is not None:
            joblib.dump(
                self._risk_level_model, 
                self.model_dir / "risk_level_model.pkl"
            )
        
        if self._violation_model is not None:
            joblib.dump(
                self._violation_model, 
                self.model_dir / "violation_model.pkl"
            )
        
        print(f"✓ Models saved to {self.model_dir}")
    
    def unload_models(self):
        """Giải phóng memory bằng cách unload models"""
        self._contract_type_model = None
        self._risk_level_model = None
        self._violation_model = None
        print("✓ Models unloaded from memory")
    
    def get_feature_importance(self, top_n=20):
        """
        Lấy các features quan trọng nhất (cho linear SVM)
        
        Args:
            top_n: Số lượng features muốn lấy
            
        Returns:
            Dictionary với feature importance cho mỗi model
        """
        result = {}
        
        if self.contract_type_model is not None and \
           self.contract_type_model.kernel == 'linear':
            feature_names = self.vectorizer.get_feature_names_out()
            coef = self.contract_type_model.coef_
            
            if coef.shape[0] > 1:  # Multi-class
                for idx, class_name in enumerate(self.label_encoder.classes_):
                    top_indices = np.argsort(np.abs(coef[idx]))[-top_n:][::-1]
                    top_features = [(feature_names[i], coef[idx][i]) 
                                   for i in top_indices]
                    result[f'contract_type_{class_name}'] = top_features
            else:  # Binary
                top_indices = np.argsort(np.abs(coef[0]))[-top_n:][::-1]
                top_features = [(feature_names[i], coef[0][i]) 
                               for i in top_indices]
                result['contract_type'] = top_features
        
        return result
