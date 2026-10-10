import re
from typing import List, Dict


# Common technical skills that FairHire can recognize.
# This is intentionally transparent and easy to extend later.
SKILL_VOCABULARY = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "html",
    "css",
    "react",
    "next.js",
    "node.js",
    "flask",
    "fastapi",
    "django",
    "rest api",
    "rest apis",
    "pandas",
    "numpy",
    "matplotlib",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "xgboost",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "nlp",
    "natural language processing",
    "tf-idf",
    "shap",
    "lime",
    "docker",
    "kubernetes",
    "terraform",
    "aws",
    "azure",
    "google cloud",
    "gcp",
    "jenkins",
    "github actions",
    "git",
    "github",
    "linux",
    "streamlit",
    "folium",
    "mapbox",
    "openstreetmap",
    "blockchain",
    "solidity",
    "data analysis",
    "data visualization",
    "pandas",
    "numpy",
    "power bi",
    "tableau",
    "excel",
]


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving readable text."""
    if not text:
        return ""

    text = text.replace("\r", "\n")

    # Collapse repeated spaces.
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_candidate_name(text: str) -> str:
    """
    Extract the likely candidate name from the beginning
    of the resume.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return ""

    # Usually the candidate name appears in the first few lines.
    for line in lines[:8]:

        # Ignore obvious contact/header lines.
        lower = line.lower()

        if any(
            marker in lower
            for marker in [
                "@",
                "linkedin",
                "github",
                "phone",
                "resume",
                "curriculum vitae",
                "profile",
            ]
        ):
            continue

        # Remove common bullet characters.
        candidate = re.sub(r"^[•▪●\-]+\s*", "", line).strip()

        # A simple name should mostly contain letters/spaces.
        if re.fullmatch(r"[A-Za-z]+(?:\s+[A-Za-z]+){1,4}", candidate):
            return candidate

    return ""


def extract_section(
    text: str,
    section_names: List[str],
) -> str:
    """
    Extract text belonging to a resume section.

    Example:
        SKILLS
        Python, SQL, ...
        PROJECTS
        ...

    returns only the SKILLS content.
    """

    lines = text.splitlines()

    start_index = None

    normalized_names = {
        name.strip().lower()
        for name in section_names
    }

    for index, line in enumerate(lines):

        cleaned = re.sub(
            r"[^a-zA-Z ]",
            "",
            line
        ).strip().lower()

        if cleaned in normalized_names:
            start_index = index + 1
            break

    if start_index is None:
        return ""

    section_lines = []

    known_section_headers = {
        "education",
        "skills",
        "projects",
        "experience",
        "work experience",
        "professional experience",
        "internships",
        "certifications",
        "achievements",
        "achievements hackathons conference presentations",
        "leadership languages",
        "summary",
        "professional summary",
    }

    for line in lines[start_index:]:

        cleaned = re.sub(
            r"[^a-zA-Z ]",
            "",
            line
        ).strip().lower()

        if cleaned in known_section_headers:
            break

        if line.strip():
            section_lines.append(line.strip())

    return "\n".join(section_lines).strip()


def extract_skills(text: str) -> List[str]:
    """Extract recognizable technical skills from resume text."""

    text_lower = text.lower()

    found_skills = []

    for skill in SKILL_VOCABULARY:

        pattern = re.escape(skill.lower())

        if re.search(
            rf"(?<![a-zA-Z0-9]){pattern}(?![a-zA-Z0-9])",
            text_lower,
        ):
            found_skills.append(skill)

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(found_skills))


def extract_experience_years(text: str) -> float:
    """
    Extract explicit years-of-experience statements.

    Examples:
        3 years of experience
        2+ years experience
        1.5 years
    """

    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
    ]

    values = []

    for pattern in patterns:
        matches = re.findall(
            pattern,
            text.lower(),
        )

        for match in matches:
            try:
                values.append(float(match))
            except ValueError:
                pass

    if values:
        return max(values)

    return 0.0


def extract_previous_role(text: str) -> str:
    """
    Attempt to identify a previous/current professional role.

    This is intentionally conservative. If no clear role is found,
    an empty string is returned instead of inventing one.
    """

    role_patterns = [
        r"(?:worked as|working as|previous role|current role|role)\s*[:\-]?\s*([A-Za-z][A-Za-z /&-]{2,60})",
        r"(?:software engineer|data analyst|data scientist|machine learning engineer|ml engineer|"
        r"python developer|web developer|frontend developer|backend developer|"
        r"full stack developer|devops engineer|cloud engineer|"
        r"ai engineer|nlp engineer|business analyst|"
        r"system administrator|software developer)",
    ]

    for pattern in role_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            if match.lastindex:
                role = match.group(1).strip()
            else:
                role = match.group(0).strip()

            return role

    return ""

def extract_projects(text: str) -> List[str]:
    """
    Extract actual project titles from the PROJECTS section.

    A project title is identified as a line containing a project-style
    name followed by ':' or '–'/'-'.
    """

    projects_section = extract_section(
        text,
        ["projects"],
    )

    if not projects_section:
        return []

    projects = []

    for line in projects_section.splitlines():
        cleaned = line.strip()

        if not cleaned:
            continue

        lower = cleaned.lower()

        # Stop if another major section leaked into the result.
        if lower in {
            "achievements, hackathons & conference presentations",
            "achievements",
            "certifications",
            "education",
            "experience",
            "work experience",
            "leadership & languages",
        }:
            break

        # Technology-stack lines are not project titles.
        if "·" in cleaned:
            continue

        # Description lines usually begin with action verbs.
        description_starts = (
            "analyzed ",
            "developed ",
            "processed ",
            "applied ",
            "forecasted ",
            "designed ",
            "implemented ",
            "created ",
            "built ",
            "used ",
            "achieved ",
        )

        if lower.startswith(description_starts):
            continue

        # A project title normally contains ':' or an en/em dash.
        if ":" in cleaned or "–" in cleaned or "—" in cleaned:
            projects.append(cleaned)

    return projects[:10]

def build_resume_intelligence(text: str) -> Dict:
    """Build structured candidate information from resume text."""

    normalized_text = normalize_text(text)

    skills_section = extract_section(
        normalized_text,
        ["skills"],
    )

    projects_section = extract_section(
        normalized_text,
        ["projects"],
    )

    skills = extract_skills(
        skills_section if skills_section else normalized_text
    )

    projects = extract_projects(normalized_text)

    return {
        "candidate_name": extract_candidate_name(normalized_text),
        "skills": skills,
        "experience_years": extract_experience_years(
            normalized_text
        ),
        "previous_role": extract_previous_role(
            normalized_text
        ),
        "projects": projects,
        "skills_section": skills_section,
        "projects_section": projects_section,
    }