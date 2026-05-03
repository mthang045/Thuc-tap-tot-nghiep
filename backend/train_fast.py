"""
Fast Training Script - Optimized for speed
Train SVM models without GridSearch, use LinearSVC for faster training
"""

import json
import os
import sys
import time
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import joblib

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DATA_DIR = "training_data"
MODEL_DIR = "models/svm"
os.makedirs(MODEL_DIR, exist_ok=True)


def load_data():
    print("Loading data...")
    records = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".jsonl") and fname != "all_contracts.jsonl":
            with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line.strip())
                        if r.get("text") and len(r["text"]) > 50:
                            records.append(r)
                    except:
                        pass
    print(f"Loaded {len(records)} records")
    return records


def train_contract_type(records):
    print("\n=== Training Contract Type Classifier ===")
    t0 = time.time()

    texts = [r["text"] for r in records]
    labels = [r["contract_type"] for r in records]

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, max_df=0.8, sublinear_tf=True)
    X = vectorizer.fit_transform(texts)

    # Label encoder
    le = LabelEncoder()
    y = le.fit_transform(labels)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"  Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    print(f"  Classes: {len(le.classes_)}")

    # Train LinearSVC (fast!)
    print("  Training LinearSVC...")
    clf = LinearSVC(C=1.0, max_iter=5000, random_state=42)
    clf.fit(X_train, y_train)

    # Calibrate for probability estimates
    print("  Calibrating for probability estimates...")
    clf = CalibratedClassifierCV(clf, cv=3, method='sigmoid')
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n  ACCURACY: {acc:.4f}")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0))

    # Save
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.pkl"))
    joblib.dump(le, os.path.join(MODEL_DIR, "label_encoder.pkl"))
    joblib.dump(clf, os.path.join(MODEL_DIR, "contract_type_model.pkl"))
    print(f"  Saved to {MODEL_DIR}/contract_type_model.pkl")

    return {"accuracy": acc, "classes": len(le.classes_)}


def train_risk_level(records):
    print("\n=== Training Risk Level Classifier ===")
    t0 = time.time()

    texts = [r["text"] for r in records]
    labels = [r["risk_level"] for r in records]

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, max_df=0.8, sublinear_tf=True)
    X = vectorizer.fit_transform(texts)

    le = LabelEncoder()
    y = le.fit_transform(labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"  Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    print(f"  Classes: {le.classes_}")

    print("  Training LinearSVC...")
    clf = LinearSVC(C=10.0, max_iter=5000, random_state=42)
    clf.fit(X_train, y_train)

    clf = CalibratedClassifierCV(clf, cv=3, method='sigmoid')
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n  ACCURACY: {acc:.4f}")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0))

    joblib.dump(le, os.path.join(MODEL_DIR, "risk_label_encoder.pkl"))
    joblib.dump(clf, os.path.join(MODEL_DIR, "risk_level_model.pkl"))
    print(f"  Saved to {MODEL_DIR}/risk_level_model.pkl")

    return {"accuracy": acc, "classes": le.classes_.tolist()}


def train_violation(records):
    print("\n=== Training Violation Detector ===")
    t0 = time.time()

    texts = [r["text"] for r in records]
    labels = [1 if r.get("has_violation") else 0 for r in records]

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, max_df=0.8, sublinear_tf=True)
    X = vectorizer.fit_transform(texts)
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"  Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    print(f"  Violation ratio: {sum(y_train)}/{len(y_train)}")

    print("  Training LinearSVC (class_weight=balanced)...")
    clf = LinearSVC(C=1.0, max_iter=5000, class_weight='balanced', random_state=42)
    clf.fit(X_train, y_train)

    clf = CalibratedClassifierCV(clf, cv=3, method='sigmoid')
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n  ACCURACY: {acc:.4f}")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Violation", "Violation"], zero_division=0))

    joblib.dump(clf, os.path.join(MODEL_DIR, "violation_model.pkl"))
    print(f"  Saved to {MODEL_DIR}/violation_model.pkl")

    return {"accuracy": acc}


def main():
    print("=" * 60)
    print("FAST SVM MODEL TRAINING")
    print(f"Data: {DATA_DIR} | Models: {MODEL_DIR}")
    print("=" * 60)

    total_start = time.time()
    records = load_data()

    results = {}

    try:
        results["contract_type"] = train_contract_type(records)
    except Exception as e:
        print(f"  ERROR: {e}")

    try:
        results["risk_level"] = train_risk_level(records)
    except Exception as e:
        print(f"  ERROR: {e}")

    try:
        results["violation"] = train_violation(records)
    except Exception as e:
        print(f"  ERROR: {e}")

    total_time = time.time() - total_start

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print("=" * 60)

    for name, result in results.items():
        print(f"  {name}: {result}")

    # Save report
    report = {
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_records": len(records),
        "total_time_seconds": total_time,
        "results": results
    }
    with open(os.path.join(MODEL_DIR, "training_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport saved to {MODEL_DIR}/training_report.json")

    # Quick test
    print("\n--- Quick Test ---")
    try:
        test_text = records[0]["text"]
        vec = joblib.load(os.path.join(MODEL_DIR, "vectorizer.pkl"))
        ct_model = joblib.load(os.path.join(MODEL_DIR, "contract_type_model.pkl"))
        le = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))
        X = vec.transform([test_text])
        pred = le.inverse_transform(ct_model.predict(X))[0]
        prob = max(ct_model.predict_proba(X)[0])
        print(f"  Predicted type: {pred} (prob: {prob:.4f})")
    except Exception as e:
        print(f"  Test error: {e}")


if __name__ == "__main__":
    main()
