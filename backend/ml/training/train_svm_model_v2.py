import sys

from pathlib import Path
import joblib
import pandas as pd
import numpy as np

from scipy.sparse import hstack, csr_matrix

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parents[2]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml.prediction.feature_engineering import (
    create_structured_features,
    create_combined_text,
    FEATURE_COLUMNS,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TRAIN_PATH = (
    BASE_DIR.parent
    / "dataset"
    / "processed"
    / "splits_v2"
    / "train.csv"
)

VAL_PATH = (
    BASE_DIR.parent
    / "dataset"
    / "processed"
    / "splits_v2"
    / "validation.csv"
)

MODEL_DIR = BASE_DIR.parent / "models"

MODEL_PATH = MODEL_DIR / "fairhire_svm_model_v2.joblib"
TFIDF_PATH = MODEL_DIR / "fairhire_svm_tfidf_v2.joblib"
SCALER_PATH = MODEL_DIR / "fairhire_svm_scaler_v2.joblib"
FEATURE_COLUMNS_PATH = (
    MODEL_DIR / "fairhire_svm_feature_columns_v2.joblib"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 LINEAR SVM TRAINING")
print("=" * 70)

print("\nLoading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
val_df = pd.read_csv(VAL_PATH)

print(f"Training rows   : {len(train_df)}")
print(f"Validation rows : {len(val_df)}")


# ============================================================
# LABELS
# ============================================================

y_train = train_df["label"]
y_val = val_df["label"]

print("\nTraining label distribution:")
print(y_train.value_counts())

print("\nValidation label distribution:")
print(y_val.value_counts())


# ============================================================
# TF-IDF
# ============================================================

print("\nCreating TF-IDF features...")

tfidf = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True,
)

train_text = create_combined_text(train_df)
val_text = create_combined_text(val_df)

X_train_tfidf = tfidf.fit_transform(train_text)
X_val_tfidf = tfidf.transform(val_text)

print(
    f"Training TF-IDF shape   : {X_train_tfidf.shape}"
)

print(
    f"Validation TF-IDF shape : {X_val_tfidf.shape}"
)


# ============================================================
# STRUCTURED FEATURES
# ============================================================

print("\nCreating structured matching features...")

train_structured = create_structured_features(train_df)
val_structured = create_structured_features(val_df)

print(
    f"Training structured shape   : {train_structured.shape}"
)

print(
    f"Validation structured shape : {val_structured.shape}"
)


# ============================================================
# SCALE STRUCTURED FEATURES
# ============================================================

print("\nScaling structured features...")

scaler = StandardScaler()

X_train_structured = scaler.fit_transform(
    train_structured[FEATURE_COLUMNS]
)

X_val_structured = scaler.transform(
    val_structured[FEATURE_COLUMNS]
)


# ============================================================
# COMBINE FEATURES
# ============================================================

print("\nCombining TF-IDF + structured features...")

X_train = hstack(
    [
        X_train_tfidf,
        csr_matrix(X_train_structured),
    ]
).tocsr()

X_val = hstack(
    [
        X_val_tfidf,
        csr_matrix(X_val_structured),
    ]
).tocsr()

print(
    f"Final training shape   : {X_train.shape}"
)

print(
    f"Final validation shape : {X_val.shape}"
)


# ============================================================
# TRAIN LINEAR SVM
# ============================================================

print("\nTraining Linear SVM...")

svm_model = LinearSVC(
    C=1.0,
    class_weight="balanced",
    random_state=42,
    max_iter=5000,
)

svm_model.fit(
    X_train,
    y_train,
)

print("Linear SVM training complete.")


# ============================================================
# VALIDATION PREDICTIONS
# ============================================================

print("\nGenerating validation predictions...")

y_pred = svm_model.predict(X_val)


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(
    y_val,
    y_pred,
)

precision = precision_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)

recall = recall_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)

f1 = f1_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("V2 LINEAR SVM VALIDATION RESULTS")
print("=" * 70)

print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Accuracy  : {accuracy * 100:.2f}%")

print(f"\nPrecision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\n" + "-" * 70)
print("CONFUSION MATRIX")
print("-" * 70)

cm = confusion_matrix(
    y_val,
    y_pred,
    labels=[
        "Weak Match",
        "Strong Match",
    ],
)

print("\n                    Predicted")
print("                 Weak    Strong")
print(
    f"Actual Weak      {cm[0][0]:4d}    {cm[0][1]:4d}"
)
print(
    f"Actual Strong    {cm[1][0]:4d}    {cm[1][1]:4d}"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n" + "-" * 70)
print("CLASSIFICATION REPORT")
print("-" * 70)

print(
    classification_report(
        y_val,
        y_pred,
        labels=[
            "Weak Match",
            "Strong Match",
        ],
        digits=4,
    )
)


# ============================================================
# SAVE ARTIFACTS
# ============================================================

print("\nSaving SVM model artifacts...")

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

joblib.dump(
    svm_model,
    MODEL_PATH,
)

joblib.dump(
    tfidf,
    TFIDF_PATH,
)

joblib.dump(
    scaler,
    SCALER_PATH,
)

joblib.dump(
    FEATURE_COLUMNS,
    FEATURE_COLUMNS_PATH,
)

print("\nSaved:")

print(
    f"Model          : {MODEL_PATH}"
)

print(
    f"TF-IDF         : {TFIDF_PATH}"
)

print(
    f"Scaler         : {SCALER_PATH}"
)

print(
    f"Feature columns: {FEATURE_COLUMNS_PATH}"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("V2 LINEAR SVM TRAINING COMPLETE")
print("=" * 70)