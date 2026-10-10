from pathlib import Path
import joblib
import pandas as pd
import numpy as np

from scipy.sparse import hstack, csr_matrix
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
TEST_PATH = (
    BASE_DIR.parent
    / "dataset"
    / "processed"
    / "splits_v2"
    / "test.csv"
)
MODEL_PATH = BASE_DIR.parent / "models" / "fairhire_hybrid_model_v2.joblib"
TFIDF_PATH = BASE_DIR.parent / "models" / "fairhire_tfidf_v2.joblib"
SCALER_PATH = BASE_DIR.parent / "models" / "fairhire_scaler_v2.joblib"
FEATURE_COLUMNS_PATH = (
    BASE_DIR.parent / "models" / "fairhire_feature_columns_v2.joblib"
)
# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - FINAL V2 MODEL EVALUATION")
print("=" * 70)

print("\nLoading saved model artifacts...")

model = joblib.load(MODEL_PATH)
tfidf = joblib.load(TFIDF_PATH)
scaler = joblib.load(SCALER_PATH)
feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

print("Model loaded successfully.")
print("TF-IDF vectorizer loaded.")
print("Scaler loaded.")
print("Feature columns loaded.")


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\nLoading test dataset...")

df = pd.read_csv(TEST_PATH)

print(f"Test rows: {len(df)}")

if "label" not in df.columns:
    raise ValueError("ERROR: 'label' column not found in test dataset.")

print("\nTest label distribution:")
print(df["label"].value_counts())


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value)


def calculate_structured_features(row):
    """
    Recreates the same structured matching features
    used during V2 hybrid model training.
    """

    resume_skills = {
        skill.strip().lower()
        for skill in safe_text(row.get("skills", "")).split(",")
        if skill.strip()
    }

    job_skills = {
        skill.strip().lower()
        for skill in safe_text(
            row.get("required_skills", row.get("skills", ""))
        ).split(",")
        if skill.strip()
    }

    # --------------------------------------------------------
    # Skill overlap
    # --------------------------------------------------------

    if len(job_skills) > 0:
        matched_skills = resume_skills.intersection(job_skills)

        skill_overlap = len(matched_skills) / len(job_skills)
        matched_skill_count = len(matched_skills)
        required_skill_count = len(job_skills)
    else:
        skill_overlap = 0.0
        matched_skill_count = 0
        required_skill_count = 0

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience_years = float(row.get("experience_years", 0) or 0)

    required_experience = float(
        row.get("required_experience", 0) or 0
    )

    experience_gap = experience_years - required_experience

    experience_compatible = (
        1.0 if experience_years >= required_experience else 0.0
    )

    # --------------------------------------------------------
    # Role compatibility
    # --------------------------------------------------------

    job_role = safe_text(row.get("job_role", "")).lower()
    previous_role = safe_text(row.get("previous_role", "")).lower()

    role_compatibility = 1.0 if (
        job_role in previous_role
        or previous_role in job_role
    ) else 0.0

    # --------------------------------------------------------
    # Project relevance
    # --------------------------------------------------------

    projects = safe_text(row.get("projects", "")).lower()

    project_relevance = 0.0

    if projects and job_role:
        role_words = {
            word.strip()
            for word in job_role.replace("-", " ").split()
            if len(word.strip()) > 2
        }

        if role_words:
            matched_project_words = sum(
                1 for word in role_words
                if word in projects
            )

            project_relevance = (
                matched_project_words / len(role_words)
            )

    # --------------------------------------------------------
    # Semantic overlap
    # --------------------------------------------------------

    resume_text = safe_text(row.get("resume_text", "")).lower()
    job_description = safe_text(
        row.get("job_description", "")
    ).lower()

    resume_words = {
        word.strip()
        for word in resume_text.split()
        if len(word.strip()) > 2
    }

    job_words = {
        word.strip()
        for word in job_description.split()
        if len(word.strip()) > 2
    }

    if job_words:
        semantic_overlap = len(
            resume_words.intersection(job_words)
        ) / len(job_words)
    else:
        semantic_overlap = 0.0

    return [
        skill_overlap,
        matched_skill_count,
        required_skill_count,
        experience_years,
        required_experience,
        experience_gap,
        experience_compatible,
        role_compatibility,
        project_relevance,
        semantic_overlap,
    ]


