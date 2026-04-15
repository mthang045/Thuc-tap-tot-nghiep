"""
SVM và RAG Model Loaders
Wrapper classes để load và sử dụng models đã train
"""

import os
import joblib
from pathlib import Path


class SVMContractClassifierV2:
    """
    Load và sử dụng SVM model đã train để classify loại hợp đồng
    """
    
    def __init__(self, model_dir='models'):
        """Initialize với đường dẫn đến models directory"""
        self.model_dir = Path(model_dir)
        self.model = None
        self.vectorizer = None
        self.metadata = None
        self.categories = None
        
        self._load_models()
    
    def _load_models(self):
        """Load SVM model, vectorizer và metadata"""
        try:
            model_path = self.model_dir / 'svm_contract_classifier.pkl'
            vectorizer_path = self.model_dir / 'tfidf_vectorizer.pkl'
            metadata_path = self.model_dir / 'model_metadata.pkl'
            
            if not model_path.exists():
                print(f"⚠️ SVM model không tồn tại: {model_path}")
                print(f"💡 Chạy: python train_svm_model.py để train model")
                return
            
            # Load model
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.metadata = joblib.load(metadata_path)
            self.categories = self.metadata.get('categories', {})
            
            print(f"✅ Loaded SVM model (accuracy: {self.metadata.get('accuracy', 0):.2%})")
            
        except Exception as e:
            print(f"❌ Không thể load SVM model: {e}")
    
    def classify(self, text: str):
        """
        Phân loại hợp đồng
        
        Args:
            text: Nội dung hợp đồng
            
        Returns:
            dict với category, label và confidence
        """
        if self.model is None:
            return {
                'success': False,
                'error': 'Model not loaded',
                'category_code': 'khac',
                'category_name': 'Hợp đồng khác',
                'confidence': 0.0
            }
        
        try:
            # Transform text
            X = self.vectorizer.transform([text])
            
            # Predict
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            confidence = float(max(probabilities))
            
            # Get category name
            category_name = self.categories.get(prediction, 'Unknown')
            
            return {
                'success': True,
                'category_code': prediction,
                'category_name': category_name,
                'confidence': confidence,
                'all_scores': {
                    self.categories.get(cat, cat): float(prob)
                    for cat, prob in zip(self.model.classes_, probabilities)
                }
            }
            
        except Exception as e:
            print(f"❌ Classification error: {e}")
            return {
                'success': False,
                'error': str(e),
                'category_code': 'khac',
                'category_name': 'Hợp đồng khác',
                'confidence': 0.0
            }
    
    def is_loaded(self):
        """Check if model đã được load thành công"""
        return self.model is not None


# Global instances (lazy loading)
_svm_classifier = None


def get_svm_classifier():
    """Get global SVM classifier instance"""
    global _svm_classifier
    if _svm_classifier is None:
        _svm_classifier = SVMContractClassifierV2()
    return _svm_classifier
