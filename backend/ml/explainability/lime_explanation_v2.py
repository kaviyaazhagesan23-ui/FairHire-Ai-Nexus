import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from lime.lime_text import LimeTextExplainer

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

OUTPUT_PATH = OUTPUT_DIR / "lime_sample_explanation.csv"

# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 LIME EXPLAINABILITY")
print("=" * 70)

# ============================================================
# LOAD MODEL
# ============================================================

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
# PREPARE FEATURES
# ============================================================

print("\nCreating structured features...")

X_structured = create_structured_features(test_df)

X_structured_scaled = scaler.transform(X_structured)

print(
    f"Structured feature shape: {X_structured.shape}"
)

# ============================================================
# TEXT PREDICTION FUNCTION
# ============================================================

def predict_proba_from_text(text_list):

    text_series = pd.Series(
        text_list,
        dtype="object"
    )

    # Create TF-IDF features from perturbed text
    X_text = tfidf.transform(text_series)

    # For LIME text perturbations, use zero structured
    # features so the explanation focuses on text influence.
    #
    # The actual model uses both text and structured features.
    # Therefore we use the mean structured feature vector
    # as a stable reference point.

    mean_structured = np.mean(
        X_structured_scaled,
        axis=0
    )

    structured_matrix = np.tile(
        mean_structured,
        (len(text_list), 1)
    )

    X_final = hstack(
        [
            X_text,
            structured_matrix
        ]
    ).tocsr()

    # LinearSVC does not have predict_proba().
    # We therefore convert its decision score into
    # a probability-like two-class distribution.

    decision_scores = model.decision_function(X_final)

    decision_scores = np.asarray(
        decision_scores
    ).reshape(-1)

    # Stable sigmoid conversion
    strong_probability = (
        1.0
        / (
            1.0
            + np.exp(
                -np.clip(
                    decision_scores,
                    -50,
                    50
                )
            )
        )
    )

    weak_probability = (
        1.0 - strong_probability
    )

    return np.column_stack(
        [
            weak_probability,
            strong_probability
        ]
    )


# ============================================================
# LIME EXPLAINER
# ============================================================

print("\nCreating LIME text explainer...")

explainer = LimeTextExplainer(
    class_names=[
        "Weak Match",
        "Strong Match"
    ],
    random_state=42
)

print("LIME explainer created successfully.")

# ============================================================
# SELECT SAMPLE
# ============================================================

sample_index = 0

sample_row = test_df.iloc[sample_index]

sample_text = create_combined_text(
    test_df.iloc[[sample_index]]
).iloc[0]

# ============================================================
# ACTUAL MODEL PREDICTION
# ============================================================

sample_structured = X_structured_scaled[
    sample_index
].reshape(1, -1)

sample_tfidf = tfidf.transform(
    [sample_text]
)

sample_combined = hstack(
    [
        sample_tfidf,
        sample_structured
    ]
).tocsr()

prediction = model.predict(
    sample_combined
)[0]

decision_score = model.decision_function(
    sample_combined
)[0]

# Convert decision score to probability-like value
strong_probability = (
    1.0
    / (
        1.0
        + np.exp(
            -np.clip(
                decision_score,
                -50,
                50
            )
        )
    )
)

weak_probability = 1.0 - strong_probability

# ============================================================
# GENERATE LIME EXPLANATION
# ============================================================

print("\nGenerating LIME explanation...")

explanation = explainer.explain_instance(
    sample_text,
    predict_proba_from_text,
    num_features=20,
    num_samples=1000
)

# ============================================================
# EXTRACT EXPLANATION
# ============================================================

lime_rows = []

for feature, weight in explanation.as_list():

    if weight > 0:
        direction = "Supports Strong Match"
    else:
        direction = "Supports Weak Match"

    lime_rows.append(
        {
            "feature": feature,
            "weight": float(weight),
            "direction": direction
        }
    )

lime_df = pd.DataFrame(lime_rows)

# Sort by absolute contribution
lime_df["absolute_weight"] = (
    lime_df["weight"].abs()
)

lime_df = lime_df.sort_values(
    "absolute_weight",
    ascending=False
)

lime_df = lime_df.drop(
    columns=["absolute_weight"]
)

# ============================================================
# ADD SAMPLE METADATA
# ============================================================

candidate_name = (
    sample_row["candidate_name"]
    if "candidate_name" in test_df.columns
    else f"Sample {sample_index + 1}"
)

job_role = (
    sample_row["job_role"]
    if "job_role" in test_df.columns
    else "Unknown"
)

actual_label = (
    sample_row["label"]
    if "label" in test_df.columns
    else "Unknown"
)

lime_df.insert(
    0,
    "candidate_name",
    candidate_name
)

lime_df.insert(
    1,
    "job_role",
    job_role
)

lime_df.insert(
    2,
    "actual_label",
    actual_label
)

lime_df.insert(
    3,
    "predicted_label",
    prediction
)

lime_df.insert(
    4,
    "strong_probability",
    round(
        strong_probability * 100,
        2
    )
)

# ============================================================
# SAVE
# ============================================================

lime_df.to_csv(
    OUTPUT_PATH,
    index=False
)

# ============================================================
# DISPLAY
# ============================================================

print("\n" + "=" * 70)
print("LIME INDIVIDUAL RESUME EXPLANATION")
print("=" * 70)

print(
    f"\nCandidate : {candidate_name}"
)

print(
    f"Job Role  : {job_role}"
)

print(
    f"Actual    : {actual_label}"
)

print(
    f"Predicted : {prediction}"
)

print(
    f"Strong Match Probability-like Score : "
    f"{strong_probability * 100:.2f}%"
)

print("\nTop contributing text features:")

print(
    lime_df[
        [
            "feature",
            "weight",
            "direction"
        ]
    ].to_string(
        index=False
    )
)

# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("LIME EXPLAINABILITY COMPLETE")
print("=" * 70)

print("\nSaved file:")
print(OUTPUT_PATH)