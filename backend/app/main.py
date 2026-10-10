from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from typing import Annotated
from app.services.uploaded_candidate_service import (
    save_uploaded_candidate,
    get_uploaded_candidate_by_id,
    list_uploaded_candidates,
    delete_uploaded_candidate,
)

from app.services.chatbot_service import answer_chat
from app.services.llm_chat_service import generate_hr_answer
from app.services.comparison_service import compare_candidates as build_comparison
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.candidate_service import get_candidate_by_id
from app.services.resume_parser_service import extract_resume_text
from app.services.prediction_service import predict_candidate
from app.services.upload_explainability_service import (
    get_upload_explanations,
)
from pathlib import Path
from app.services.explainability_service import (
    get_shap_global,
    get_shap_structured,
    get_shap_candidate,
    get_lime_candidate,
)

from app.services.resume_intelligence_service import (
    build_resume_intelligence
)
app = FastAPI(
    title="FairHire AI V2 API",
    description="AI-powered explainable resume screening and candidate intelligence API",
    version="2.0.0",
)

# Allow frontend applications to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class CandidatePredictionRequest(BaseModel):
    resume_text: str
    job_description: str
    skills: str
    required_skills: str = ""
    experience_years: float = 0
    required_experience: float = 0
    job_role: str
    previous_role: str = ""
    projects: str = ""
class CandidateCompareRequest(BaseModel):
    candidate_ids: list[str]
class ChatRequest(BaseModel):
    message: str
    candidate_id: str | None = None
@app.post("/api/predict")
def predict_resume(request: CandidatePredictionRequest):
    result = predict_candidate(
        request.model_dump()
    )

    return {
        "prediction": result["prediction"],
        "decision_score": result["decision_score"],
    }
@app.get("/api/candidate/{candidate_id}")
def get_candidate(candidate_id: str):
    candidate = get_candidate_by_id(candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate {candidate_id} not found",
        )

    return candidate


@app.post("/api/compare")
def compare_candidates(request: CandidateCompareRequest):
    candidate_ids = request.candidate_ids

    if len(candidate_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 candidates are required for comparison.",
        )

    if len(candidate_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="A maximum of 10 candidates can be compared at once.",
        )

    if any(not candidate_id.strip() for candidate_id in candidate_ids):
        raise HTTPException(
            status_code=400,
            detail="Candidate IDs cannot be empty.",
        )

    if len(set(candidate_ids)) != len(candidate_ids):
        raise HTTPException(
            status_code=400,
            detail="Duplicate candidate IDs are not allowed.",
        )

    candidates = []

    for candidate_id in candidate_ids:
        candidate = get_candidate_by_id(candidate_id.strip())

        if candidate is None:
            raise HTTPException(
                status_code=404,
                detail=f"Candidate {candidate_id} not found.",
            )

        candidates.append(candidate)

    return build_comparison(candidates)



@app.post("/api/compare/uploaded")
def compare_uploaded_candidates(request: CandidateCompareRequest):
    candidate_ids = request.candidate_ids

    if len(candidate_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 candidates are required for comparison.",
        )

    if len(candidate_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="A maximum of 10 candidates can be compared at once.",
        )

    if any(not candidate_id.strip() for candidate_id in candidate_ids):
        raise HTTPException(
            status_code=400,
            detail="Candidate IDs cannot be empty.",
        )

    if len(set(candidate_ids)) != len(candidate_ids):
        raise HTTPException(
            status_code=400,
            detail="Duplicate candidate IDs are not allowed.",
        )

    candidates = []

    for candidate_id in candidate_ids:
        candidate = get_uploaded_candidate_by_id(candidate_id.strip())

        if candidate is None:
            raise HTTPException(
                status_code=404,
                detail=f"Uploaded candidate {candidate_id} not found.",
            )

        candidates.append(candidate)

    # Return the real saved records for frontend comparison.
    return {
        "status": "success",
        "count": len(candidates),
        "candidates": candidates,
    }


@app.get("/api/explain/shap/global")
def shap_global():
    return {
        "explanation_type": "SHAP",
        "scope": "global",
        "data": get_shap_global(),
    }


@app.get("/api/explain/shap/structured")
def shap_structured():
    return {
        "explanation_type": "SHAP",
        "scope": "structured_features",
        "data": get_shap_structured(),
    }


