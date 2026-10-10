import sys
from pathlib import Path

import joblib
import pandas as pd
import shap
from scipy.sparse import hstack, csr_matrix


# ============================================================
# PATHS
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]

MODEL_DIR = PROJECT_ROOT / "models"

TEST_DATA_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "processed"
    / "splits_v2"
    / "test.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "docs"
    / "explainability"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "shap_candidate_explanations_v2.csv"
)


MODEL_PATH = MODEL_DIR / "fairhire_svm_model_v2.joblib"
TFIDF_PATH = MODEL_DIR / "fairhire_svm_tfidf_v2.joblib"
SCALER_PATH = MODEL_DIR / "fairhire_svm_scaler_v2.joblib"
FEATURE_COLUMNS_PATH = (
    MODEL_DIR
    / "fairhire_svm_feature_columns_v2.joblib"
)


# ============================================================
# BACKEND PATH
# ============================================================

BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from ml.prediction.feature_engineering import (
    create_structured_features,
    create_combined_text,
)


# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 CANDIDATE SHAP EXPLANATIONS")
print("=" * 70)

print("\nLoading saved SVM artifacts...")

svm_model = joblib.load(MODEL_PATH)
tfidf = joblib.load(TFIDF_PATH)
scaler = joblib.load(SCALER_PATH)
feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

print("SVM model loaded.")
print("TF-IDF vectorizer loaded.")
print("Scaler loaded.")
print("Feature columns loaded.")


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\nLoading test dataset...")

df = pd.read_csv(TEST_DATA_PATH)

print(f"Test candidates: {len(df)}")

if "candidate_name" not in df.columns:
    raise ValueError(
        "candidate_name column not found in test dataset."
    )

if "job_role" not in df.columns:
    raise ValueError(
        "job_role column not found in test dataset."
    )

if "label" not in df.columns:
    raise ValueError(
        "label column not found in test dataset."
    )


# ============================================================
# CREATE MODEL FEATURES
# ============================================================

print("\nCreating model features...")

combined_text = create_combined_text(df)

tfidf_features = tfidf.transform(combined_text)

structured_features = create_structured_features(df)

structured_features = structured_features[
    feature_columns
]

scaled_structured_features = scaler.transform(
    structured_features
)

final_features = hstack(
    [
        tfidf_features,
        csr_matrix(scaled_structured_features),
    ]
).tocsr()

print(
    f"Final feature shape: {final_features.shape}"
)


# ============================================================
# FEATURE NAMES
# ============================================================

tfidf_feature_names = list(
    tfidf.get_feature_names_out()
)

structured_feature_names = list(
    feature_columns
)

feature_names = (
    tfidf_feature_names
    + structured_feature_names
)

print(
    f"Total feature names: {len(feature_names)}"
)


# ============================================================
# PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

predictions = svm_model.predict(
    final_features
)

decision_scores = svm_model.decision_function(
    final_features
)

print(
    f"Predictions generated: {len(predictions)}"
)


# ============================================================
# SHAP EXPLAINER
# ============================================================

print("\nCreating SHAP LinearExplainer...")

# Use a small background sample to keep explanation
# computation practical while preserving the real model
# feature space.

background_size = min(
    100,
    final_features.shape[0],
)

background = final_features[
    :background_size
]

explainer = shap.LinearExplainer(
    svm_model,
    background,
)

print("SHAP LinearExplainer created.")


# ============================================================
# GENERATE SHAP VALUES
# ============================================================

print("\nGenerating SHAP values...")

shap_values = explainer(
    final_features
)

values = shap_values.values

print(
    f"SHAP value matrix shape: {values.shape}"
)


# ============================================================
# OUTPUT RECORDS
# ============================================================

records = []

TOP_FEATURES = 20


for index in range(len(df)):

    candidate_name = str(
        df.iloc[index]["candidate_name"]
    )

    job_role = str(
        df.iloc[index]["job_role"]
    )

    actual_label = str(
        df.iloc[index]["label"]
    )

    predicted_label = str(
        predictions[index]
    )

    candidate_shap_values = values[index]

    # Sort by absolute SHAP contribution
    top_indices = sorted(
        range(len(candidate_shap_values)),
        key=lambda i: abs(
            candidate_shap_values[i]
        ),
        reverse=True,
    )[:TOP_FEATURES]

    for feature_index in top_indices:

        shap_value = float(
            candidate_shap_values[
                feature_index
            ]
        )

        if shap_value >= 0:
            direction = "Supports Strong Match"
        else:
            direction = "Supports Weak Match"

        records.append(
            {
                "candidate_name": candidate_name,
                "job_role": job_role,
                "actual_label": actual_label,
                "predicted_label": predicted_label,
                "decision_score": float(
                    decision_scores[index]
                ),
                "feature": feature_names[
                    feature_index
                ],
                "shap_value": shap_value,
                "direction": direction,
            }
        )


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

output_df = pd.DataFrame(records)

output_df.to_csv(
    OUTPUT_PATH,
    index=False,
)

print("\n" + "=" * 70)
print("CANDIDATE SHAP GENERATION COMPLETE")
print("=" * 70)

print(
    f"\nCandidates explained: {len(df)}"
)

print(
    f"Explanation records: {len(output_df)}"
)

print(
    f"\nSaved file:\n{OUTPUT_PATH}"
)


# ============================================================
# VERIFY CANDIDATE 1562
# ============================================================

candidate_1562 = output_df[
    output_df["candidate_name"]
    == "Candidate 1562"
]

print("\n" + "=" * 70)
print("CANDIDATE 1562 VERIFICATION")
print("=" * 70)

if candidate_1562.empty:

    print(
        "ERROR: Candidate 1562 was not found."
    )

else:

    print(
        f"Candidate: "
        f"{candidate_1562.iloc[0]['candidate_name']}"
    )

    print(
        f"Job Role: "
        f"{candidate_1562.iloc[0]['job_role']}"
    )

    print(
        f"Prediction: "
        f"{candidate_1562.iloc[0]['predicted_label']}"
    )

    print("\nTop SHAP features:")

    print(
        candidate_1562[
            [
                "feature",
                "shap_value",
                "direction",
            ]
        ].to_string(index=False)
    )

print("\nDone.")