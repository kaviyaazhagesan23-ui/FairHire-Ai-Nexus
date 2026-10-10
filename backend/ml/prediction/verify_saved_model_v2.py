from pathlib import Path
import re

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

MODEL_DIR = Path("../models")

TEST_PATH = Path(
    "../dataset/processed/splits_v2/test.csv"
)


MODEL_PATH = (
    MODEL_DIR
    / "fairhire_hybrid_model_v2.joblib"
)

VECTORIZER_PATH = (
    MODEL_DIR
    / "fairhire_tfidf_v2.joblib"
)

SCALER_PATH = (
    MODEL_DIR
    / "fairhire_scaler_v2.joblib"
)

FEATURE_COLUMNS_PATH = (
    MODEL_DIR
    / "fairhire_feature_columns_v2.joblib"
)


# ============================================================
# SKILLS
# ============================================================

COMMON_SKILLS = {
    "python", "java", "javascript", "typescript",
    "c++", "c", "sql", "html", "css",
    "react", "angular", "vue", "node.js", "node",
    "express", "fastapi", "flask", "django",
    "spring", "spring boot",
    "mongodb", "mysql", "postgresql", "postgres",
    "oracle", "redis",
    "docker", "kubernetes",
    "aws", "azure", "gcp", "google cloud",
    "git", "github", "linux",
    "tensorflow", "pytorch", "scikit-learn", "sklearn",
    "pandas", "numpy", "matplotlib", "seaborn",
    "xgboost", "machine learning", "deep learning",
    "nlp", "computer vision",
    "data analysis", "data analytics", "data science",
    "statistics", "power bi", "tableau", "excel",
    "spark", "hadoop", "airflow", "etl",
    "data pipelines", "rest api", "api",
    "testing", "selenium", "ci/cd",
    "llm", "generative ai", "blockchain", "solidity",
}


# ============================================================
# HELPERS
# ============================================================

def normalize_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = text.replace("c++", "cplusplus")
    text = text.replace("node.js", "nodejs")

    text = re.sub(
        r"[^a-z0-9+#./\-\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_skills(text):

    text = normalize_text(text)

    found = set()

    for skill in COMMON_SKILLS:

        normalized_skill = normalize_text(skill)

        if normalized_skill in text:
            found.add(skill)

    return found


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def calculate_features(df, feature_columns):

    rows = []

    for _, row in df.iterrows():

        resume_text = normalize_text(
            row.get("resume_text", "")
        )

        job_description = normalize_text(
            row.get("job_description", "")
        )

        resume_skills = extract_skills(
            str(row.get("skills", ""))
            + " "
            + str(row.get("resume_text", ""))
        )

        required_skills = extract_skills(
            job_description
        )

        if required_skills:

            matched_skills = (
                resume_skills
                .intersection(required_skills)
            )

            skill_overlap = (
                len(matched_skills)
                / len(required_skills)
            )

        else:

            matched_skills = set()
            skill_overlap = 0.0

        matched_skill_count = len(
            matched_skills
        )

        required_skill_count = len(
            required_skills
        )

        # ----------------------------------------------------
        # EXPERIENCE
        # ----------------------------------------------------

        candidate_experience = float(
            row.get("experience_years", 0)
        )

        required_experience = float(
            row.get("required_experience", 0)
        )

        experience_gap = (
            candidate_experience
            - required_experience
        )

        experience_compatible = (
            1.0
            if candidate_experience >= required_experience
            else 0.0
        )

        # ----------------------------------------------------
        # ROLE
        # ----------------------------------------------------

        candidate_role = normalize_text(
            row.get("previous_role", "")
        )

        target_role = normalize_text(
            row.get("job_role", "")
        )

        role_compatibility = 0.0

        if candidate_role and target_role:

            if set(candidate_role.split()).intersection(
                set(target_role.split())
            ):

                role_compatibility = 1.0

        # ----------------------------------------------------
        # PROJECT
        # ----------------------------------------------------

        project_text = normalize_text(
            row.get("projects", "")
        )

        project_words = set(
            project_text.split()
        )

        job_words = set(
            job_description.split()
        )

        if job_words:

            project_relevance = (
                len(
                    project_words.intersection(
                        job_words
                    )
                )
                / len(job_words)
            )

        else:

            project_relevance = 0.0

        # ----------------------------------------------------
        # SEMANTIC OVERLAP
        # ----------------------------------------------------

        resume_words = set(
            resume_text.split()
        )

        if job_words:

            semantic_overlap = (
                len(
                    resume_words.intersection(
                        job_words
                    )
                )
                / len(job_words)
            )

        else:

            semantic_overlap = 0.0

        rows.append({
            "skill_overlap": skill_overlap,
            "matched_skill_count": matched_skill_count,
            "required_skill_count": required_skill_count,
            "experience_years": candidate_experience,
            "required_experience": required_experience,
            "experience_gap": experience_gap,
            "experience_compatible": experience_compatible,
            "role_compatibility": role_compatibility,
            "project_relevance": project_relevance,
            "semantic_overlap": semantic_overlap,
        })

    return pd.DataFrame(
        rows,
        columns=feature_columns
    )


# ============================================================
# START
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - SAVED MODEL VERIFICATION")
print("=" * 70)


# ============================================================
# LOAD ARTIFACTS
# ============================================================

print("\n[1/5] Loading saved artifacts...")

model = joblib.load(
    MODEL_PATH
)

vectorizer = joblib.load(
    VECTORIZER_PATH
)

scaler = joblib.load(
    SCALER_PATH
)

feature_columns = joblib.load(
    FEATURE_COLUMNS_PATH
)

print("Model loaded.")
print("TF-IDF vectorizer loaded.")
print("Scaler loaded.")
print("Feature columns loaded.")


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\n[2/5] Loading test dataset...")

test_df = pd.read_csv(
    TEST_PATH
)

print(
    f"Test rows available: {len(test_df)}"
)


# ============================================================
# TEXT FEATURES
# ============================================================

print("\n[3/5] Creating TF-IDF features...")

test_text = (
    test_df["resume_text"].fillna("")
    + " [JOB_DESCRIPTION] "
    + test_df["job_description"].fillna("")
)

X_tfidf = vectorizer.transform(
    test_text
)

print(
    f"TF-IDF shape: {X_tfidf.shape}"
)


# ============================================================
# STRUCTURED FEATURES
# ============================================================

print("\n[4/5] Creating structured features...")

structured = calculate_features(
    test_df,
    feature_columns
)

X_structured = scaler.transform(
    structured
)

print(
    f"Structured shape: {X_structured.shape}"
)


# ============================================================
# COMBINE + PREDICT
# ============================================================

print("\n[5/5] Generating predictions...")

X_combined = np.hstack([
    X_tfidf.toarray(),
    X_structured,
])

predictions = model.predict(
    X_combined
)

probabilities = model.predict_proba(
    X_combined
)

print(
    f"Predictions generated: {len(predictions)}"
)

print(
    f"Probability matrix shape: "
    f"{probabilities.shape}"
)


# ============================================================
# SAMPLE PREDICTIONS
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE PREDICTIONS")
print("=" * 70)

for i in range(min(10, len(test_df))):

    predicted_label = predictions[i]

    confidence = (
        probabilities[i].max() * 100
    )

    print(
        f"{i + 1:02d}. "
        f"Actual: {test_df.iloc[i]['label']:12s} | "
        f"Predicted: {predicted_label:12s} | "
        f"Confidence: {confidence:.2f}%"
    )


print("\n" + "=" * 70)
print("SAVED MODEL VERIFICATION COMPLETE")
print("=" * 70)