@app.get("/api/explain/shap/{candidate_id}")
def shap_candidate(candidate_id: str):

    explanation = get_shap_candidate(candidate_id)

    if not explanation:
        raise HTTPException(
            status_code=404,
            detail=f"SHAP explanation not found for Candidate {candidate_id}",
        )

    return {
        "candidate_id": candidate_id,
        "explanation_type": "SHAP",
        "data": explanation,
    }
@app.get("/api/explain/lime/{candidate_id}")
def lime_candidate(candidate_id: str):

    explanation = get_lime_candidate(candidate_id)

    if not explanation:
        raise HTTPException(
            status_code=404,
            detail=f"LIME explanation not found for Candidate {candidate_id}",
        )

    return {
        "candidate_id": candidate_id,
        "explanation_type": "LIME",
        "data": explanation,
    }

@app.get("/")
def root():
    return {
        "message": "FairHire AI V2 API is running",
        "version": "2.0.0",
        "status": "online",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FairHire AI V2",
        "model": "SVM + TF-IDF + Structured Features",
    }
@app.post("/api/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename was provided."
        )

    filename = file.filename

    allowed_extensions = {".pdf", ".docx"}

    from pathlib import Path

    extension = Path(filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX resume."
        )

    try:
        file_bytes = await file.read()

        text = extract_resume_text(
            filename=filename,
            file_bytes=file_bytes
        )

        return {
            "status": "success",
            "filename": filename,
            "content_type": file.content_type,
            "character_count": len(text),
            "text": text,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {str(exc)}"
        )
@app.post("/api/upload/analyze")
async def analyze_uploaded_resume(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename was provided."
        )

    from pathlib import Path

    extension = Path(file.filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX resume."
        )

    try:
        file_bytes = await file.read()

        resume_text = extract_resume_text(
            filename=file.filename,
            file_bytes=file_bytes
        )

        intelligence = build_resume_intelligence(
            resume_text
        )

        return {
            "status": "success",
            "filename": file.filename,
            "intelligence": intelligence
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Resume analysis failed: {str(exc)}"
        )
@app.post("/api/upload/predict")
async def predict_uploaded_resume(
    file: UploadFile = File(...),
    job_role: str = Form(...),
    job_description: str = Form(...),
    required_skills: str = Form(""),
    required_experience: float = Form(0),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename was provided."
        )

   

    extension = Path(file.filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX resume."
        )

    if not job_role.strip():
        raise HTTPException(
            status_code=400,
            detail="Job role is required."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is required."
        )

    try:
        file_bytes = await file.read()

        resume_text = extract_resume_text(
            filename=file.filename,
            file_bytes=file_bytes
        )

        intelligence = build_resume_intelligence(
            resume_text
        )

        candidate_data = {
            "resume_text": resume_text,
            "job_description": job_description,
            "skills": ", ".join(
                intelligence["skills"]
            ),
            "required_skills": required_skills,
            "experience_years": intelligence[
                "experience_years"
            ],
            "required_experience": required_experience,
            "job_role": job_role,
            "previous_role": intelligence[
                "previous_role"
            ],
            "projects": " ".join(
                intelligence["projects"]
            ),
        }

        prediction_result = predict_candidate(
            candidate_data
        )
        explanations = get_upload_explanations(
    candidate_data
    
)
        
        saved_record = save_uploaded_candidate(
            filename=file.filename,
            file_bytes=file_bytes,
            resume_text=resume_text,
            intelligence=intelligence,
            job={
                "job_role": job_role,
                "job_description": job_description,
                "required_skills": [
                    s.strip()
                    for s in required_skills.split(",")
                    if s.strip()
                ],
                "required_experience": required_experience,
            },
            prediction=prediction_result,
        )


        return {
            "status": "success",
            "filename": file.filename,
            "candidate_id": saved_record["candidate_id"],
            "candidate": {
                "candidate_name": intelligence["candidate_name"],
                "skills": intelligence["skills"],
                "experience_years": intelligence["experience_years"],
                "previous_role": intelligence["previous_role"],
                "projects": intelligence["projects"],
            },
            "job": {
                "job_role": job_role,
                "required_skills": required_skills,
                "required_experience": required_experience,
            },
            "prediction": {
                "label": prediction_result["prediction"],
                "decision_score": prediction_result["decision_score"],
            },
            "explanations": {
                "available": True,
                "shap": explanations["shap"],
                "lime": explanations["lime"],
            },
        }


    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Resume prediction failed: {str(exc)}"
        )

