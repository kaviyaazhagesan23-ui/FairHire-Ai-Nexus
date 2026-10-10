import re
from typing import Any
from app.services.llm_chat_service import generate_hr_answer
from app.services.candidate_service import get_candidate_by_id
from app.services.comparison_service import compare_candidates
import logging

logger = logging.getLogger(__name__)

def _find_candidate_ids(message: str) -> list[str]:
    """Extract candidate IDs mentioned in a message."""
    matches = re.findall(
        r"\bcandidate\s*#?\s*(\d+)\b",
        message,
        flags=re.IGNORECASE,
    )
    return list(dict.fromkeys(matches))


def _candidate_value(candidate: dict[str, Any], *keys: str) -> Any:
    """Read a value from a candidate record without assuming every field exists."""
    for key in keys:
        if key in candidate and candidate[key] is not None:
            return candidate[key]
    return None


def _format_list(value: Any) -> str:
    if not value:
        return "Not available in this candidate record."
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value) or "None listed."
    return str(value)


def _get_candidate(candidate_id: str) -> dict[str, Any] | None:
    try:
        result = get_candidate_by_id(candidate_id)
        return result if isinstance(result, dict) else None
    except (KeyError, ValueError, LookupError):
        return None


def _candidate_summary(candidate: dict[str, Any]) -> str:
    name = _candidate_value(candidate, "candidate_name") or "Unknown candidate"
    role = _candidate_value(candidate, "job_role") or "Not specified"
    prediction = _candidate_value(candidate, "prediction") or "Not available"

    skills = _candidate_value(candidate, "candidate_skills")
    if skills is None:
        skills = candidate.get("skills")

    experience = candidate.get("experience") or {}
    if not isinstance(experience, dict):
        experience = {}

    years = experience.get("candidate_experience_years", "Not available")

    matched = candidate.get("matched_skills", [])
    missing = candidate.get("missing_skills", [])

    lines = [
        f"Candidate: {name}",
        f"Target role: {role}",
        f"Model prediction: {prediction}",
        f"Experience: {years} years",
        f"Skills: {_format_list(skills)}",
        f"Matched skills: {_format_list(matched)}",
        f"Missing skills: {_format_list(missing)}",
    ]

    summary = candidate.get("summary")
    if summary:
        lines.append(f"Candidate summary: {summary}")

    return "\n".join(lines)


def _compare(candidate_ids: list[str]) -> str:
    candidates = []

    for candidate_id in candidate_ids:
        candidate = _get_candidate(candidate_id)
        if candidate is None:
            return (
                f"I couldn't find Candidate {candidate_id}. "
                "Please check the candidate ID and try again."
            )
        candidates.append(candidate)

    try:
        result = compare_candidates(candidates)
    except (KeyError, ValueError, TypeError) as exc:
        return f"I couldn't compare these records: {exc}"

    ranked = result.get("ranked_candidates", [])
    if not ranked:
        return "The comparison service returned no ranked candidates."

    lines = [
        "Candidate comparison results:",
        "Scores are heuristic ranking scores, not SVM probabilities "
        "or automatic hiring decisions.",
    ]

    for item in ranked:
        name = item.get("candidate_name", "Unknown candidate")
        rank = item.get("rank", "N/A")
        score = item.get("ranking_score", "N/A")
        role = item.get("job_role", "Not specified")
        lines.append(
            f"Rank {rank}: {name} — {role} — ranking score: {score}"
        )

        strengths = item.get("strengths")
        if strengths:
            lines.append(f"  Strengths: {_format_list(strengths)}")

        improvements = item.get("improvement_areas")
        if improvements:
            lines.append(
                f"  Improvement areas: {_format_list(improvements)}"
            )

    return "\n".join(lines)

def answer_chat(message: str) -> dict[str, Any]:
    """Answer HR questions naturally using Groq and real candidate data."""

    clean_message = message.strip()

    if not clean_message:
        return {
            "answer": "Hey! What would you like to know about a candidate?",
            "candidate_ids": [],
            "intent": "empty",
        }

    if len(clean_message) > 1000:
        return {
            "answer": "That message is a little long. Please shorten it and try again.",
            "candidate_ids": [],
            "intent": "message_too_long",
        }

    candidate_ids = _find_candidate_ids(clean_message)

    # Build context only from candidate records that actually exist.
    contexts = []
    valid_ids = []

    for candidate_id in candidate_ids:
        candidate = _get_candidate(candidate_id)

        if candidate is not None:
            valid_ids.append(candidate_id)
            contexts.append(_candidate_summary(candidate))

    if candidate_ids and not valid_ids:
        return {
            "answer": (
                "I couldn't find that candidate in the available records. "
                "Could you check the candidate ID?"
            ),
            "candidate_ids": candidate_ids,
            "intent": "candidate_not_found",
        }

    candidate_context = "\n\n".join(contexts)

    # Preserve the existing comparison calculation when multiple IDs are given.
    if len(valid_ids) >= 2:
        candidate_context += "\n\nExisting comparison results:\n" + _compare(valid_ids)

    try:
        answer = generate_hr_answer(
            message=clean_message,
            candidate_context=candidate_context or (
                "No specific candidate was identified. "
                "Answer general HR questions without inventing candidate details."
            ),
        )

        return {
            "answer": answer,
            "candidate_ids": valid_ids,
            "intent": "hr_assistant",
        }

    except Exception:
        logger.exception("Groq chatbot request failed")
    return {
        "answer": (
            "I'm having trouble reaching my AI assistant right now. "
            "Please check the backend terminal for the error."
        ),
        "candidate_ids": valid_ids,
        "intent": "llm_error",
    }