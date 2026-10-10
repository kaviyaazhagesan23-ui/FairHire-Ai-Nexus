
import json
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone

import mysql.connector
from dotenv import load_dotenv


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]

load_dotenv(PROJECT_ROOT / "backend" / ".env")

UPLOAD_DATA_DIR = PROJECT_ROOT / "data" / "uploaded_candidates"
RESUMES_DIR = UPLOAD_DATA_DIR / "resumes"


def _ensure_storage():
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)


def _get_connection():
    """Create a connection using credentials from backend/.env."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "fairhire_ai"),
    )


def _json_value(value):
    """Convert Python data to JSON suitable for MySQL JSON columns."""
    return json.dumps(value if value is not None else [])


def _first_value(data, *keys, default=None):
    """Read the first available key from a dictionary."""
    for key in keys:
        if data.get(key) is not None:
            return data[key]
    return default


def _row_to_record(row):
    """Convert a MySQL row into a candidate record."""
    if not row:
        return None

    skills = row.get("skills") or []
    projects = row.get("projects") or []
    required_skills = row.get("required_skills") or []

    # MySQL JSON values may be returned as either Python objects
    # or JSON strings depending on connector configuration.
    for key, value in (
        ("skills", skills),
        ("projects", projects),
        ("required_skills", required_skills),
    ):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass

        if key == "skills":
            skills = value
        elif key == "projects":
            projects = value
        else:
            required_skills = value

    return {
        "candidate_id": row["candidate_id"],
        "source": "recruiter_upload",
        "filename": row["filename"],
        "candidate": {
            "candidate_name": row.get("candidate_name"),
            "skills": skills,
            "experience_years": float(row.get("experience_years") or 0),
            "previous_role": row.get("previous_role") or "",
            "projects": projects,
        },
        "job": {
            "job_role": row.get("job_role") or "",
            "job_description": row.get("job_description") or "",
            "required_skills": required_skills,
            "required_experience": float(
                row.get("required_experience") or 0
            ),
        },
        "prediction": {
            "prediction": row.get("prediction"),
            "decision_score": (
                float(row["decision_score"])
                if row.get("decision_score") is not None
                else None
            ),
        },
        "evaluation": {
            "screening_match_score": (
                float(row["screening_match_score"])
                if row.get("screening_match_score") is not None
                else None
            ),
        },
        "resume_path": row["resume_path"],
        "created_at": (
            row["created_at"].isoformat()
            if row.get("created_at")
            else None
        ),
    }


def save_uploaded_candidate(
    filename: str,
    file_bytes: bytes,
    resume_text: str,
    intelligence: dict,
    job: dict,
    prediction: dict,
    evaluation: dict | None = None,
):
    """Save a real uploaded resume file and its record in MySQL."""
    _ensure_storage()
    evaluation = evaluation or {}

    candidate_id = f"UP-{uuid.uuid4().hex[:12].upper()}"
    safe_filename = Path(filename).name
    extension = Path(safe_filename).suffix.lower()

    # Keep the uploaded file on disk; store its relative path in MySQL.
    resume_path = RESUMES_DIR / f"{candidate_id}{extension}"
    relative_resume_path = resume_path.relative_to(PROJECT_ROOT).as_posix()

    skills = intelligence.get("skills") or []
    projects = intelligence.get("projects") or []
    required_skills = job.get("required_skills") or []

    candidate_name = intelligence.get("candidate_name")
    experience_years = intelligence.get("experience_years") or 0
    previous_role = intelligence.get("previous_role") or ""

    job_role = _first_value(job, "job_role", "role", default="")
    job_description = job.get("job_description") or ""
    required_experience = job.get("required_experience") or 0

    prediction_label = _first_value(
        prediction, "prediction", "label", "result", default=""
    )
    decision_score = prediction.get("decision_score")
    match_score = _first_value(
        evaluation,
        "screening_match_score",
        "match_score",
        "score",
    )

    record = None
    connection = None

    try:
        resume_path.write_bytes(file_bytes)

        connection = _get_connection()
        cursor = connection.cursor()

        sql = """
            INSERT INTO uploaded_candidates (
                candidate_id,
                candidate_name,
                filename,
                skills,
                experience_years,
                previous_role,
                projects,
                job_role,
                job_description,
                required_skills,
                required_experience,
                prediction,
                decision_score,
                screening_match_score,
                resume_path
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
        """

        values = (
            candidate_id,
            candidate_name,
            safe_filename,
            _json_value(skills),
            experience_years,
            previous_role,
            _json_value(projects),
            job_role,
            job_description,
            _json_value(required_skills),
            required_experience,
            str(prediction_label),
            decision_score,
            match_score,
            relative_resume_path,
        )

        cursor.execute(sql, values)
        connection.commit()

        record = get_uploaded_candidate_by_id(candidate_id)

    except Exception:
        # Do not leave an orphaned resume if saving the DB row fails.
        if connection is not None:
            try:
                connection.rollback()
            except Exception:
                pass

        if resume_path.exists():
            resume_path.unlink()

        raise

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

    return record


def get_uploaded_candidate_by_id(candidate_id: str):
    """Retrieve only a real recruiter-uploaded candidate."""
    connection = _get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM uploaded_candidates WHERE candidate_id = %s",
            (candidate_id,),
        )
        row = cursor.fetchone()
        return _row_to_record(row)
    finally:
        cursor.close()
        connection.close()


def list_uploaded_candidates():
    """List real uploaded candidates, newest first."""
    connection = _get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM uploaded_candidates ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
        return [_row_to_record(row) for row in rows]
    finally:
        cursor.close()
        connection.close()

def delete_uploaded_candidate(candidate_id: str):
    """Delete an uploaded candidate and safely remove its saved resume."""
    connection = _get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT resume_path FROM uploaded_candidates WHERE candidate_id = %s",
            (candidate_id,),
        )
        row = cursor.fetchone()

        if not row:
            return False

        resume_path = row.get("resume_path")

        cursor.execute(
            "DELETE FROM uploaded_candidates WHERE candidate_id = %s",
            (candidate_id,),
        )

        # Check whether another candidate record references this same file.
        cursor.execute(
            "SELECT COUNT(*) AS total FROM uploaded_candidates WHERE resume_path = %s",
            (resume_path,),
        )
        remaining = cursor.fetchone()["total"]

        connection.commit()

        # Only remove files inside the dedicated resumes directory.
        if resume_path and remaining == 0:
            stored_path = (PROJECT_ROOT / resume_path).resolve()
            resumes_root = RESUMES_DIR.resolve()

            if stored_path != resumes_root and resumes_root in stored_path.parents:
                if stored_path.is_file():
                    stored_path.unlink()

        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
