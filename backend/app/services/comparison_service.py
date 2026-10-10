
from typing import Any


WEIGHTS = {
    "skill_match": 0.40,
    "experience_fit": 0.20,
    "semantic_overlap": 0.15,
    "project_relevance": 0.15,
    "role_compatibility": 0.10,
}


def build_comparison_record(candidate: dict) -> dict:
    features = candidate.get("model_features") or {}
    experience = candidate.get("experience") or {}
    role = candidate.get("role_analysis") or {}
    projects = candidate.get("project_analysis") or {}

    matched = candidate.get("matched_skills") or []
    missing = candidate.get("missing_skills") or []
    skills = candidate.get("candidate_skills") or []
    required = candidate.get("required_skills") or []

    matched_count = candidate.get(
        "matched_skill_count", len(matched)
    )
    required_count = candidate.get(
        "required_skill_count", len(required)
    )

    skill_match = (
        min(1.0, matched_count / required_count)
        if required_count > 0 else 1.0
    )

    experience_fit = float(
        bool(experience.get("experience_compatible", False))
    )
    semantic_overlap = float(
        features.get("semantic_overlap", 0) or 0
    )
    project_relevance = float(
        projects.get("project_relevance",
                     features.get("project_relevance", 0)) or 0
    )
    role_compatibility = float(
        bool(role.get("role_compatible", False))
    )

    metrics = {
        "skill_match": skill_match,
        "experience_fit": experience_fit,
        "semantic_overlap": semantic_overlap,
        "project_relevance": project_relevance,
        "role_compatibility": role_compatibility,
    }

    score = round(
        sum(metrics[key] * weight for key, weight in WEIGHTS.items())
        * 100,
        2,
    )

    strengths = []
    improvement_areas = []

    if skill_match >= 0.75:
        strengths.append("Strong required-skill coverage")
    elif skill_match < 0.50:
        improvement_areas.append("Review required-skill gaps")

    if experience_fit:
        strengths.append("Meets or exceeds the experience requirement")
    else:
        improvement_areas.append("Review experience compatibility")

    if semantic_overlap >= 0.30:
        strengths.append("Good resume and job-description text overlap")
    else:
        improvement_areas.append("Improve job-specific resume alignment")

    if project_relevance >= 0.50:
        strengths.append("Highly relevant project experience")
    elif project_relevance < 0.20:
        improvement_areas.append("Highlight role-relevant projects")

    if role_compatibility:
        strengths.append("Previous role is compatible with the target role")
    else:
        improvement_areas.append("Review previous-role relevance")

    return {
        "candidate_name": candidate.get("candidate_name"),
        "job_role": candidate.get("job_role"),
        "model_prediction": candidate.get("prediction", "Not available"),
        "ranking_score": score,
        "ranking_score_type": "Heuristic score, not model probability",
        "metrics": metrics,
        "skills": {
            "candidate_skills": skills,
            "required_skills": required,
            "matched_skills": matched,
            "missing_skills": missing,
            "matched_skill_count": matched_count,
            "required_skill_count": required_count,
        },
        "experience": experience,
        "role_analysis": role,
        "project_analysis": projects,
        "strengths": strengths,
        "improvement_areas": improvement_areas,
        "original_candidate": candidate,
    }


def compare_candidates(candidates: list[dict]) -> dict:
    ranked = [build_comparison_record(c) for c in candidates]

    ranked.sort(
        key=lambda item: item["ranking_score"],
        reverse=True,
    )

    for index, candidate in enumerate(ranked, start=1):
        candidate["rank"] = index

    return {
        "comparison_type": "Candidate Comparison and Ranking",
        "candidate_count": len(ranked),
        "score_explanation": (
            "Scores use weighted skill match (40%), experience fit (20%), "
            "semantic overlap (15%), project relevance (15%), and role "
            "compatibility (10%). Scores are heuristic comparisons, not "
            "SVM probabilities or hiring recommendations."
        ),
        "weights": WEIGHTS,
        "ranked_candidates": ranked,
        "candidates": candidates,
    }