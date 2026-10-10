from pathlib import Path
import re

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer


# ============================================================
# PATHS
# ============================================================

TRAIN_PATH = Path("../dataset/processed/splits_v2/train.csv")
VAL_PATH = Path("../dataset/processed/splits_v2/validation.csv")


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42


# ============================================================
# SKILL EXTRACTION
# ============================================================

COMMON_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c",
    "sql",
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "node",
    "express",
    "fastapi",
    "flask",
    "django",
    "spring",
    "spring boot",
    "mongodb",
    "mysql",
    "postgresql",
    "postgres",
    "oracle",
    "redis",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "git",
    "github",
    "linux",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "sklearn",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "xgboost",
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
    "data analysis",
    "data analytics",
    "data science",
    "statistics",
    "power bi",
    "tableau",
    "excel",
    "spark",
    "hadoop",
    "airflow",
    "etl",
    "data pipelines",
    "rest api",
    "api",
    "testing",
    "selenium",
    "ci/cd",
    "llm",
    "generative ai",
    "blockchain",
    "solidity",
}


def normalize_text(text):
    """Normalize text for matching."""
    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = text.replace("c++", "cplusplus")
    text = text.replace("node.js", "nodejs")
    text = text.replace("scikit-learn", "sklearn")

    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text):
    """Extract known skills appearing in text."""
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
    """
    Create structured matching features.

    These features are calculated independently for each row.
    """

    feature_rows = []

    for _, row in df.iterrows():

        resume_text = normalize_text(
            row.get("resume_text", "")
        )

        job_description = normalize_text(
            row.get("job_description", "")
        )

        resume_skills = extract_skills(
            row.get("skills", "")
            + " "
            + row.get("resume_text", "")
        )

        required_skills = extract_skills(
            row.get("job_description", "")
        )

        # ----------------------------------------------------
        # Skill overlap
        # ----------------------------------------------------

        if len(required_skills) > 0:
            matched_skills = (
                resume_skills.intersection(required_skills)
            )

            skill_overlap = (
                len(matched_skills)
                / len(required_skills)
            )
        else:
            matched_skills = set()
            skill_overlap = 0.0

        matched_skill_count = len(matched_skills)
        required_skill_count = len(required_skills)

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        try:
            candidate_experience = float(
                row.get("experience_years", 0)
            )
        except (ValueError, TypeError):
            candidate_experience = 0.0

        try:
            required_experience = float(
                row.get("required_experience", 0)
            )
        except (ValueError, TypeError):
            required_experience = 0.0

        experience_gap = (
            candidate_experience - required_experience
        )

        experience_compatible = (
            1.0 if candidate_experience >= required_experience
            else 0.0
        )

        # ----------------------------------------------------
        # Role compatibility
        # ----------------------------------------------------

        candidate_role = normalize_text(
            row.get("previous_role", "")
        )

        target_role = normalize_text(
            row.get("job_role", "")
        )

        role_compatibility = 0.0

        if target_role and candidate_role:

            target_words = set(target_role.split())
            candidate_words = set(candidate_role.split())

            if target_words.intersection(candidate_words):
                role_compatibility = 1.0

        # ----------------------------------------------------
        # Project relevance
        # ----------------------------------------------------

        project_text = normalize_text(
            row.get("projects", "")
        )

        project_words = set(project_text.split())
        job_words = set(job_description.split())

        if job_words:
            project_relevance = (
                len(project_words.intersection(job_words))
                / len(job_words)
            )
        else:
            project_relevance = 0.0

        # ----------------------------------------------------
        # Resume / Job TF-IDF similarity
        # ----------------------------------------------------

        resume_words = set(resume_text.split())
        job_words = set(job_description.split())

        if resume_words and job_words:
            semantic_overlap = (
                len(resume_words.intersection(job_words))
                / len(job_words)
            )
        else:
            semantic_overlap = 0.0

        feature_rows.append(
            {
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
            }
        )

    return pd.DataFrame(feature_rows)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - V2 HYBRID MATCHING MODEL")
print("=" * 70)

print("\n[1/8] Loading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
val_df = pd.read_csv(VAL_PATH)

print(f"Training rows:   {len(train_df)}")
print(f"Validation rows: {len(val_df)}")


# ============================================================
# TARGET
# ============================================================

y_train = train_df["label"]
y_val = val_df["label"]


# ============================================================
# STRUCTURED FEATURES
# ============================================================

print("\n[2/8] Creating structured matching features...")

train_features = calculate_features(train_df)
val_features = calculate_features(val_df)

print(f"Feature count: {train_features.shape[1]}")
print("\nFeature names:")
print(list(train_features.columns))


# ============================================================
# DISPLAY FEATURE SIGNAL
# ============================================================

print("\n[3/8] Checking feature averages...")

feature_check = train_features.copy()
feature_check["label"] = y_train.values

print(
    feature_check
    .groupby("label")
    .mean(numeric_only=True)
    .round(4)
)


# ============================================================
# TF-IDF TEXT FEATURES
# ============================================================

print("\n[4/8] Creating TF-IDF features...")

def build_text(df):
    return (
        df["resume_text"].fillna("")
        + " [JOB_DESCRIPTION] "
        + df["job_description"].fillna("")
    )


X_train_text = build_text(train_df)
X_val_text = build_text(val_df)

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True,
)

X_train_tfidf = vectorizer.fit_transform(X_train_text)
X_val_tfidf = vectorizer.transform(X_val_text)

print(
    f"TF-IDF training matrix:   {X_train_tfidf.shape}"
)

print(
    f"TF-IDF validation matrix: {X_val_tfidf.shape}"
)


# ============================================================
# SCALE STRUCTURED FEATURES
# ============================================================

print("\n[5/8] Scaling structured features...")

scaler = StandardScaler()

X_train_structured = scaler.fit_transform(
    train_features
)

X_val_structured = scaler.transform(
    val_features
)


# ============================================================
# COMBINE FEATURES
# ============================================================

print("\n[6/8] Combining NLP + structured features...")

X_train = np.hstack(
    [
        X_train_tfidf.toarray(),
        X_train_structured,
    ]
)

X_val = np.hstack(
    [
        X_val_tfidf.toarray(),
        X_val_structured,
    ]
)

print(f"Combined training shape:   {X_train.shape}")
print(f"Combined validation shape: {X_val.shape}")


# ============================================================
# TRAIN MODEL
# ============================================================

print("\n[7/8] Training hybrid Logistic Regression...")

model = LogisticRegression(
    max_iter=3000,
    random_state=RANDOM_STATE,
)

model.fit(
    X_train,
    y_train,
)

print("Hybrid model training complete.")


# ============================================================
# EVALUATION
# ============================================================

print("\n[8/8] Evaluating validation performance...")

y_pred = model.predict(X_val)

accuracy = accuracy_score(
    y_val,
    y_pred,
)

precision = precision_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)

recall = recall_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)

f1 = f1_score(
    y_val,
    y_pred,
    pos_label="Strong Match",
)

print("\n" + "=" * 70)
print("HYBRID VALIDATION RESULTS")
print("=" * 70)

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")

print("\nClassification Report:")
print(
    classification_report(
        y_val,
        y_pred,
    )
)

print("Confusion Matrix:")

print(
    confusion_matrix(
        y_val,
        y_pred,
        labels=[
            "Weak Match",
            "Strong Match",
        ],
    )
)


print("\n" + "=" * 70)
print("V2 HYBRID MODEL COMPLETE")
print("=" * 70)