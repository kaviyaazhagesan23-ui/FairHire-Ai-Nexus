import sys
import json
from pathlib import Path

import joblib
import pandas as pd
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
)

from ml.prediction.candidate_intelligence_v2 import (
    build_candidate_intelligence,
)

# ============================================================
# PATHS
# ============================================================

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "fairhire_svm_model_v2.joblib"
)

TFIDF_PATH = (
    PROJECT_ROOT
    / "models"
    / "fairhire_svm_tfidf_v2.joblib"
)

SCALER_PATH = (
    PROJECT_ROOT
    / "models"
    / "fairhire_svm_scaler_v2.joblib"
)

TEST_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "processed"
    / "splits_v2"
    / "test.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "docs"
    / "candidate_intelligence"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

JSON_OUTPUT = (
    OUTPUT_DIR
    / "candidate_intelligence_v2.json"
)

CSV_OUTPUT = (
    OUTPUT_DIR
    / "candidate_intelligence_v2.csv"
)

# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 CANDIDATE INTELLIGENCE")
print("=" * 70)

# ============================================================
# LOAD ARTIFACTS
# ============================================================

print("\nLoading saved SVM artifacts...")

model = joblib.load(
    MODEL_PATH
)

tfidf = joblib.load(
    TFIDF_PATH
)

scaler = joblib.load(
    SCALER_PATH
)

print("Model loaded successfully.")
print("TF-IDF loaded successfully.")
print("Scaler loaded successfully.")

# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading test dataset...")

test_df = pd.read_csv(
    TEST_PATH
)

print(
    f"Test candidates: {len(test_df)}"
)

# ============================================================
# CREATE MODEL FEATURES
# ============================================================

print("\nCreating model features...")

combined_text = create_combined_text(
    test_df
)

X_tfidf = tfidf.transform(
    combined_text
)

X_structured = (
    create_structured_features(
        test_df
    )
)

X_structured_scaled = scaler.transform(
    X_structured
)

X_combined = hstack(
    [
        X_tfidf,
        X_structured_scaled
    ]
).tocsr()

print(
    f"Final feature shape: {X_combined.shape}"
)

# ============================================================
# PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

predictions = model.predict(
    X_combined
)

print(
    f"Predictions generated: {len(predictions)}"
)

# ============================================================
# BUILD INTELLIGENCE
# ============================================================

print(
    "\nBuilding candidate intelligence..."
)

candidate_results = []

for index, row in test_df.iterrows():

    result = build_candidate_intelligence(
        row,
        predictions[index]
    )

    candidate_results.append(
        result
    )

    if index < 10:

        print(
            f"\n{index + 1:02d}. "
            f"{result['candidate_name']} | "
            f"{result['job_role']} | "
            f"{result['prediction']}"
        )

        print(
            f"    Matched skills: "
            f"{result['matched_skills']}"
        )

        print(
            f"    Missing skills: "
            f"{result['missing_skills']}"
        )

        print(
            f"    Summary: "
            f"{result['summary']}"
        )

# ============================================================
# SAVE JSON
# ============================================================

with open(
    JSON_OUTPUT,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        candidate_results,
        file,
        indent=2,
        ensure_ascii=False
    )

# ============================================================
# CREATE FLAT CSV
# ============================================================

csv_rows = []

for result in candidate_results:

    experience = result[
        "experience"
    ]

    role_analysis = result[
        "role_analysis"
    ]

    project_analysis = result[
        "project_analysis"
    ]

    csv_rows.append(
        {
            "candidate_name":
                result["candidate_name"],

            "job_role":
                result["job_role"],

            "prediction":
                result["prediction"],

            "matched_skills":
                ", ".join(
                    result["matched_skills"]
                ),

            "missing_skills":
                ", ".join(
                    result["missing_skills"]
                ),

            "matched_skill_count":
                result["matched_skill_count"],

            "required_skill_count":
                result["required_skill_count"],

            "candidate_experience_years":
                experience[
                    "candidate_experience_years"
                ],

            "required_experience_years":
                experience[
                    "required_experience_years"
                ],

            "experience_gap_years":
                experience[
                    "experience_gap_years"
                ],

            "experience_status":
                experience[
                    "experience_status"
                ],

            "role_compatible":
                role_analysis[
                    "role_compatible"
                ],

            "project_relevance":
                project_analysis[
                    "project_relevance"
                ],

            "summary":
                result["summary"],
        }
    )

candidate_df = pd.DataFrame(
    csv_rows
)

candidate_df.to_csv(
    CSV_OUTPUT,
    index=False
)

# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("CANDIDATE INTELLIGENCE COMPLETE")
print("=" * 70)

print("\nSaved files:")

print(JSON_OUTPUT)
print(CSV_OUTPUT)

print("\nCandidates analyzed:")
print(len(candidate_results))