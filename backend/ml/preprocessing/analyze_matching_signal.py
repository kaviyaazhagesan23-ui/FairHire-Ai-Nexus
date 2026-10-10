import pandas as pd
import re
from pathlib import Path
from collections import Counter


# ============================================================
# FAIRHIRE AI - RESUME/JOB MATCHING SIGNAL ANALYSIS
# ============================================================

print("=" * 70)
print("FAIRHIRE AI - RESUME/JOB MATCHING SIGNAL ANALYSIS")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

DATA_PATH = Path("../dataset/raw/fairhire_synthetic_dataset_v2_3000.csv")
print("\n[1/8] Loading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ------------------------------------------------------------
# 2. BASIC TEXT NORMALIZATION
# ------------------------------------------------------------

print("\n[2/8] Preparing text...")

def normalize_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9+#.\- ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


df["resume_normalized"] = (
    df["resume_text"]
    .fillna("")
    .apply(normalize_text)
)

df["job_normalized"] = (
    df["job_description"]
    .fillna("")
    .apply(normalize_text)
)


# ------------------------------------------------------------
# 3. CALCULATE WORD OVERLAP
# ------------------------------------------------------------

print("\n[3/8] Calculating resume/job keyword overlap...")


def get_words(text):
    return set(
        word
        for word in text.split()
        if len(word) >= 3
    )


def calculate_overlap(resume, job):

    resume_words = get_words(resume)
    job_words = get_words(job)

    if not job_words:
        return 0.0

    common_words = resume_words.intersection(job_words)

    return len(common_words) / len(job_words)


df["keyword_overlap"] = df.apply(
    lambda row: calculate_overlap(
        row["resume_normalized"],
        row["job_normalized"]
    ),
    axis=1
)


print(
    "\nKeyword overlap statistics:"
)

print(
    df.groupby("label")["keyword_overlap"]
    .agg(["mean", "median", "min", "max"])
    .round(4)
)


# ------------------------------------------------------------
# 4. SKILL OVERLAP
# ------------------------------------------------------------

print("\n[4/8] Calculating technical skill overlap...")


KNOWN_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "sql",
    "nosql",
    "mongodb",
    "mysql",
    "postgresql",
    "oracle",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "keras",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "natural language processing",
    "nlp",
    "computer vision",
    "data science",
    "data analysis",
    "data visualization",
    "power bi",
    "tableau",
    "excel",
    "spark",
    "hadoop",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "docker",
    "kubernetes",
    "jenkins",
    "git",
    "github",
    "linux",
    "terraform",
    "ansible",
    "fastapi",
    "flask",
    "django",
    "react",
    "next.js",
    "node.js",
    "express",
    "html",
    "css",
    "tailwind",
    "rest api",
    "graphql",
    "spring",
    "spring boot",
    "selenium",
    "pytest",
    "cybersecurity",
    "network security",
    "penetration testing",
    "ethical hacking",
    "nlp",
    "mlops",
    "data engineering",
    "airflow",
    "kafka"
}


def extract_skills(text):

    found = set()

    normalized = normalize_text(text)

    for skill in KNOWN_SKILLS:

        skill_normalized = normalize_text(skill)

        if skill_normalized in normalized:
            found.add(skill)

    return found


df["resume_skills"] = df["resume_normalized"].apply(
    extract_skills
)

df["job_skills"] = df["job_normalized"].apply(
    extract_skills
)


def calculate_skill_overlap(row):

    resume_skills = row["resume_skills"]
    job_skills = row["job_skills"]

    if not job_skills:
        return 0.0

    matched = resume_skills.intersection(
        job_skills
    )

    return len(matched) / len(job_skills)


df["skill_overlap"] = df.apply(
    calculate_skill_overlap,
    axis=1
)


df["matched_skill_count"] = df.apply(
    lambda row: len(
        row["resume_skills"].intersection(
            row["job_skills"]
        )
    ),
    axis=1
)


df["required_skill_count"] = (
    df["job_skills"].apply(len)
)


print("\nSkill overlap statistics:")

print(
    df.groupby("label")[
        [
            "skill_overlap",
            "matched_skill_count",
            "required_skill_count"
        ]
    ]
    .agg(["mean", "median", "min", "max"])
    .round(4)
)


# ------------------------------------------------------------
# 5. EXPERIENCE SIGNAL
# ------------------------------------------------------------

print("\n[5/8] Checking experience compatibility...")


# Look for common experience requirements in job descriptions.

def extract_required_experience(text):

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"minimum\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        r"at\s+least\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)"
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text.lower()
        )

        for match in matches:

            try:
                values.append(float(match))
            except ValueError:
                pass

    if values:
        return max(values)

    return 0.0


df["required_experience"] = (
    df["job_description"]
    .fillna("")
    .apply(extract_required_experience)
)


df["experience_gap"] = (
    df["experience_years"]
    - df["required_experience"]
)


df["experience_compatible"] = (
    df["experience_gap"] >= 0
).astype(int)


print("\nExperience statistics:")

print(
    df.groupby("label")[
        [
            "experience_years",
            "required_experience",
            "experience_gap",
            "experience_compatible"
        ]
    ]
    .agg(["mean", "median"])
    .round(3)
)


# ------------------------------------------------------------
# 6. ROLE / JOB TITLE COMPATIBILITY
# ------------------------------------------------------------

print("\n[6/8] Checking role compatibility...")


def role_tokens(role):

    role = normalize_text(role)

    return set(
        token
        for token in role.split()
        if len(token) >= 3
    )


def role_compatibility(row):

    role_words = role_tokens(row["job_role"])

    resume_words = get_words(
        row["resume_normalized"]
    )

    if not role_words:
        return 0.0

    return len(
        role_words.intersection(resume_words)
    ) / len(role_words)


df["role_compatibility"] = df.apply(
    role_compatibility,
    axis=1
)


print("\nRole compatibility statistics:")

print(
    df.groupby("label")["role_compatibility"]
    .agg(["mean", "median", "min", "max"])
    .round(4)
)


# ------------------------------------------------------------
# 7. OVERALL SIGNAL COMPARISON
# ------------------------------------------------------------

print("\n[7/8] Comparing Strong Match vs Weak Match...")


signal_columns = [
    "keyword_overlap",
    "skill_overlap",
    "matched_skill_count",
    "required_skill_count",
    "experience_years",
    "required_experience",
    "experience_gap",
    "experience_compatible",
    "role_compatibility"
]


summary = (
    df.groupby("label")[signal_columns]
    .mean()
    .T
)


print("\nAverage signal values:")

print(
    summary.round(4)
)


# ------------------------------------------------------------
# 8. HIGH-SIGNAL CHECK
# ------------------------------------------------------------

print("\n[8/8] Checking whether matching signals separate labels...")


strong = df[df["label"] == "Strong Match"]

weak = df[df["label"] == "Weak Match"]


print("\nStrong Match averages:")

print(
    strong[signal_columns]
    .mean()
    .round(4)
)


print("\nWeak Match averages:")

print(
    weak[signal_columns]
    .mean()
    .round(4)
)


print("\n" + "=" * 70)
print("MATCHING SIGNAL ANALYSIS COMPLETE")
print("=" * 70)