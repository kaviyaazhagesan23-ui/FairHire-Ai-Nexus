import sys
from pathlib import Path

import joblib
import pandas as pd
from scipy.sparse import hstack, csr_matrix

# ------------------------------------------------------------
# PATH SETUP
# ------------------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
MODEL_DIR = PROJECT_ROOT / "models"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml.prediction.feature_engineering import (
    create_structured_features,
    create_combined_text,
)


# ------------------------------------------------------------
# MODEL PATHS
# ------------------------------------------------------------

MODEL_PATH = MODEL_DIR / "fairhire_svm_model_v2.joblib"
TFIDF_PATH = MODEL_DIR / "fairhire_svm_tfidf_v2.joblib"
SCALER_PATH = MODEL_DIR / "fairhire_svm_scaler_v2.joblib"
FEATURE_COLUMNS_PATH = (
    MODEL_DIR / "fairhire_svm_feature_columns_v2.joblib"
)


# ------------------------------------------------------------
# LOAD MODEL ARTIFACTS
# ------------------------------------------------------------

print("Loading FairHire AI V2 model artifacts...")

svm_model = joblib.load(MODEL_PATH)
tfidf = joblib.load(TFIDF_PATH)
scaler = joblib.load(SCALER_PATH)
feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

print("SVM model loaded.")
print("TF-IDF loaded.")
print("Scaler loaded.")
print("Feature columns loaded.")


# ------------------------------------------------------------
# PREDICTION FUNCTION
# ------------------------------------------------------------

def predict_candidate(candidate_data: dict):
    """
    Run the exact FairHire V2 SVM prediction pipeline.

    Pipeline:
        Combined Text
            ↓
        TF-IDF
            +
        Structured Features
            ↓
        StandardScaler
            ↓
        Feature Combination
            ↓
        Linear SVM
    """

    # Convert request into one-row DataFrame
    candidate_df = pd.DataFrame([candidate_data])

    # --------------------------------------------------------
    # TF-IDF FEATURES
    # --------------------------------------------------------

    combined_text = create_combined_text(candidate_df)

    tfidf_features = tfidf.transform(combined_text)

    # --------------------------------------------------------
    # STRUCTURED FEATURES
    # --------------------------------------------------------

    structured_features = create_structured_features(
        candidate_df
    )

    structured_features = structured_features[
        feature_columns
    ]

    scaled_structured_features = scaler.transform(
        structured_features
    )

    # --------------------------------------------------------
    # COMBINE FEATURES
    # --------------------------------------------------------

    final_features = hstack(
        [
            tfidf_features,
            csr_matrix(scaled_structured_features),
        ]
    ).tocsr()

    # --------------------------------------------------------
    # SVM PREDICTION
    # --------------------------------------------------------

    prediction = svm_model.predict(final_features)[0]

    decision_score = float(
        svm_model.decision_function(final_features)[0]
    )

    return {
        "prediction": str(prediction),
        "decision_score": decision_score,
    }