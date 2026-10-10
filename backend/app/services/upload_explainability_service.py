import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

from scipy.sparse import hstack, csr_matrix
from lime.lime_text import LimeTextExplainer


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
MODEL_DIR = PROJECT_ROOT / "models"
TEST_DATA_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "processed"
    / "splits_v2"
    / "test.csv"
)

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml.prediction.feature_engineering import (
    create_structured_features,
    create_combined_text,
)


# ---------------------------------------------------------
# Model artifacts
# ---------------------------------------------------------

MODEL_PATH = MODEL_DIR / "fairhire_svm_model_v2.joblib"
TFIDF_PATH = MODEL_DIR / "fairhire_svm_tfidf_v2.joblib"
SCALER_PATH = MODEL_DIR / "fairhire_svm_scaler_v2.joblib"
FEATURE_COLUMNS_PATH = (
    MODEL_DIR / "fairhire_svm_feature_columns_v2.joblib"
)


svm_model = joblib.load(MODEL_PATH)
tfidf = joblib.load(TFIDF_PATH)
scaler = joblib.load(SCALER_PATH)
feature_columns = joblib.load(FEATURE_COLUMNS_PATH)


# ---------------------------------------------------------
# Test background data
# ---------------------------------------------------------

test_df = pd.read_csv(TEST_DATA_PATH)

test_text = create_combined_text(test_df)

test_tfidf = tfidf.transform(test_text)

test_structured = create_structured_features(test_df)
test_structured = test_structured[feature_columns]

test_scaled_structured = scaler.transform(
    test_structured
)

test_features = hstack(
    [
        test_tfidf,
        csr_matrix(test_scaled_structured),
    ]
).tocsr()


# Use a manageable background for SHAP.
SHAP_BACKGROUND_SIZE = min(100, test_features.shape[0])

shap_background = test_features[
    :SHAP_BACKGROUND_SIZE
]


# ---------------------------------------------------------
# Feature names
# ---------------------------------------------------------

tfidf_feature_names = list(
    tfidf.get_feature_names_out()
)

feature_names = (
    tfidf_feature_names
    + list(feature_columns)
)


# ---------------------------------------------------------
# SHAP
# ---------------------------------------------------------

shap_explainer = shap.LinearExplainer(
    svm_model,
    shap_background,
)


def build_candidate_features(candidate_data: dict):
    """
    Build exactly the same feature representation used
    by the V2 prediction pipeline.
    """

    candidate_df = pd.DataFrame(
        [candidate_data]
    )

    combined_text = create_combined_text(
        candidate_df
    )

    candidate_tfidf = tfidf.transform(
        combined_text
    )

    candidate_structured = (
        create_structured_features(
            candidate_df
        )
    )

    candidate_structured = (
        candidate_structured[
            feature_columns
        ]
    )

    candidate_scaled = scaler.transform(
        candidate_structured
    )

    final_features = hstack(
        [
            candidate_tfidf,
            csr_matrix(candidate_scaled),
        ]
    ).tocsr()

    return final_features


def get_shap_explanation(candidate_data: dict):
    """
    Generate genuine SHAP explanation for a newly
    uploaded candidate.
    """

    candidate_features = build_candidate_features(
        candidate_data
    )

    prediction = svm_model.predict(
        candidate_features
    )[0]

    decision_score = float(
        svm_model.decision_function(
            candidate_features
        )[0]
    )

    shap_values = shap_explainer(
        candidate_features
    )

    values = np.asarray(
        shap_values.values
    )

    # LinearSVC explanation is normally:
    # samples x features
    if values.ndim == 2:
        values = values[0]

    if values.ndim > 1:
        values = np.asarray(
            values[0]
        )

    records = []

    for feature, value in zip(
        feature_names,
        values
    ):
        value = float(value)

        records.append(
            {
                "feature": feature,
                "shap_value": value,
                "direction": (
                    "Supports Strong Match"
                    if value >= 0
                    else "Supports Weak Match"
                ),
            }
        )

    records.sort(
        key=lambda item: abs(
            item["shap_value"]
        ),
        reverse=True,
    )

    return {
        "explanation_type": "SHAP",
        "prediction": str(prediction),
        "decision_score": decision_score,
        "top_features": records[:20],
    }


# ---------------------------------------------------------
# LIME
# ---------------------------------------------------------

lime_explainer = LimeTextExplainer(
    class_names=[
        "Weak Match",
        "Strong Match",
    ],
    random_state=42,
)


def get_lime_explanation(candidate_data: dict):
    """
    Generate genuine LIME text explanation for a newly
    uploaded candidate.
    """

    candidate_df = pd.DataFrame(
        [candidate_data]
    )

    combined_text = create_combined_text(
        candidate_df
    )[0]

    candidate_structured = (
        create_structured_features(
            candidate_df
        )
    )

    candidate_structured = (
        candidate_structured[
            feature_columns
        ]
    )

    candidate_scaled = scaler.transform(
        candidate_structured
    )

    def predict_texts(text_list):

        text_features = tfidf.transform(
            text_list
        )

        repeated_structured = csr_matrix(
            candidate_scaled
            .repeat(
                len(text_list),
                axis=0
            )
        )

        final_features = hstack(
            [
                text_features,
                repeated_structured,
            ]
        ).tocsr()

        decision_scores = (
            svm_model.decision_function(
                final_features
            )
        )

        # Convert decision scores to a smooth
        # explanation probability.
        probabilities = 1 / (
            1 + np.exp(
                -decision_scores
            )
        )

        return np.column_stack(
            [
                1 - probabilities,
                probabilities,
            ]
        )

    explanation = lime_explainer.explain_instance(
        combined_text,
        predict_texts,
        num_features=20,
    )

    records = []

    for feature, weight in explanation.as_list():

        records.append(
            {
                "feature": feature,
                "lime_weight": float(weight),
                "direction": (
                    "Supports Strong Match"
                    if weight >= 0
                    else "Supports Weak Match"
                ),
            }
        )

    return {
        "explanation_type": "LIME",
        "top_features": records,
    }


def get_upload_explanations(
    candidate_data: dict
):
    """
    Generate both SHAP and LIME explanations.
    """

    shap_result = get_shap_explanation(
        candidate_data
    )

    lime_result = get_lime_explanation(
        candidate_data
    )

    return {
        "shap": shap_result,
        "lime": lime_result,
    }