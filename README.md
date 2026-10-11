# FairHire AI Nexus
### Intelligent Resume Screening • Candidate Intelligence • Explainable AI

FairHire AI Nexus is an AI-powered recruitment support platform designed to help recruiters analyze resumes, evaluate candidate-job alignment, identify skill gaps, compare candidates, and explore screening insights through a modern full-stack application.

The project combines machine learning, resume parsing, explainable AI, backend APIs, and a recruiter-focused frontend to make candidate evaluation more structured and transparent.

---

## Overview

Recruiters often need to review large numbers of resumes and compare candidates against job requirements. FairHire AI Nexus aims to support this process by bringing resume screening, candidate insights, and recruiter assistance into one application.

**Core objectives**
- Streamline resume screening and candidate evaluation.
- Identify relevant skills and potential skill gaps.
- Support structured candidate comparison.
- Provide explainability insights for model predictions.
- Enable recruiters to ask questions about candidate screening results.

> **Responsible AI:** Screening outputs are decision-support information, not guarantees of job performance or employment success. Recruiters should review candidates individually and avoid relying on automated scores as the sole basis for hiring decisions.

---

## Key Features

### Resume Screening
- Resume text extraction and processing.
- Candidate evaluation against job-related information.
- Machine-learning-based screening support.
- Structured candidate results.

### Candidate Intelligence
- Organized candidate information.
- Skills and experience insights.
- Identification of missing or relevant skills.
- Candidate comparison support.

### Explainable AI
- SHAP-based model explanations.
- LIME-based candidate explanations.
- Insights intended to help users understand model outputs.

### AI Recruiter Assistant
- Chat interface for recruitment-related questions.
- Questions about candidate strengths and missing skills.
- Candidate-specific chat context when an uploaded candidate ID is supplied and recognized by the backend.

### Full-Stack Architecture
- React and TypeScript frontend.
- FastAPI backend.
- API-based communication between application layers.
- Existing machine-learning models and candidate intelligence services.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn, TF-IDF-based text processing |
| Explainable AI | SHAP, LIME |
| Resume Processing | PyMuPDF and resume parsing utilities |
| API | REST endpoints, JSON |
| Development | Git, GitHub, VS Code |

*The stack reflects the project's intended and existing components; installed versions and exact dependencies are defined by the project files.*

---

## System Architecture

```text
                 ┌──────────────────────────┐
                 │       Recruiter          │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ React + TypeScript UI    │
                 │ Resume & Recruiter Chat  │
                 └────────────┬─────────────┘
                              │ REST API
                              ▼
                 ┌──────────────────────────┐
                 │ FastAPI Backend           │
                 │ Resume & Candidate Logic  │
                 └────────────┬─────────────┘
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
       ┌─────────────┐ ┌──────────────┐ ┌──────────────┐
       │ ML Screening│ │ Candidate    │ │ SHAP / LIME  │
       │ Services    │ │ Intelligence │ │ Explanations │
       └─────────────┘ └──────────────┘ └──────────────┘
```

---

## Project Structure

```text
FairHire-Ai-Nexus/
├── backend/
│   └── app/
│       ├── main.py
│       └── services/
├── frontend/
│   └── src/
│       ├── api/
│       └── pages/
├── dataset/
├── docs/
│   ├── candidate_intelligence/
│   └── explainability/
├── models/
├── notebooks/
├── tests/
└── README.md
```

*This is a high-level overview. The exact contents may vary as the project evolves.*

---

## Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by the project's dependencies.
- Node.js and npm.
- Git.

### 1. Clone the repository

```bash
git clone https://github.com/kaviyaazhagesan23-ui/FairHire-Ai-Nexus.git
cd FairHire-Ai-Nexus
```

### 2. Set up the backend

Open a terminal in the project root:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the backend dependencies using the project's dependency file. For example, if `requirements.txt` is present:

```bash
pip install -r requirements.txt
```

Start the API from the project root using the import path supported by the application:

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

If the backend uses `app.main` from inside the `backend` directory instead, run:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

API documentation is normally available at:

`http://127.0.0.1:8000/docs`

### 3. Set up the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your terminal.

**Configuration note:** Use the frontend's existing API configuration to point to the running backend. If an external AI provider is enabled, configure its API key through backend environment variables or a local `.env` file as required by the project. Never commit secrets to GitHub.

---

## Example Recruiter Questions

The recruiter assistant is intended to support questions such as:

- What are this candidate's key strengths?
- Which skills are missing for the target role?
- Summarize the candidate's relevant experience.
- Compare candidates using available screening information.

Responses depend on the available candidate records, backend services, and configuration.

---

## API Overview

The backend exposes API routes for candidate screening, candidate retrieval, comparisons, explainability, resume uploads, and recruiter chat.

Interactive API documentation:

`http://127.0.0.1:8000/docs`

Refer to the FastAPI documentation generated by the running application for the exact request schemas and available routes.

---

## Security and Responsible Use

- Keep API keys, passwords, tokens, and private environment files out of version control.
- Store secrets in backend environment variables or an appropriate secret manager.
- Validate uploaded files and handle candidate information responsibly.
- Protect personally identifiable information and restrict access to candidate records.
- Treat model outputs as assistance for human review, not definitive hiring decisions.
- Evaluate models for accuracy, fairness, and potential bias before real-world recruitment use.

---

## Current Development Status

FairHire AI Nexus is an actively developed full-stack AI recruitment project. Its codebase includes backend screening and candidate services, explainability components, and a React-based recruiter interface.

Features should be validated against the running application before production deployment. Production use requires appropriate testing, security controls, fairness evaluation, and deployment configuration.

---

## Future Improvements

- Automated test coverage for screening and recruiter workflows.
- More comprehensive fairness and bias audits.
- Improved candidate-specific explanations.
- Secure authentication and role-based access control.
- Deployment automation and monitoring.
- Performance evaluation on representative, appropriately sourced datasets.

---

## Author

**Kaviya Azhagesan**

Computer Science and Engineering — Artificial Intelligence & Machine Learning

GitHub: [@kaviyaazhagesan23-ui](https://github.com/kaviyaazhagesan23-ui)

---

*FairHire AI Nexus — Building more structured, explainable, and responsible recruitment workflows with AI.*
