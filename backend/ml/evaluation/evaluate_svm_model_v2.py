from pathlib import Path
import sys
import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# ============================================================
# PATH SETUP
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parents[2]
PROJECT_ROOT = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml.prediction.feature_engineering import (
    create_structured_features,
    create_combined_text,
)


# ============================================================
# PATHS
# ============================================================

TEST_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "processed"
    / "splits_v2"
    / "test.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"

MODEL_PATH = MODEL_DIR / "fairhire_svm_model_v2.joblib"
TFIDF_PATH = MODEL_DIR / "fairhire_svm_tfidf_v2.joblib"
SCALER_PATH = MODEL_DIR / "fairhire_svm_scaler_v2.joblib"


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 LINEAR SVM TEST EVALUATION")
print("=" * 70)


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\nLoading test dataset...")

test_df = pd.read_csv(TEST_PATH)

print(f"Test rows : {len(test_df)}")

print("\nTest label distribution:")
print(test_df["label"].value_counts())


# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================

print("\nLoading saved SVM model artifacts...")

model = joblib.load(MODEL_PATH)
tfidf = joblib.load(TFIDF_PATH)
scaler = joblib.load(SCALER_PATH)

print("Model loaded successfully.")


# ============================================================
# CREATE TF-IDF FEATURES
# ============================================================

print("\nCreating TF-IDF features...")

test_text = create_combined_text(test_df)

X_test_tfidf = tfidf.transform(test_text)

print(f"Test TF-IDF shape : {X_test_tfidf.shape}")


# ============================================================
# CREATE STRUCTURED FEATURES
# ============================================================

print("\nCreating structured matching features...")

X_test_structured = create_structured_features(test_df)

print(f"Test structured shape : {X_test_structured.shape}")


# ============================================================
# SCALE STRUCTURED FEATURES
# ============================================================

print("\nScaling structured features...")

X_test_structured_scaled = scaler.transform(X_test_structured)


# ============================================================
# COMBINE FEATURES
# ============================================================

print("\nCombining TF-IDF + structured features...")

from scipy.sparse import hstack

X_test = hstack(
    [
        X_test_tfidf,
        X_test_structured_scaled,
    ]
)

print(f"Final test shape : {X_test.shape}")


# ============================================================
# GENERATE PREDICTIONS
# ============================================================

print("\nGenerating test predictions...")

y_test = test_df["label"]
y_pred = model.predict(X_test)


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    pos_label="Strong Match",
)

recall = recall_score(
    y_test,
    y_pred,
    pos_label="Strong Match",
)

f1 = f1_score(
    y_test,
    y_pred,
    pos_label="Strong Match",
)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("V2 LINEAR SVM TEST RESULTS")
print("=" * 70)

print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Accuracy  : {accuracy * 100:.2f}%")

print(f"\nPrecision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=["Weak Match", "Strong Match"],
)

print("\n" + "-" * 70)
print("CONFUSION MATRIX")
print("-" * 70)

print("""
                    Predicted
                 Weak    Strong
Actual Weak      {:4d}    {:4d}
Actual Strong    {:4d}    {:4d}
""".format(
    cm[0][0],
    cm[0][1],
    cm[1][0],
    cm[1][1],
))


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("-" * 70)
print("CLASSIFICATION REPORT")
print("-" * 70)

print(
    classification_report(
        y_test,
        y_pred,
        labels=["Weak Match", "Strong Match"],
    )
)


# ============================================================
# SAMPLE PREDICTIONS
# ============================================================

print("-" * 70)
print("SAMPLE TEST PREDICTIONS")
print("-" * 70)

sample_df = test_df[
    [
        "candidate_name",
        "job_role",
        "label",
    ]
].copy()

sample_df["predicted_label"] = y_pred

print(sample_df.head(15).to_string(index=False))


print("\n" + "=" * 70)
print("V2 LINEAR SVM TEST EVALUATION COMPLETE")
print("=" * 70)