@app.post("/api/chat")
def chat_with_hr_assistant(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    if len(message) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Message cannot exceed 1000 characters.",
        )

    candidate_id = (
        request.candidate_id.strip()
        if request.candidate_id
        else None
    )

    # Uploaded resume: use the actual saved candidate record.
    if candidate_id and candidate_id.startswith("UP-"):
        candidate = get_uploaded_candidate_by_id(candidate_id)

        if candidate is None:
            raise HTTPException(
                status_code=404,
                detail="Uploaded candidate not found.",
            )

        context = (
            f"Candidate ID: {candidate.get('candidate_id')}\n"
            f"Source: Uploaded resume\n"
            f"Filename: {candidate.get('filename')}\n"
            f"Candidate details: {candidate.get('candidate')}\n"
            f"Job details: {candidate.get('job')}\n"
            f"Prediction: {candidate.get('prediction')}\n"
            f"Evaluation: {candidate.get('evaluation')}\n"
        )

        try:
            answer = generate_hr_answer(
                message=message,
                candidate_context=context,
            )
            return {
                "answer": answer,
                "candidate_ids": [candidate_id],
                "intent": "hr_assistant",
            }
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        except Exception:
            import logging
            logging.getLogger(__name__).exception(
                "Uploaded candidate chat failed"
            )
            raise HTTPException(
                status_code=502,
                detail="AI response failed. Check the backend terminal.",
            )

    # Preserve existing synthetic-candidate chatbot behavior.
    return answer_chat(message)