# ============================================================
# CREATE STRUCTURED FEATURES
# ============================================================

print("\nCreating structured features...")

structured_features = np.array(
    [
        calculate_structured_features(row)
        for _, row in df.iterrows()
    ],
    dtype=float,
)

structured_df = pd.DataFrame(
    structured_features,
    columns=feature_columns,
)

print(
    f"Structured feature shape: {structured_df.shape}"
)


# ============================================================
# SCALE STRUCTURED FEATURES
# ============================================================

structured_scaled = scaler.transform(structured_df)


# ============================================================
# CREATE TF-IDF FEATURES
# ============================================================

print("\nCreating TF-IDF features...")

combined_text = (
    df["resume_text"].fillna("").astype(str)
    + " [JOB_DESCRIPTION] "
    + df["job_description"].fillna("").astype(str)
)

tfidf_features = tfidf.transform(combined_text)

print(
    f"TF-IDF feature shape: {tfidf_features.shape}"
)


# ============================================================
# COMBINE FEATURES
# ============================================================

print("\nCombining TF-IDF + structured features...")

structured_sparse = csr_matrix(structured_scaled)

combined_features = hstack(
    [
        tfidf_features,
        structured_sparse,
    ]
)

print(
    f"Final feature shape: {combined_features.shape}"
)


# ============================================================
# PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

y_true = df["label"]

y_pred = model.predict(combined_features)

y_probability = model.predict_proba(combined_features)

print(
    f"Predictions generated: {len(y_pred)}"
)


# ============================================================
# FINAL METRICS
# ============================================================

accuracy = accuracy_score(y_true, y_pred)

precision = precision_score(
    y_true,
    y_pred,
    pos_label="Strong Match",
)

recall = recall_score(
    y_true,
    y_pred,
    pos_label="Strong Match",
)

f1 = f1_score(
    y_true,
    y_pred,
    pos_label="Strong Match",
)


# ============================================================
# ROC-AUC
# ============================================================

classes = list(model.classes_)

if "Strong Match" in classes:
    strong_index = classes.index("Strong Match")

    y_probability_strong = y_probability[:, strong_index]

    y_true_binary = (
        y_true == "Strong Match"
    ).astype(int)

    roc_auc = roc_auc_score(
        y_true_binary,
        y_probability_strong,
    )
else:
    roc_auc = None


# ============================================================
# DISPLAY FINAL RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("FINAL V2 HYBRID MODEL RESULTS")
print("=" * 70)

print(f"\nTest Samples : {len(y_true)}")

print(f"\nAccuracy     : {accuracy:.4f}")
print(f"Accuracy     : {accuracy * 100:.2f}%")

print(f"\nPrecision    : {precision:.4f}")
print(f"Recall       : {recall:.4f}")
print(f"F1 Score     : {f1:.4f}")

if roc_auc is not None:
    print(f"ROC-AUC      : {roc_auc:.4f}")

print("\n" + "-" * 70)
print("CONFUSION MATRIX")
print("-" * 70)

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=["Weak Match", "Strong Match"],
)

print("\n                    Predicted")
print("                 Weak    Strong")
print(f"Actual Weak      {cm[0][0]:4d}    {cm[0][1]:4d}")
print(f"Actual Strong    {cm[1][0]:4d}    {cm[1][1]:4d}")


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n" + "-" * 70)
print("CLASSIFICATION REPORT")
print("-" * 70)

print(
    classification_report(
        y_true,
        y_pred,
        labels=["Weak Match", "Strong Match"],
        digits=4,
    )
)


# ============================================================
# SAMPLE PREDICTIONS
# ============================================================

print("-" * 70)
print("SAMPLE TEST PREDICTIONS")
print("-" * 70)

sample_count = min(10, len(df))

for i in range(sample_count):

    predicted_label = y_pred[i]

    if "Strong Match" in model.classes_:
        strong_index = list(model.classes_).index(
            "Strong Match"
        )

        strong_probability = (
            y_probability[i][strong_index] * 100
        )
    else:
        strong_probability = 0.0

    print(
        f"{i + 1:02d}. "
        f"Actual: {y_true.iloc[i]:12s} | "
        f"Predicted: {predicted_label:12s} | "
        f"Strong Probability: {strong_probability:6.2f}%"
    )


# ============================================================
# COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("FINAL MODEL EVALUATION COMPLETE")
print("=" * 70)