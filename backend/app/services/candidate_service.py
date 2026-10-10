import json
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()

# candidate_service.py
# backend/app/services/candidate_service.py
# parents[0] = services
# parents[1] = app
# parents[2] = backend
# parents[3] = project root
PROJECT_ROOT = CURRENT_FILE.parents[3]

CANDIDATE_DATA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "candidate_intelligence"
    / "candidate_intelligence_v2.json"
)


def load_candidate_intelligence():
    """Load the generated candidate intelligence dataset."""

    if not CANDIDATE_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Candidate intelligence file not found: {CANDIDATE_DATA_PATH}"
        )

    with open(CANDIDATE_DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


CANDIDATES = load_candidate_intelligence()


def get_candidate_by_id(candidate_id: str):
    """
    Return candidate intelligence using the numeric candidate ID.

    Example:
        /api/candidate/1562
        -> Candidate 1562
    """

    candidate_name = f"Candidate {candidate_id}"

    for candidate in CANDIDATES:
        if candidate.get("candidate_name") == candidate_name:
            return candidate

    return None