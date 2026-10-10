import re
from typing import Dict, List

import pandas as pd

from ml.prediction.feature_engineering import (
    calculate_structured_features,
)


# ============================================================
# TEXT / SKILL HELPERS
# ============================================================

def normalize_skill(skill: str) -> str:
    """Normalize a skill for comparison."""

    skill = str(skill).strip().lower()

    skill = re.sub(
        r"\s+",
        " ",
        skill
    )

    return skill


def parse_skills(value) -> List[str]:
    """Convert comma-separated skills into a normalized list."""

    if pd.isna(value):
        return []

    text = str(value)

    skills = [
        normalize_skill(skill)
        for skill in text.split(",")
    ]

    return [
        skill
        for skill in skills
        if skill
    ]


# ============================================================
# SKILL ANALYSIS
# ============================================================

def analyze_skills(row) -> Dict:

    candidate_skills = set(
        parse_skills(
            row.get("skills", "")
        )
    )

    required_skills = set(
        parse_skills(
            row.get(
                "required_skills",
                row.get("skills", "")
            )
        )
    )

    matched_skills = sorted(
        candidate_skills.intersection(
            required_skills
        )
    )

    missing_skills = sorted(
        required_skills.difference(
            candidate_skills
        )
    )

    return {
        "candidate_skills": sorted(
            candidate_skills
        ),
        "required_skills": sorted(
            required_skills
        ),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_skill_count": len(
            matched_skills
        ),
        "required_skill_count": len(
            required_skills
        ),
    }


# ============================================================
# EXPERIENCE ANALYSIS
# ============================================================

def analyze_experience(row) -> Dict:

    experience = float(
        row.get(
            "experience_years",
            0
        )
    )

    required_experience = float(
        row.get(
            "required_experience",
            0
        )
    )

    gap = experience - required_experience

    if gap >= 0:
        status = "Meets or exceeds requirement"
    elif gap >= -2:
        status = "Slightly below requirement"
    else:
        status = "Below requirement"

    return {
        "candidate_experience_years": experience,
        "required_experience_years": required_experience,
        "experience_gap_years": round(
            gap,
            2
        ),
        "experience_status": status,
        "experience_compatible": bool(
            experience >= required_experience
        ),
    }


# ============================================================
# ROLE ANALYSIS
# ============================================================

def analyze_role_compatibility(row) -> Dict:

    job_role = str(
        row.get(
            "job_role",
            ""
        )
    ).strip()

    previous_role = str(
        row.get(
            "previous_role",
            ""
        )
    ).strip()

    job_role_lower = job_role.lower()
    previous_role_lower = previous_role.lower()

    compatible = (
        job_role_lower in previous_role_lower
        or previous_role_lower in job_role_lower
    )

    if compatible:
        status = "Relevant previous role"
    elif previous_role:
        status = "Different previous role"
    else:
        status = "Previous role unavailable"

    return {
        "target_role": job_role,
        "previous_role": previous_role,
        "role_compatible": bool(
            compatible
        ),
        "role_compatibility_status": status,
    }


# ============================================================
# PROJECT ANALYSIS
# ============================================================

def analyze_projects(row) -> Dict:

    projects = str(
        row.get(
            "projects",
            ""
        )
    ).strip()

    job_role = str(
        row.get(
            "job_role",
            ""
        )
    ).strip()

    if not projects:
        return {
            "project_relevance": 0.0,
            "project_relevance_status": "No projects provided",
        }

    role_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            job_role.lower()
        )
    )

    project_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            projects.lower()
        )
    )

    overlap = role_words.intersection(
        project_words
    )

    if role_words:
        relevance = len(overlap) / len(
            role_words
        )
    else:
        relevance = 0.0

    relevance = min(
        max(
            relevance,
            0.0
        ),
        1.0
    )

    if relevance >= 0.5:
        status = "Highly relevant projects"
    elif relevance > 0:
        status = "Somewhat relevant projects"
    else:
        status = "Limited direct project relevance"

    return {
        "project_relevance": round(
            relevance,
            4
        ),
        "project_relevance_status": status,
    }


# ============================================================
# CANDIDATE SUMMARY
# ============================================================

def generate_candidate_summary(
    prediction: str,
    skill_info: Dict,
    experience_info: Dict,
    role_info: Dict,
    project_info: Dict,
) -> str:

    positive_points = []

    if skill_info["matched_skill_count"] > 0:
        positive_points.append(
            f"{skill_info['matched_skill_count']} "
            "required skills matched"
        )

    if experience_info[
        "experience_compatible"
    ]:
        positive_points.append(
            "experience requirement satisfied"
        )

    if role_info[
        "role_compatible"
    ]:
        positive_points.append(
            "previous role is relevant"
        )

    if project_info[
        "project_relevance"
    ] > 0:
        positive_points.append(
            "relevant project experience"
        )

    if prediction == "Strong Match":

        if positive_points:
            return (
                "Strong candidate with "
                + ", ".join(
                    positive_points
                )
                + "."
            )

        return (
            "The model classified this "
            "candidate as a Strong Match."
        )

    # Weak Match

    improvement_points = []

    if skill_info[
        "missing_skill_count"
        if "missing_skill_count"
        in skill_info
        else "matched_skill_count"
    ]:
        pass

    if skill_info["missing_skills"]:
        improvement_points.append(
            "additional required skills may "
            "be needed"
        )

    if not experience_info[
        "experience_compatible"
    ]:
        improvement_points.append(
            "experience is below the requirement"
        )

    if not role_info[
        "role_compatible"
    ]:
        improvement_points.append(
            "previous role has limited direct "
            "role compatibility"
        )

    if improvement_points:
        return (
            "Candidate may need improvement in "
            + ", ".join(
                improvement_points
            )
            + "."
        )

    return (
        "The model classified this candidate "
        "as a Weak Match."
    )


# ============================================================
# COMPLETE CANDIDATE INTELLIGENCE
# ============================================================

def build_candidate_intelligence(
    row,
    prediction: str,
) -> Dict:

    skill_info = analyze_skills(row)

    experience_info = analyze_experience(
        row
    )

    role_info = analyze_role_compatibility(
        row
    )

    project_info = analyze_projects(
        row
    )

    # Add model structured features
    structured_features = (
        calculate_structured_features(
            row
        )
    )

    result = {
        "candidate_name": row.get(
            "candidate_name",
            "Unknown Candidate"
        ),
        "job_role": row.get(
            "job_role",
            "Unknown Role"
        ),
        "prediction": prediction,

        "candidate_skills": skill_info[
            "candidate_skills"
        ],

        "required_skills": skill_info[
            "required_skills"
        ],

        "matched_skills": skill_info[
            "matched_skills"
        ],

        "missing_skills": skill_info[
            "missing_skills"
        ],

        "matched_skill_count": skill_info[
            "matched_skill_count"
        ],

        "required_skill_count": skill_info[
            "required_skill_count"
        ],

        "experience": experience_info,

        "role_analysis": role_info,

        "project_analysis": project_info,

        "model_features": {
    feature_name: float(feature_value)
    for feature_name, feature_value in zip(
        [
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
        ],
        structured_features,
    )
},
    }

    result["summary"] = (
        generate_candidate_summary(
            prediction,
            skill_info,
            experience_info,
            role_info,
            project_info,
        )
    )

    return result