import sys
from pathlib import Path

import joblib
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from lime.lime_text import LimeTextExplainer


# ============================================================
# PATHS
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
MODEL_DIR = PROJECT_ROOT / "models"

OUTPUT_DIR = PROJECT_ROOT / "docs" / "explainability"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEST_DATA_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "processed"
    / "splits_v2"
    / "test.csv"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "lime_candidate_explanations_v2.csv"
)


# ============================================================
# PYTHON PATH
# ============================================================

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from ml.prediction.feature_engineering import (
    create_structured_features,
)


# ============================================================
# MODEL PATHS
# ============================================================

MODEL_PATH = MODEL_DIR / "fairhire_svm_model_v2.joblib"
TFIDF_PATH = MODEL_DIR / "fairhire_svm_tfidf_v2.joblib"
SCALER_PATH = MODEL_DIR / "fairhire_svm_scaler_v2.joblib"
FEATURE_COLUMNS_PATH = (
    MODEL_DIR / "fairhire_svm_feature_columns_v2.joblib"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 CANDIDATE LIME EXPLANATIONS")
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

test_df = pd.read_csv(TEST_DATA_PATH)

print(f"Test candidates: {len(test_df)}")


# ============================================================
# CREATE BASE STRUCTURED FEATURES
# ============================================================

print("\nCreating structured features...")

structured_df = create_structured_features(test_df)
structured_df = structured_df[feature_columns]

scaled_structured = scaler.transform(structured_df)
scaled_structured_sparse = csr_matrix(scaled_structured)

print(
    f"Structured feature shape: "
    f"{scaled_structured_sparse.shape}"
)


# ============================================================
# LIME EXPLAINER
# ============================================================

explainer = LimeTextExplainer(
    class_names=["Weak Match", "Strong Match"],
    random_state=42,
)


# ============================================================
# HELPER: BUILD MODEL FEATURES
# ============================================================
def build_features_from_text(text_list, row_index):
    """
    Build the exact SVM feature representation while allowing
    LIME to perturb only the text component.

    Structured candidate features remain fixed for the candidate.
    """

    text_series = pd.Series(
        text_list,
        dtype="object"
    )

    tfidf_features = tfidf.transform(text_series)

    candidate_structured = (
        scaled_structured_sparse[row_index]
    )

    # Repeat the candidate's structured feature row
    # for every LIME-generated text sample.
    repeated_structured = csr_matrix(
        candidate_structured.toarray().repeat(
            len(text_list),
            axis=0
        )
    )

    final_features = hstack(
        [
            tfidf_features,
            repeated_structured,
        ]
    ).tocsr()

    return final_features
# ============================================================
# LIME PREDICTION FUNCTION
# ============================================================

def create_predict_function(row_index):
    """
    Create a prediction function for one candidate.

    LIME modifies the candidate's combined text while the
    candidate's structured features remain fixed.
    """

    def predict_fn(text_list):

        final_features = build_features_from_text(
            text_list,
            row_index,
        )

        decision_scores = svm_model.decision_function(
            final_features
        )

        # LinearSVC does not provide probabilities.
        # Convert decision scores into a two-class probability-like
        # distribution only for LIME's explanation interface.
        #
        # These are NOT true model probabilities.
        import numpy as np

        positive_probability = 1.0 / (
            1.0 + np.exp(-decision_scores)
        )

        negative_probability = 1.0 - positive_probability

        return np.column_stack(
            [
                negative_probability,
                positive_probability,
            ]
        )

    return predict_fn


# ============================================================
# GENERATE LIME EXPLANATIONS
# ============================================================

all_records = []

total_candidates = len(test_df)

print("\nGenerating candidate-specific LIME explanations...")
print(
    f"Candidates to explain: {total_candidates}"
)

for index, row in test_df.iterrows():

    candidate_name = str(
        row.get(
            "candidate_name",
            f"Candidate {index + 1}"
        )
    )

    job_role = str(
        row.get(
            "job_role",
            "Unknown"
        )
    )

    actual_label = str(
        row.get(
            "label",
            "Unknown"
        )
    )

    # --------------------------------------------------------
    # Build candidate text
    # --------------------------------------------------------

    resume_text = str(
        row.get("resume_text", "")
    )

    job_description = str(
        row.get("job_description", "")
    )

    combined_text = (
        resume_text
        + " [JOB_DESCRIPTION] "
        + job_description
    )

    # --------------------------------------------------------
    # Generate prediction
    # --------------------------------------------------------

    predict_fn = create_predict_function(index)

    base_features = build_features_from_text(
        [combined_text],
        index,
    )

    predicted_label = str(
        svm_model.predict(base_features)[0]
    )

    decision_score = float(
        svm_model.decision_function(base_features)[0]
    )

    # --------------------------------------------------------
    # Generate LIME explanation
    # --------------------------------------------------------

    explanation = explainer.explain_instance(
        combined_text,
        predict_fn,
        labels=[0, 1],
        num_features=20,
        num_samples=300,
    )

    # Determine which LIME label corresponds to prediction
    if predicted_label == "Strong Match":
        lime_label = 1
    else:
        lime_label = 0

    explanation_list = explanation.as_list(
        label=lime_label
    )

    # --------------------------------------------------------
    # Save top 20 features
    # --------------------------------------------------------

    for feature, weight in explanation_list:

        if weight >= 0:
            if predicted_label == "Strong Match":
                direction = "Supports Strong Match"
            else:
                direction = "Supports Weak Match"
        else:
            if predicted_label == "Strong Match":
                direction = "Supports Weak Match"
            else:
                direction = "Supports Strong Match"

        all_records.append(
            {
                "candidate_name": candidate_name,
                "job_role": job_role,
                "actual_label": actual_label,
                "predicted_label": predicted_label,
                "decision_score": decision_score,
                "feature": feature,
                "lime_weight": float(weight),
                "direction": direction,
            }
        )

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    completed = index + 1

    if (
        completed % 25 == 0
        or completed == total_candidates
    ):
        print(
            f"Processed {completed}/{total_candidates} "
            f"candidates..."
        )


# ============================================================
# SAVE OUTPUT
# ============================================================

lime_df = pd.DataFrame(all_records)

lime_df.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ============================================================
# VERIFICATION
# ============================================================

print("\n" + "=" * 70)
print("CANDIDATE LIME GENERATION COMPLETE")
print("=" * 70)

print(
    f"\nCandidates explained: "
    f"{lime_df['candidate_name'].nunique()}"
)

print(
    f"Explanation records: "
    f"{len(lime_df)}"
)

print("\nSaved file:")

print(OUTPUT_PATH)


# ============================================================
# CANDIDATE 1562 VERIFICATION
# ============================================================

candidate_1562 = lime_df[
    lime_df["candidate_name"] == "Candidate 1562"
]

print("\n" + "=" * 70)
print("CANDIDATE 1562 VERIFICATION")
print("=" * 70)

if len(candidate_1562) > 0:

    first = candidate_1562.iloc[0]

    print(
        f"Candidate: "
        f"{first['candidate_name']}"
    )

    print(
        f"Job Role: "
        f"{first['job_role']}"
    )

    print(
        f"Prediction: "
        f"{first['predicted_label']}"
    )

    print("\nTop LIME features:")

    print(
        candidate_1562[
            [
                "feature",
                "lime_weight",
                "direction",
            ]
        ].to_string(index=False)
    )

else:

    print(
        "WARNING: Candidate 1562 was not found."
    )

print("\nDone.")