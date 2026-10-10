from pathlib import Path
import re

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

TRAIN_PATH = Path("../dataset/processed/splits_v2/train.csv")

RANDOM_STATE = 42


# ============================================================
# SKILL LIST
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


def normalize_text(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = text.replace("c++", "cplusplus")
    text = text.replace("node.js", "nodejs")

    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text):
    text = normalize_text(text)

    found = set()

    for skill in COMMON_SKILLS:
        normalized = normalize_text(skill)

        if normalized in text:
            found.add(skill)

    return found


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
            str(row.get("skills", "")) +
            " " +
            str(row.get("resume_text", ""))
        )

        required_skills = extract_skills(
            job_description
        )

        if required_skills:

            matched = (
                resume_skills
                .intersection(required_skills)
            )

            skill_overlap = (
                len(matched)
                / len(required_skills)
            )

        else:

            matched = set()
            skill_overlap = 0.0

        matched_skill_count = len(matched)
        required_skill_count = len(required_skills)

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

        resume_words = set(resume_text.split())

        if job_words:
            semantic_overlap = (
                len(resume_words.intersection(job_words))
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

    return pd.DataFrame(rows)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - HYBRID FEATURE IMPORTANCE ANALYSIS")
print("=" * 70)

print("\n[1/5] Loading training data...")

df = pd.read_csv(TRAIN_PATH)

print(f"Training rows: {len(df)}")


# ============================================================
# STRUCTURED FEATURES
# ============================================================

print("\n[2/5] Creating structured features...")

features = calculate_features(df)

print(f"Structured features: {features.shape[1]}")


# ============================================================
# SCALE FEATURES
# ============================================================

print("\n[3/5] Scaling structured features...")

scaler = StandardScaler()

X_structured = scaler.fit_transform(features)

y = df["label"]


# ============================================================
# TRAIN STRUCTURED-ONLY MODEL
# ============================================================

print("\n[4/5] Training structured-feature model...")

model = LogisticRegression(
    max_iter=3000,
    random_state=RANDOM_STATE,
)

model.fit(
    X_structured,
    y,
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("\n[5/5] Calculating feature importance...")

importance = pd.DataFrame({
    "feature": features.columns,
    "coefficient": model.coef_[0],
})

importance["absolute_importance"] = (
    importance["coefficient"].abs()
)

importance = importance.sort_values(
    "absolute_importance",
    ascending=False,
)


print("\n" + "=" * 70)
print("STRUCTURED FEATURE IMPORTANCE")
print("=" * 70)

for _, row in importance.iterrows():

    direction = (
        "Strong Match"
        if row["coefficient"] > 0
        else "Weak Match"
    )

    print(
        f"{row['feature']:30s} "
        f"{row['coefficient']:10.4f}   "
        f"→ {direction}"
    )


print("\n" + "=" * 70)
print("TOP FEATURES")
print("=" * 70)

print(
    importance[
        [
            "feature",
            "coefficient",
            "absolute_importance",
        ]
    ].to_string(index=False)
)


print("\n" + "=" * 70)
print("FEATURE ANALYSIS COMPLETE")
print("=" * 70)