@app.post("/api/compare/uploads")
async def compare_uploaded_resumes(
    
    files: list[UploadFile] = File(
    ...,
    media_type="multipart/form-data",
),
    job_role: str = Form(...),
    job_description: str = Form(...),
    required_skills: str = Form(""),
    required_experience: float = Form(0),
):
    """
    Evaluate 2-10 recruiter-uploaded resumes against one job.
    Candidate records are never fetched from the saved dataset.
    """

    if not job_role.strip():
        raise HTTPException(status_code=400, detail="Job role is required.")

    if not job_description.strip():
        raise HTTPException(
            status_code=400, detail="Job description is required."
        )

    if required_experience < 0:
        raise HTTPException(
            status_code=400,
            detail="Required experience cannot be negative.",
        )

    if not 2 <= len(files) <= 10:
        raise HTTPException(
            status_code=400,
            detail="Upload between 2 and 10 resumes.",
        )

    allowed_extensions = {".pdf", ".docx"}
    required = {
        skill.strip().casefold()
        for skill in required_skills.split(",")
        if skill.strip()
    }

    async def analyze_upload(upload: UploadFile):
        filename = upload.filename or "unnamed"
        extension = Path(filename).suffix.lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"{filename}: upload a PDF or DOCX file.",
            )

        file_bytes = await upload.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"{filename}: uploaded file is empty.",
            )

        resume_text = extract_resume_text(
            filename=filename,
            file_bytes=file_bytes,
        )

        if not resume_text or not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail=f"{filename}: no readable resume text was extracted.",
            )

        intelligence = build_resume_intelligence(resume_text)

        raw_skills = intelligence.get("skills") or []
        if isinstance(raw_skills, str):
            raw_skills = raw_skills.split(",")

        skills = [
            str(skill).strip()
            for skill in raw_skills
            if str(skill).strip()
        ]

        raw_projects = intelligence.get("projects") or []
        if isinstance(raw_projects, str):
            projects = raw_projects
        else:
            projects = " ".join(str(p) for p in raw_projects)

        experience = float(
            intelligence.get("experience_years") or 0
        )

        candidate_data = {
            "resume_text": resume_text,
            "job_description": job_description.strip(),
            "skills": ", ".join(skills),
            "required_skills": required_skills.strip(),
            "experience_years": experience,
            "required_experience": required_experience,
            "job_role": job_role.strip(),
            "previous_role": intelligence.get("previous_role") or "",
            "projects": projects,
        }

        prediction = predict_candidate(candidate_data)

        resume_skills = {s.casefold() for s in skills}
        matched = sorted(resume_skills & required)
        missing = sorted(required - resume_skills)

        skill_match = (
            len(matched) / len(required) * 100
            if required else None
        )
        experience_met = experience >= required_experience

        # Transparent screening score, not a probability:
        # 80% required-skill coverage + 20% experience requirement.
        # If no required skills were supplied, use experience only.
        if required:
            match_score = (
                0.8 * (skill_match or 0)
                + 20.0 * float(experience_met)
            )
        else:
            match_score = 100.0 if experience_met else 0.0
        
        saved_record = save_uploaded_candidate(
            filename=filename,
            file_bytes=file_bytes,
            resume_text=resume_text,
            intelligence={
                **intelligence,
                "skills": skills,
                "projects": (
                    raw_projects.split()
                    if isinstance(raw_projects, str)
                    else raw_projects
                ),
            },
            job={
                "job_role": job_role.strip(),
                "job_description": job_description.strip(),
                "required_skills": sorted(required),
                "required_experience": required_experience,
            },
            prediction=prediction,
            evaluation={
                "screening_match_score": round(match_score, 2),
            },
        )

        candidate_id = saved_record["candidate_id"]


        return {
            "candidate_id": candidate_id,
            "filename": filename,
            "candidate": {
                "candidate_name": intelligence.get("candidate_name"),
                "skills": skills,
                "experience_years": experience,
                "previous_role": candidate_data["previous_role"],
                "projects": intelligence.get("projects") or [],
            },
            "evaluation": {
                "prediction": prediction.get("prediction"),
                "decision_score": prediction.get("decision_score"),
                "matched_skills": matched,
                "missing_skills": missing,
                "matched_skill_count": len(matched),
                "required_skill_count": len(required),
                "skill_match_percentage": (
                    round(skill_match, 2)
                    if skill_match is not None else None
                ),
                "experience_requirement_met": experience_met,
                "screening_match_score": round(match_score, 2),
            },
        }

    try:
        # Evaluate only the files included in this request.
        results = []
        seen_names = set()

        for upload in files:
            result = await analyze_upload(upload)

            # Avoid accidental duplicate uploads with identical filenames.
            # Filenames are not treated as candidate IDs.
            filename_key = result["filename"].casefold()
            if filename_key in seen_names:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Duplicate filenames detected. Rename the files "
                        "so each uploaded resume has a unique filename."
                    ),
                )

            seen_names.add(filename_key)
            results.append(result)

        results.sort(
            key=lambda item: item["evaluation"]["screening_match_score"],
            reverse=True,
        )

        for rank, result in enumerate(results, start=1):
            result["rank"] = rank

        return {
            "status": "success",
            "source": "uploaded_resumes_only",
            "job": {
                "job_role": job_role.strip(),
                "job_description": job_description.strip(),
                "required_skills": sorted(required),
                "required_experience": required_experience,
            },
            "ranking_method": (
                "80% required-skill coverage + 20% experience requirement "
                "when required skills are provided; otherwise based on "
                "the experience requirement alone."
            ),
            "score_note": (
                "The screening match score is a transparent rule-based "
                "screening metric, not a probability of employment success. "
                "The SVM decision score is a separate model output. "
                "Review resumes individually and do not use automated "
                "scores as the sole basis for hiring."
            ),
            "count": len(results),
            "results": results,
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not evaluate the uploaded resumes: {exc}",
        )
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Uploaded resume comparison failed"
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "Resume comparison failed. Check the backend terminal "
                "for the error details."
            ),
        )
    
@app.get("/api/uploaded-candidates")
def get_uploaded_candidates():
    try:
        candidates = list_uploaded_candidates()
        return {
            "status": "success",
            "count": len(candidates),
            "candidates": candidates,
        }
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Could not list uploaded candidates"
        )
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve uploaded candidates.",
        )


@app.get("/api/uploaded-candidates/{candidate_id}")
def get_uploaded_candidate(candidate_id: str):
    try:
        candidate = get_uploaded_candidate_by_id(candidate_id)
        if candidate is None:
            raise HTTPException(
                status_code=404,
                detail="Uploaded candidate not found.",
            )
        return {"status": "success", "candidate": candidate}
    except HTTPException:
        raise
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Could not retrieve uploaded candidate"
        )
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve uploaded candidate.",
        )

@app.delete("/api/uploaded-candidates/{candidate_id}")
def delete_uploaded_candidate_endpoint(candidate_id: str):
    try:
        deleted = delete_uploaded_candidate(candidate_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Uploaded candidate not found.",
            )

        return {
            "status": "success",
            "message": "Uploaded candidate deleted successfully.",
            "candidate_id": candidate_id,
        }

    except HTTPException:
        raise
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Could not delete uploaded candidate"
        )
        raise HTTPException(
            status_code=500,
            detail="Could not delete uploaded candidate.",
        )
