from pathlib import Path
import re

import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

TRAIN_PATH = Path("../dataset/processed/splits_v2/train.csv")
MODEL_DIR = Path("../models")

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIG
# ============================================================

RANDOM_STATE = 42


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


FEATURE_COLUMNS = [
    "skill_overlap",
    "matched_skill_count",
    "required_skill_count",
    "experience_years",
    "required_experience",
    "experience_gap",
    "experience_compatible",
    "role_compatibility",
    "project_relevance",
    "semantic_overlap",
]


# ============================================================
# TEXT HELPERS
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

def calculate_features(df):

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
        # PROJECT RELEVANCE
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
        columns=FEATURE_COLUMNS
    )


# ============================================================
# LOAD TRAINING DATA
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - SAVE V2 HYBRID MODEL")
print("=" * 70)

print("\n[1/6] Loading training data...")

train_df = pd.read_csv(
    TRAIN_PATH
)

print(
    f"Training rows: {len(train_df)}"
)


# ============================================================
# STRUCTURED FEATURES
# ============================================================

print("\n[2/6] Creating structured features...")

structured_features = calculate_features(
    train_df
)

print(
    f"Structured feature shape: "
    f"{structured_features.shape}"
)


# ============================================================
# SCALE
# ============================================================

print("\n[3/6] Fitting scaler...")

scaler = StandardScaler()

X_structured = scaler.fit_transform(
    structured_features
)


# ============================================================
# TF-IDF
# ============================================================

print("\n[4/6] Fitting TF-IDF vectorizer...")

text = (
    train_df["resume_text"].fillna("")
    + " [JOB_DESCRIPTION] "
    + train_df["job_description"].fillna("")
)

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True,
)

X_tfidf = vectorizer.fit_transform(
    text
)

print(
    f"TF-IDF feature count: "
    f"{X_tfidf.shape[1]}"
)


# ============================================================
# COMBINE
# ============================================================

print("\n[5/6] Training final hybrid model...")

X_combined = np.hstack([
    X_tfidf.toarray(),
    X_structured,
])

model = LogisticRegression(
    max_iter=3000,
    random_state=RANDOM_STATE,
)

model.fit(
    X_combined,
    train_df["label"]
)

print("Final model trained.")


# ============================================================
# SAVE ARTIFACTS
# ============================================================

print("\n[6/6] Saving model artifacts...")

model_path = (
    MODEL_DIR
    / "fairhire_hybrid_model_v2.joblib"
)

vectorizer_path = (
    MODEL_DIR
    / "fairhire_tfidf_v2.joblib"
)

scaler_path = (
    MODEL_DIR
    / "fairhire_scaler_v2.joblib"
)

features_path = (
    MODEL_DIR
    / "fairhire_feature_columns_v2.joblib"
)


joblib.dump(
    model,
    model_path
)

joblib.dump(
    vectorizer,
    vectorizer_path
)

joblib.dump(
    scaler,
    scaler_path
)

joblib.dump(
    FEATURE_COLUMNS,
    features_path
)


print("\nSaved artifacts:")

print(
    f"Model:       {model_path}"
)

print(
    f"TF-IDF:      {vectorizer_path}"
)

print(
    f"Scaler:      {scaler_path}"
)

print(
    f"Features:    {features_path}"
)


print("\n" + "=" * 70)
print("V2 HYBRID MODEL ARTIFACTS SAVED")
print("=" * 70)