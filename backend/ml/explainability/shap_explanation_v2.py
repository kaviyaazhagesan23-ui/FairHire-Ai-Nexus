import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from scipy.sparse import hstack

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
    FEATURE_COLUMNS,
)

# ============================================================
# PATHS
# ============================================================

MODEL_PATH = PROJECT_ROOT / "models" / "fairhire_svm_model_v2.joblib"
TFIDF_PATH = PROJECT_ROOT / "models" / "fairhire_svm_tfidf_v2.joblib"
SCALER_PATH = PROJECT_ROOT / "models" / "fairhire_svm_scaler_v2.joblib"

TEST_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "processed"
    / "splits_v2"
    / "test.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "docs" / "explainability"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD ARTIFACTS
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 SHAP EXPLAINABILITY")
print("=" * 70)

print("\nLoading saved SVM model artifacts...")

model = joblib.load(MODEL_PATH)
tfidf = joblib.load(TFIDF_PATH)
scaler = joblib.load(SCALER_PATH)

print("Model loaded successfully.")
print("TF-IDF vectorizer loaded.")
print("Scaler loaded.")

# ============================================================
# LOAD TEST DATA
# ============================================================

print("\nLoading test dataset...")

test_df = pd.read_csv(TEST_PATH)

print(f"Test rows: {len(test_df)}")

# ============================================================
# CREATE FEATURES
# ============================================================

print("\nCreating TF-IDF features...")

combined_text = create_combined_text(test_df)

X_tfidf = tfidf.transform(combined_text)

print(f"TF-IDF shape: {X_tfidf.shape}")

print("\nCreating structured features...")

X_structured = create_structured_features(test_df)

X_structured_scaled = scaler.transform(X_structured)

print(f"Structured shape: {X_structured.shape}")

print("\nCombining features...")

X_combined = hstack(
    [
        X_tfidf,
        X_structured_scaled
    ]
).tocsr()

print(f"Combined shape: {X_combined.shape}")

# ============================================================
# FEATURE NAMES
# ============================================================

tfidf_feature_names = list(tfidf.get_feature_names_out())

feature_names = (
    tfidf_feature_names
    + list(FEATURE_COLUMNS)
)

print(f"\nTotal feature names: {len(feature_names)}")

# ============================================================
# SHAP EXPLAINER
# ============================================================

print("\nCreating SHAP LinearExplainer...")

explainer = shap.LinearExplainer(
    model,
    X_combined
)

print("SHAP explainer created successfully.")

# ============================================================
# CALCULATE SHAP VALUES
# ============================================================

print("\nCalculating SHAP values...")

# Explain a manageable subset for development
N_EXPLANATIONS = min(100, X_combined.shape[0])

X_sample = X_combined[:N_EXPLANATIONS]

shap_values = explainer.shap_values(X_sample)

print(f"SHAP values calculated for {N_EXPLANATIONS} samples.")

# ============================================================
# GLOBAL FEATURE IMPORTANCE
# ============================================================

print("\nCalculating global feature importance...")

mean_abs_shap = np.mean(
    np.abs(shap_values),
    axis=0
)

importance_df = pd.DataFrame(
    {
        "feature": feature_names,
        "mean_abs_shap": mean_abs_shap,
    }
)

importance_df = importance_df.sort_values(
    "mean_abs_shap",
    ascending=False
)

global_output = OUTPUT_DIR / "shap_global_feature_importance.csv"

importance_df.to_csv(
    global_output,
    index=False
)

# ============================================================
# PRINT TOP FEATURES
# ============================================================

print("\n" + "=" * 70)
print("TOP 20 GLOBAL SHAP FEATURES")
print("=" * 70)

print(
    importance_df.head(20).to_string(
        index=False
    )
)

# ============================================================
# STRUCTURED FEATURE IMPORTANCE
# ============================================================

structured_importance = importance_df[
    importance_df["feature"].isin(FEATURE_COLUMNS)
].copy()

structured_output = (
    OUTPUT_DIR
    / "shap_structured_feature_importance.csv"
)

structured_importance.to_csv(
    structured_output,
    index=False
)

print("\n" + "=" * 70)
print("STRUCTURED FEATURE IMPORTANCE")
print("=" * 70)

print(
    structured_importance.to_string(
        index=False
    )
)

# ============================================================
# INDIVIDUAL EXPLANATION
# ============================================================

sample_index = 0

sample_row = test_df.iloc[sample_index]

sample_shap = shap_values[sample_index]

top_indices = np.argsort(
    np.abs(sample_shap)
)[::-1][:20]

individual_rows = []

for idx in top_indices:

    value = sample_shap[idx]

    individual_rows.append(
        {
            "feature": feature_names[idx],
            "shap_value": float(value),
            "direction": (
                "Supports Strong Match"
                if value > 0
                else "Supports Weak Match"
            ),
        }
    )

individual_df = pd.DataFrame(individual_rows)

individual_output = (
    OUTPUT_DIR
    / "shap_sample_explanation.csv"
)

individual_df.to_csv(
    individual_output,
    index=False
)

# ============================================================
# SAMPLE INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE RESUME EXPLANATION")
print("=" * 70)

if "candidate_name" in test_df.columns:
    print(
        f"Candidate: {sample_row['candidate_name']}"
    )

if "job_role" in test_df.columns:
    print(
        f"Job Role: {sample_row['job_role']}"
    )

if "label" in test_df.columns:
    print(
        f"Actual Label: {sample_row['label']}"
    )

predicted_label = model.predict(
    X_combined[sample_index]
)[0]

print(
    f"Predicted Label: {predicted_label}"
)

print("\nTop contributing features:")

print(
    individual_df.to_string(
        index=False
    )
)

# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("SHAP EXPLAINABILITY COMPLETE")
print("=" * 70)

print("\nSaved files:")

print(global_output)
print(structured_output)
print(individual_output)