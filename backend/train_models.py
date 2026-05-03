"""
Train SVM Models với 10,400 dữ liệu huấn luyện
Train tất cả 3 model: contract type, risk level, violation detection
"""

import json
import os
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from classifier.svm_classifier import SVMContractClassifier

DATA_DIR = "training_data"
MODEL_DIR = "models/svm"

def load_training_data():
    """Load all 10,400 records from JSONL files"""
    print("Loading training data...")
    records = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".jsonl") and fname != "all_contracts.jsonl":
            fpath = os.path.join(DATA_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line.strip())
                        records.append(r)
                    except:
                        continue
    print(f"Loaded {len(records)} records")
    return records

def extract_fields(records):
    """Extract texts and labels from records"""
    texts = []
    contract_types = []
    risk_levels = []
    violations = []

    for r in records:
        text = r.get("text", "")
        if not text or len(text) < 50:
            continue
        texts.append(text)
        contract_types.append(r.get("contract_type", "Unknown"))
        risk_levels.append(r.get("risk_level", "low"))
        violations.append(1 if r.get("has_violation", False) else 0)

    print(f"\nData summary:")
    print(f"  Total valid records: {len(texts)}")

    # Count per type
    from collections import Counter
    ct_counts = Counter(contract_types)
    print(f"\n  Contract type distribution:")
    for ct, cnt in sorted(ct_counts.items()):
        print(f"    {ct}: {cnt}")

    risk_counts = Counter(risk_levels)
    print(f"\n  Risk level distribution:")
    for r, cnt in sorted(risk_counts.items()):
        print(f"    {r}: {cnt}")

    viol_counts = Counter(violations)
    print(f"\n  Violation distribution:")
    print(f"    No violation (0): {viol_counts[0]}")
    print(f"    Violation (1): {viol_counts[1]}")

    return texts, contract_types, risk_levels, violations

def train_all_models():
    """Train all 3 SVM models"""
    start_time = time.time()

    # Load data
    records = load_training_data()
    texts, contract_types, risk_levels, violations = extract_fields(records)

    # Initialize classifier
    classifier = SVMContractClassifier(model_dir=MODEL_DIR)

    # Ensure model directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)

    results = {}

    # 1. Train Contract Type Classifier
    print("\n" + "="*60)
    print("TRAINING MODEL 1: Contract Type Classifier")
    print("="*60)
    t0 = time.time()
    try:
        result1 = classifier.train_contract_type_classifier(
            texts=texts,
            labels=contract_types,
            test_size=0.2,
            use_grid_search=False  # Fast mode
        )
        results["contract_type"] = result1
        print(f"\nContract type training time: {time.time()-t0:.1f}s")
        print(f"Accuracy: {result1['accuracy']:.4f}")
    except Exception as e:
        print(f"ERROR training contract type model: {e}")

    # 2. Train Risk Level Classifier
    print("\n" + "="*60)
    print("TRAINING MODEL 2: Risk Level Classifier")
    print("="*60)
    t0 = time.time()
    try:
        result2 = classifier.train_risk_level_classifier(
            texts=texts,
            risk_labels=risk_levels,
            test_size=0.2
        )
        results["risk_level"] = result2
        print(f"\nRisk level training time: {time.time()-t0:.1f}s")
        print(f"Accuracy: {result2['accuracy']:.4f}")
    except Exception as e:
        print(f"ERROR training risk level model: {e}")

    # 3. Train Violation Detector
    print("\n" + "="*60)
    print("TRAINING MODEL 3: Violation Detector")
    print("="*60)
    t0 = time.time()
    try:
        result3 = classifier.train_violation_detector(
            texts=texts,
            violation_labels=violations,
            test_size=0.2
        )
        results["violation"] = result3
        print(f"\nViolation detector training time: {time.time()-t0:.1f}s")
        print(f"Accuracy: {result3['accuracy']:.4f}")
    except Exception as e:
        print(f"ERROR training violation model: {e}")

    # Save all models
    print("\n" + "="*60)
    print("SAVING ALL MODELS")
    print("="*60)
    try:
        classifier._save_models()
        print("All models saved successfully!")
    except Exception as e:
        print(f"ERROR saving models: {e}")

    # Feature importance
    print("\n" + "="*60)
    print("FEATURE IMPORTANCE (Top 10 per model)")
    print("="*60)
    try:
        features = classifier.get_feature_importance(top_n=10)
        for name, top_feats in features.items():
            print(f"\n{name}:")
            for feat, weight in top_feats[:10]:
                print(f"  {feat}: {weight:.4f}")
    except Exception as e:
        print(f"Could not extract feature importance: {e}")

    # Test predictions
    print("\n" + "="*60)
    print("TEST PREDICTIONS (Sample)")
    print("="*60)
    sample_text = texts[0]
    try:
        pred = classifier.analyze_contract(sample_text)
        print(f"\nSample contract analysis:")
        if "contract_type" in pred:
            print(f"  Contract type: {pred['contract_type']['predicted_type']}")
            print(f"  Confidence: {pred['contract_type']['confidence']:.4f}")
        if "risk_assessment" in pred:
            print(f"  Risk level: {pred['risk_assessment']['predicted_risk']}")
            print(f"  Confidence: {pred['risk_assessment']['confidence']:.4f}")
        if "violation_check" in pred:
            print(f"  Has violation: {pred['violation_check']['has_violation']}")
            print(f"  Violation probability: {pred['violation_check']['violation_probability']:.4f}")
    except Exception as e:
        print(f"ERROR in test prediction: {e}")

    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print("TRAINING COMPLETE!")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"{'='*60}")

    # Save training report
    report = {
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_records": len(texts),
        "total_time_seconds": total_time,
        "results": {
            "contract_type_accuracy": results.get("contract_type", {}).get("accuracy", "N/A"),
            "risk_level_accuracy": results.get("risk_level", {}).get("accuracy", "N/A"),
            "violation_accuracy": results.get("violation", {}).get("accuracy", "N/A"),
        },
        "distribution": {
            "contract_types": dict(Counter(contract_types)),
            "risk_levels": dict(Counter(risk_levels)),
            "violations": dict(Counter(violations)),
        }
    }
    report_path = os.path.join(MODEL_DIR, "training_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nTraining report saved to: {report_path}")

    return results

if __name__ == "__main__":
    print("="*60)
    print("SVM CONTRACT ANALYSIS MODEL TRAINING")
    print(f"Training with 10,400 records from training_data/")
    print("="*60)
    train_all_models()
