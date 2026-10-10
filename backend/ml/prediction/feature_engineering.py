from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# COMMON HELPERS
# ============================================================

def safe_text(value):
    """Convert missing values to empty strings."""
    if pd.isna(value):
        return ""
    return str(value)


# ============================================================
# STRUCTURED MATCHING FEATURES
# ============================================================

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


def calculate_structured_features(row):
    """
    Create the 10 structured matching features used by FairHire V2.

    IMPORTANT:
    This function must be used during training, validation,
    testing, and API prediction so that feature calculation
    remains identical everywhere.
    """

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    resume_skills = {
        skill.strip().lower()
        for skill in safe_text(row.get("skills", "")).split(",")
        if skill.strip()
    }

    required_skills_text = row.get(
        "required_skills",
        row.get("skills", "")
    )

    job_skills = {
        skill.strip().lower()
        for skill in safe_text(required_skills_text).split(",")
        if skill.strip()
    }

    if job_skills:
        matched_skills = resume_skills.intersection(job_skills)

        skill_overlap = (
            len(matched_skills) / len(job_skills)
        )

        matched_skill_count = len(matched_skills)
        required_skill_count = len(job_skills)

    else:
        skill_overlap = 0.0
        matched_skill_count = 0
        required_skill_count = 0

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience_years = float(
        row.get("experience_years", 0) or 0
    )

    required_experience = float(
        row.get("required_experience", 0) or 0
    )

    experience_gap = (
        experience_years - required_experience
    )

    experience_compatible = (
        1.0
        if experience_years >= required_experience
        else 0.0
    )

    # --------------------------------------------------------
    # Role compatibility
    # --------------------------------------------------------

    job_role = safe_text(
        row.get("job_role", "")
    ).lower()

    previous_role = safe_text(
        row.get("previous_role", "")
    ).lower()

    role_compatibility = (
        1.0
        if (
            job_role in previous_role
            or previous_role in job_role
        )
        else 0.0
    )

    # --------------------------------------------------------
    # Project relevance
    # --------------------------------------------------------

    projects = safe_text(
        row.get("projects", "")
    ).lower()

    project_relevance = 0.0

    if projects and job_role:

        role_words = {
            word.strip()
            for word in job_role.replace("-", " ").split()
            if len(word.strip()) > 2
        }

        if role_words:

            matched_project_words = sum(
                1
                for word in role_words
                if word in projects
            )

            project_relevance = (
                matched_project_words
                / len(role_words)
            )

    # --------------------------------------------------------
    # Semantic / lexical overlap
    # --------------------------------------------------------

    resume_text = safe_text(
        row.get("resume_text", "")
    ).lower()

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
        semantic_overlap = (
            len(resume_words.intersection(job_words))
            / len(job_words)
        )
    else:
        semantic_overlap = 0.0

    # --------------------------------------------------------
    # Return features
    # --------------------------------------------------------

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
# DATAFRAME FEATURE CREATION
# ============================================================

def create_structured_features(df):
    """
    Convert a FairHire dataframe into the standardized
    structured feature dataframe.
    """

    features = np.array(
        [
            calculate_structured_features(row)
            for _, row in df.iterrows()
        ],
        dtype=float,
    )

    return pd.DataFrame(
        features,
        columns=FEATURE_COLUMNS,
        index=df.index,
    )


# ============================================================
# TEXT FEATURE CREATION
# ============================================================

def create_combined_text(df):
    """
    Combine resume text and job description for TF-IDF.
    """

    resume_text = (
        df["resume_text"]
        .fillna("")
        .astype(str)
    )

    job_description = (
        df["job_description"]
        .fillna("")
        .astype(str)
    )

    return (
        resume_text
        + " [JOB_DESCRIPTION] "
        + job_description
    )