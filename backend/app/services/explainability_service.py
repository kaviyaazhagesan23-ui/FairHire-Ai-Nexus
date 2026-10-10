import pandas as pd
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]

EXPLAINABILITY_DIR = PROJECT_ROOT / "docs" / "explainability"

SHAP_GLOBAL_PATH = (
    EXPLAINABILITY_DIR / "shap_global_feature_importance.csv"
)

SHAP_STRUCTURED_PATH = (
    EXPLAINABILITY_DIR / "shap_structured_feature_importance.csv"
)

SHAP_SAMPLE_PATH = (
    EXPLAINABILITY_DIR / "shap_sample_explanation.csv"
)
SHAP_CANDIDATE_PATH = (
    EXPLAINABILITY_DIR / "shap_candidate_explanations_v2.csv"
)

LIME_CANDIDATE_PATH = (
    EXPLAINABILITY_DIR
    / "lime_candidate_explanations_v2.csv"
)

def load_csv(path: Path):
    """Load an explainability CSV file."""
    if not path.exists():
        raise FileNotFoundError(
            f"Explainability file not found: {path}"
        )

    df = pd.read_csv(path)

    # Convert NaN values into JSON-safe None values
    df = df.where(pd.notna(df), None)

    return df.to_dict(orient="records")


def get_shap_global():
    """Return global SHAP feature importance."""
    return load_csv(SHAP_GLOBAL_PATH)


def get_shap_structured():
    """Return SHAP importance for structured features."""
    return load_csv(SHAP_STRUCTURED_PATH)

def get_shap_candidate(candidate_id: str):
    """
    Return candidate-specific SHAP explanation.
    Supports existing numeric candidates and saved uploaded candidates.
    """
    records = load_csv(SHAP_CANDIDATE_PATH)

    # Preserve compatibility with the existing explanation CSV.
    candidate_name = f"Candidate {candidate_id}"

    matches = [
        record
        for record in records
        if record.get("candidate_name") == candidate_name
        or record.get("candidate_id") == candidate_id
    ]

    return matches


def get_lime_candidate(candidate_id: str):
    """
    Return candidate-specific LIME explanation.
    Supports existing numeric candidates and saved uploaded candidates.
    """
    records = load_csv(LIME_CANDIDATE_PATH)

    candidate_name = f"Candidate {candidate_id}"

    matches = [
        record
        for record in records
        if record.get("candidate_name") == candidate_name
        or record.get("candidate_id") == candidate_id
    ]

    return matches
