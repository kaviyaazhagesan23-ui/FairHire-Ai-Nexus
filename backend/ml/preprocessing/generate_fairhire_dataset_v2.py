from pathlib import Path
import random
import pandas as pd

# ============================================================
# FairHire AI - Synthetic Dataset V2 Generator
# ============================================================

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[3]

OUTPUT_PATH = (
    ROOT
    / "dataset"
    / "raw"
    / "fairhire_synthetic_dataset_v2_3000.csv"
)

TOTAL_ROWS = 3000
ROWS_PER_ROLE = 150
STRONG_PER_ROLE = 75
WEAK_PER_ROLE = 75


# ============================================================
# ROLE DEFINITIONS
# ============================================================

ROLES = {
    "AI/ML Engineer": {
        "skills": [
            "Python", "Machine Learning", "Deep Learning",
            "TensorFlow", "PyTorch", "Scikit-learn",
            "Pandas", "NumPy", "SQL", "NLP"
        ],
        "projects": [
            "machine learning prediction system",
            "deep learning image classification project",
            "NLP text classification system",
            "AI recommendation system"
        ],
        "previous_roles": [
            "ML Intern", "Python Developer", "AI Intern",
            "Data Science Intern"
        ],
        "industries": [
            "Artificial Intelligence", "Software", "Technology"
        ],
        "education": [
            "B.Tech Computer Science",
            "B.E. Computer Science",
            "M.Tech Artificial Intelligence",
            "M.Sc Data Science"
        ],
        "certifications": [
            "TensorFlow Developer",
            "AWS Certified Machine Learning",
            "Google Professional Machine Learning Engineer"
        ],
    },

    "Machine Learning Engineer": {
        "skills": [
            "Python", "Machine Learning", "Scikit-learn",
            "TensorFlow", "PyTorch", "Pandas", "NumPy",
            "SQL", "Feature Engineering", "Model Deployment"
        ],
        "projects": [
            "machine learning classification system",
            "customer prediction model",
            "fraud detection model",
            "automated ML pipeline"
        ],
        "previous_roles": [
            "ML Intern", "Data Analyst", "Python Developer",
            "Junior ML Engineer"
        ],
        "industries": ["Technology", "Software", "FinTech"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Computer Science",
            "M.Tech Machine Learning",
            "M.Sc Data Science"
        ],
        "certifications": [
            "AWS Certified Machine Learning",
            "Google Professional Machine Learning Engineer",
            "Microsoft Azure AI Engineer"
        ],
    },

    "Data Scientist": {
        "skills": [
            "Python", "Machine Learning", "Statistics",
            "Pandas", "NumPy", "Scikit-learn",
            "SQL", "Data Visualization", "Feature Engineering",
            "Jupyter"
        ],
        "projects": [
            "customer churn prediction",
            "sales forecasting system",
            "customer segmentation project",
            "predictive analytics project"
        ],
        "previous_roles": [
            "Data Analyst", "Research Intern",
            "Data Science Intern", "Business Analyst"
        ],
        "industries": ["Analytics", "Technology", "FinTech", "Retail"],
        "education": [
            "B.Tech Computer Science",
            "B.Sc Statistics",
            "M.Sc Data Science",
            "M.Tech Data Science"
        ],
        "certifications": [
            "IBM Data Science Professional",
            "Google Data Analytics",
            "Microsoft Power BI"
        ],
    },

    "Data Analyst": {
        "skills": [
            "SQL", "Excel", "Python", "Pandas",
            "Data Visualization", "Power BI", "Tableau",
            "Statistics", "Data Cleaning", "Reporting"
        ],
        "projects": [
            "sales analytics dashboard",
            "business intelligence dashboard",
            "customer analytics project",
            "financial reporting dashboard"
        ],
        "previous_roles": [
            "Data Analyst Intern", "Business Analyst",
            "Reporting Analyst", "Research Assistant"
        ],
        "industries": ["Analytics", "Finance", "Retail", "Consulting"],
        "education": [
            "B.Tech Computer Science",
            "B.Com",
            "B.Sc Statistics",
            "M.Sc Data Analytics"
        ],
        "certifications": [
            "Google Data Analytics",
            "Microsoft Power BI",
            "Tableau Desktop Specialist"
        ],
    },

    "Data Engineer": {
        "skills": [
            "Python", "SQL", "ETL", "Apache Spark",
            "Hadoop", "Airflow", "Data Pipelines",
            "AWS", "Azure", "Database Management"
        ],
        "projects": [
            "ETL data pipeline",
            "real-time data processing pipeline",
            "cloud data warehouse",
            "large scale data processing system"
        ],
        "previous_roles": [
            "Data Engineer Intern", "Database Developer",
            "Python Developer", "ETL Developer"
        ],
        "industries": ["Technology", "Cloud", "FinTech"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Information Technology",
            "M.Tech Data Engineering",
            "B.Sc Computer Science"
        ],
        "certifications": [
            "AWS Certified Data Engineer",
            "Azure Data Engineer Associate",
            "Google Professional Data Engineer"
        ],
    },

    "Software Engineer": {
        "skills": [
            "Python", "Java", "C++", "Data Structures",
            "Algorithms", "Git", "REST API",
            "SQL", "Object Oriented Programming", "Testing"
        ],
        "projects": [
            "web application",
            "backend software system",
            "REST API application",
            "software automation platform"
        ],
        "previous_roles": [
            "Software Developer Intern",
            "Junior Software Engineer",
            "Backend Developer"
        ],
        "industries": ["Software", "Technology", "IT Services"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Computer Science",
            "B.E. Information Technology",
            "MCA"
        ],
        "certifications": [
            "Oracle Java Certification",
            "Microsoft Azure Fundamentals",
            "AWS Certified Developer"
        ],
    },

    "Backend Developer": {
        "skills": [
            "Python", "Java", "Node.js", "FastAPI",
            "Django", "REST API", "SQL",
            "PostgreSQL", "MongoDB", "Git"
        ],
        "projects": [
            "REST API backend",
            "microservices application",
            "database driven web application",
            "FastAPI backend system"
        ],
        "previous_roles": [
            "Backend Developer Intern",
            "Python Developer",
            "Software Developer"
        ],
        "industries": ["Software", "Technology", "SaaS"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Computer Science",
            "MCA",
            "B.Sc Computer Science"
        ],
        "certifications": [
            "AWS Certified Developer",
            "Oracle Java Certification",
            "Microsoft Azure Developer"
        ],
    },

    "Frontend Developer": {
        "skills": [
            "HTML", "CSS", "JavaScript", "React",
            "TypeScript", "Next.js", "Tailwind CSS",
            "Responsive Design", "Git", "UI Development"
        ],
        "projects": [
            "responsive web application",
            "React dashboard",
            "Next.js website",
            "interactive frontend application"
        ],
        "previous_roles": [
            "Frontend Developer Intern",
            "Web Developer",
            "UI Developer"
        ],
        "industries": ["Software", "Technology", "Digital Services"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Information Technology",
            "B.Sc Computer Science",
            "MCA"
        ],
        "certifications": [
            "Meta Front-End Developer",
            "Google UX Design",
            "Microsoft Web Development"
        ],
    },

    "Full Stack Developer": {
        "skills": [
            "HTML", "CSS", "JavaScript", "React",
            "Node.js", "Python", "SQL", "REST API",
            "MongoDB", "Git"
        ],
        "projects": [
            "full stack web application",
            "e-commerce platform",
            "online booking system",
            "full stack dashboard"
        ],
        "previous_roles": [
            "Web Developer", "Frontend Developer",
            "Backend Developer", "Full Stack Intern"
        ],
        "industries": ["Software", "Technology", "SaaS"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Computer Science",
            "MCA",
            "B.Sc Computer Science"
        ],
        "certifications": [
            "Meta Full Stack Developer",
            "AWS Certified Developer",
            "Microsoft Azure Developer"
        ],
    },

    "Python Developer": {
        "skills": [
            "Python", "Django", "Flask", "FastAPI",
            "REST API", "SQL", "PostgreSQL",
            "Git", "Pandas", "Testing"
        ],
        "projects": [
            "Python web application",
            "FastAPI service",
            "Django management system",
            "Python automation platform"
        ],
        "previous_roles": [
            "Python Intern", "Backend Developer",
            "Software Developer"
        ],
        "industries": ["Software", "Technology", "Automation"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Computer Science",
            "MCA",
            "B.Sc Computer Science"
        ],
        "certifications": [
            "Python Institute Certification",
            "AWS Certified Developer",
            "Microsoft Python Certification"
        ],
    },

    "Cloud Engineer": {
        "skills": [
            "AWS", "Azure", "Google Cloud", "Docker",
            "Kubernetes", "Linux", "Terraform",
            "Cloud Computing", "Networking", "CI/CD"
        ],
        "projects": [
            "cloud infrastructure deployment",
            "AWS cloud migration",
            "containerized cloud application",
            "cloud monitoring platform"
        ],
        "previous_roles": [
            "Cloud Intern", "System Administrator",
            "DevOps Engineer", "Cloud Support Engineer"
        ],
        "industries": ["Cloud", "Technology", "IT Services"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Information Technology",
            "B.Tech Cloud Computing",
            "M.Tech Cloud Computing"
        ],
        "certifications": [
            "AWS Solutions Architect",
            "Microsoft Azure Administrator",
            "Google Cloud Engineer"
        ],
    },

    "DevOps Engineer": {
        "skills": [
            "Linux", "Docker", "Kubernetes", "Jenkins",
            "GitHub Actions", "AWS", "Terraform",
            "CI/CD", "Ansible", "Monitoring"
        ],
        "projects": [
            "CI/CD pipeline",
            "Kubernetes deployment",
            "cloud automation platform",
            "DevOps monitoring system"
        ],
        "previous_roles": [
            "DevOps Intern", "System Administrator",
            "Cloud Engineer", "Release Engineer"
        ],
        "industries": ["Cloud", "Software", "IT Services"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Information Technology",
            "B.Tech Cloud Computing",
            "M.Tech Cloud Computing"
        ],
        "certifications": [
            "AWS DevOps Engineer",
            "Certified Kubernetes Administrator",
            "Azure DevOps Engineer"
        ],
    },

    "Cybersecurity Analyst": {
        "skills": [
            "Cybersecurity", "Network Security", "Python",
            "Linux", "SIEM", "Incident Response",
            "Ethical Hacking", "Threat Detection",
            "Vulnerability Assessment", "Firewalls"
        ],
        "projects": [
            "network intrusion detection system",
            "security monitoring platform",
            "vulnerability assessment project",
            "threat detection system"
        ],
        "previous_roles": [
            "Security Intern", "SOC Analyst",
            "Network Administrator", "Security Analyst"
        ],
        "industries": ["Cybersecurity", "Technology", "Banking"],
        "education": [
            "B.Tech Cybersecurity",
            "B.Tech Computer Science",
            "B.Sc Cybersecurity",
            "M.Tech Cybersecurity"
        ],
        "certifications": [
            "CompTIA Security+",
            "Certified Ethical Hacker",
            "Cisco CyberOps"
        ],
    },

    "NLP Engineer": {
        "skills": [
            "Python", "NLP", "Natural Language Processing",
            "Transformers", "BERT", "PyTorch",
            "TensorFlow", "Text Classification",
            "NLTK", "Hugging Face"
        ],
        "projects": [
            "sentiment analysis system",
            "text classification application",
            "chatbot using NLP",
            "document analysis system"
        ],
        "previous_roles": [
            "NLP Intern", "AI Intern",
            "ML Engineer", "Data Scientist"
        ],
        "industries": ["Artificial Intelligence", "Technology", "Research"],
        "education": [
            "B.Tech Computer Science",
            "M.Tech Artificial Intelligence",
            "M.Sc Data Science",
            "M.Tech NLP"
        ],
        "certifications": [
            "Hugging Face NLP Certification",
            "TensorFlow Developer",
            "AWS Machine Learning"
        ],
    },

    "Computer Vision Engineer": {
        "skills": [
            "Python", "Computer Vision", "OpenCV",
            "PyTorch", "TensorFlow", "CNN",
            "Image Processing", "Deep Learning",
            "YOLO", "Object Detection"
        ],
        "projects": [
            "object detection system",
            "facial recognition system",
            "medical image classification",
            "real time computer vision application"
        ],
        "previous_roles": [
            "Computer Vision Intern", "AI Intern",
            "ML Engineer", "Research Assistant"
        ],
        "industries": ["Artificial Intelligence", "Healthcare", "Technology"],
        "education": [
            "B.Tech Computer Science",
            "M.Tech Artificial Intelligence",
            "M.Tech Computer Vision",
            "M.Sc Computer Science"
        ],
        "certifications": [
            "TensorFlow Developer",
            "NVIDIA Deep Learning",
            "AWS Machine Learning"
        ],
    },

    "MLOps Engineer": {
        "skills": [
            "Python", "Machine Learning", "Docker",
            "Kubernetes", "MLflow", "AWS",
            "CI/CD", "Model Deployment",
            "Git", "Monitoring"
        ],
        "projects": [
            "ML model deployment pipeline",
            "MLOps automation platform",
            "model monitoring system",
            "machine learning CI/CD pipeline"
        ],
        "previous_roles": [
            "ML Engineer", "DevOps Engineer",
            "Cloud Engineer", "ML Intern"
        ],
        "industries": ["Artificial Intelligence", "Cloud", "Technology"],
        "education": [
            "B.Tech Computer Science",
            "M.Tech Machine Learning",
            "M.Tech Artificial Intelligence",
            "B.E. Information Technology"
        ],
        "certifications": [
            "AWS Machine Learning",
            "Certified Kubernetes Administrator",
            "MLflow Certification"
        ],
    },

    "Business Intelligence Analyst": {
        "skills": [
            "SQL", "Power BI", "Tableau", "Excel",
            "Data Visualization", "Data Analysis",
            "Business Intelligence", "Statistics",
            "Reporting", "Dashboard Development"
        ],
        "projects": [
            "business intelligence dashboard",
            "sales performance dashboard",
            "financial analytics dashboard",
            "executive reporting system"
        ],
        "previous_roles": [
            "Business Analyst", "Data Analyst",
            "BI Intern", "Reporting Analyst"
        ],
        "industries": ["Business", "Finance", "Retail", "Analytics"],
        "education": [
            "B.Com",
            "B.Tech Computer Science",
            "BBA",
            "M.Sc Business Analytics"
        ],
        "certifications": [
            "Microsoft Power BI",
            "Tableau Desktop Specialist",
            "Google Data Analytics"
        ],
    },

    "Java Developer": {
        "skills": [
            "Java", "Spring Boot", "Hibernate",
            "REST API", "SQL", "MySQL",
            "Microservices", "Git", "Maven",
            "Object Oriented Programming"
        ],
        "projects": [
            "Spring Boot application",
            "Java banking application",
            "microservices platform",
            "enterprise management system"
        ],
        "previous_roles": [
            "Java Developer Intern",
            "Software Developer",
            "Backend Developer"
        ],
        "industries": ["Software", "Banking", "Enterprise Technology"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Computer Science",
            "MCA",
            "B.Sc Computer Science"
        ],
        "certifications": [
            "Oracle Java Certification",
            "Spring Professional Certification",
            "AWS Certified Developer"
        ],
    },

    "Cloud/DevOps Engineer": {
        "skills": [
            "AWS", "Azure", "Docker", "Kubernetes",
            "Linux", "Terraform", "Jenkins",
            "CI/CD", "Git", "Cloud Computing"
        ],
        "projects": [
            "cloud DevOps platform",
            "automated deployment pipeline",
            "container orchestration system",
            "cloud infrastructure automation"
        ],
        "previous_roles": [
            "Cloud Engineer", "DevOps Engineer",
            "System Administrator", "Cloud Intern"
        ],
        "industries": ["Cloud", "Technology", "IT Services"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Information Technology",
            "B.Tech Cloud Computing",
            "M.Tech Cloud Computing"
        ],
        "certifications": [
            "AWS Solutions Architect",
            "Azure Administrator",
            "Certified Kubernetes Administrator"
        ],
    },

    "QA Automation Engineer": {
        "skills": [
            "Python", "Java", "Selenium", "Cypress",
            "Playwright", "Test Automation", "API Testing",
            "Postman", "JUnit", "Git"
        ],
        "projects": [
            "automated web testing framework",
            "API testing automation",
            "end to end testing system",
            "continuous testing pipeline"
        ],
        "previous_roles": [
            "QA Intern", "Test Engineer",
            "Software Tester", "Automation Tester"
        ],
        "industries": ["Software", "IT Services", "Technology"],
        "education": [
            "B.Tech Computer Science",
            "B.E. Computer Science",
            "B.E. Information Technology",
            "MCA"
        ],
        "certifications": [
            "ISTQB Foundation",
            "Selenium Certification",
            "Postman API Certification"
        ],
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def choose_education(role_data):
    return random.choice(role_data["education"])


def choose_certification(role_data, strong=True):
    if random.random() < 0.30:
        return "None"

    if strong:
        return random.choice(role_data["certifications"])

    # Weak candidates may still have certifications.
    return random.choice(role_data["certifications"])


def create_job_description(role, role_data, required_skills, required_exp):
    skills_text = ", ".join(required_skills)

    project_area = random.choice(role_data["projects"])

    return (
        f"We are hiring a {role} to work on {project_area}. "
        f"The candidate should have experience with {skills_text}. "
        f"The role requires approximately {required_exp} years of experience. "
        f"The candidate will contribute to software development, "
        f"problem solving, testing, documentation, and production delivery. "
        f"Experience with modern development practices and collaborative "
        f"engineering workflows is preferred."
    )


def create_resume_text(
    role,
    role_data,
    candidate_skills,
    experience,
    previous_role,
    project,
    education,
    certification,
):
    skills_text = ", ".join(candidate_skills)

    certification_text = (
        "No professional certification listed."
        if certification == "None"
        else f"Certification: {certification}."
    )

    return (
        f"Candidate profile for a {role}. "
        f"Education: {education}. "
        f"Has {experience} years of professional experience. "
        f"Previous role: {previous_role}. "
        f"Technical skills include {skills_text}. "
        f"Completed a project involving {project}. "
        f"{certification_text} "
        f"Experienced in software development, problem solving, "
        f"team collaboration, documentation, and project delivery."
    )


def calculate_compatibility(
    candidate_skills,
    required_skills,
    experience,
    required_experience,
):
    candidate_set = set(candidate_skills)
    required_set = set(required_skills)

    skill_score = len(candidate_set & required_set) / len(required_set)

    if required_experience == 0:
        experience_score = 1.0
    else:
        experience_score = min(experience / required_experience, 1.0)

    # Small project-independent score.
    base_score = (
        0.70 * skill_score
        + 0.30 * experience_score
    )

    return base_score


# ============================================================
# GENERATION
# ============================================================

def generate_dataset():
    rows = []

    candidate_number = 1

    role_names = list(ROLES.keys())

    for role in role_names:

        role_data = ROLES[role]

        # ----------------------------------------------------
        # STRONG MATCHES
        # ----------------------------------------------------

        for _ in range(STRONG_PER_ROLE):

            required_skill_count = random.randint(4, 6)

            required_skills = random.sample(
                role_data["skills"],
                required_skill_count,
            )

            # Strong candidates get most required skills.
            candidate_skill_count = random.randint(6, 9)

            candidate_skills = random.sample(
                role_data["skills"],
                min(candidate_skill_count, len(role_data["skills"])),
            )

            # Guarantee strong skill overlap.
            missing_required = [
                skill
                for skill in required_skills
                if skill not in candidate_skills
            ]

            for skill in missing_required:
                replace_index = random.randrange(len(candidate_skills))
                candidate_skills[replace_index] = skill

            candidate_skills = list(dict.fromkeys(candidate_skills))

            experience = random.randint(1, 10)

            # Mostly reasonable experience requirements.
            required_experience = random.randint(
                max(0, experience - 2),
                min(10, experience + 1),
            )

            education = choose_education(role_data)
            previous_role = random.choice(role_data["previous_roles"])
            project = random.choice(role_data["projects"])
            certification = choose_certification(role_data, strong=True)

            resume_text = create_resume_text(
                role,
                role_data,
                candidate_skills,
                experience,
                previous_role,
                project,
                education,
                certification,
            )

            job_description = create_job_description(
                role,
                role_data,
                required_skills,
                required_experience,
            )

            rows.append({
                "resume_id": f"FH{candidate_number:05d}",
                "candidate_name": f"Candidate {candidate_number:04d}",
                "job_role": role,
                "education": education,
                "experience_years": experience,
                "skills": ", ".join(candidate_skills),
                "certifications": certification,
                "projects": project,
                "previous_role": previous_role,
                "industry": random.choice(role_data["industries"]),
                "resume_text": resume_text,
                "job_description": job_description,
                "label": "Strong Match",
            })

            candidate_number += 1

        # ----------------------------------------------------
        # WEAK MATCHES
        # ----------------------------------------------------

        for _ in range(WEAK_PER_ROLE):

            required_skill_count = random.randint(4, 6)

            required_skills = random.sample(
                role_data["skills"],
                required_skill_count,
            )

            # Weak candidates receive only a small portion
            # of the required skills.
            overlap_count = random.randint(0, 2)

            overlap_skills = random.sample(
                required_skills,
                min(overlap_count, len(required_skills)),
            )

            other_skills = [
                skill
                for skill in role_data["skills"]
                if skill not in overlap_skills
            ]

            candidate_skill_count = random.randint(4, 7)

            candidate_skills = overlap_skills + random.sample(
                other_skills,
                min(
                    candidate_skill_count - len(overlap_skills),
                    len(other_skills),
                ),
            )

            candidate_skills = list(dict.fromkeys(candidate_skills))

            # Experience can occasionally be high, creating
            # non-trivial examples where skills are the weakness.
            experience = random.randint(0, 10)

            required_experience = random.randint(
                min(10, experience + 1),
                12,
            )

            education = choose_education(role_data)
            previous_role = random.choice(role_data["previous_roles"])
            project = random.choice(role_data["projects"])
            certification = choose_certification(role_data, strong=False)

            resume_text = create_resume_text(
                role,
                role_data,
                candidate_skills,
                experience,
                previous_role,
                project,
                education,
                certification,
            )

            job_description = create_job_description(
                role,
                role_data,
                required_skills,
                required_experience,
            )

            rows.append({
                "resume_id": f"FH{candidate_number:05d}",
                "candidate_name": f"Candidate {candidate_number:04d}",
                "job_role": role,
                "education": education,
                "experience_years": experience,
                "skills": ", ".join(candidate_skills),
                "certifications": certification,
                "projects": project,
                "previous_role": previous_role,
                "industry": random.choice(role_data["industries"]),
                "resume_text": resume_text,
                "job_description": job_description,
                "label": "Weak Match",
            })

            candidate_number += 1

    df = pd.DataFrame(rows)

    expected_columns = [
        "resume_id",
        "candidate_name",
        "job_role",
        "education",
        "experience_years",
        "skills",
        "certifications",
        "projects",
        "previous_role",
        "industry",
        "resume_text",
        "job_description",
        "label",
    ]

    df = df[expected_columns]

    # Shuffle rows so labels are not grouped by role.
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    # ========================================================
    # VALIDATION
    # ========================================================

    assert len(df) == TOTAL_ROWS
    assert len(df.columns) == 13
    assert list(df.columns) == expected_columns

    assert df["resume_id"].is_unique
    assert df["candidate_name"].is_unique

    assert df["label"].value_counts()["Strong Match"] == 1500
    assert df["label"].value_counts()["Weak Match"] == 1500

    assert df["job_role"].nunique() == 20

    role_counts = df["job_role"].value_counts()

    for role_name in role_names:
        assert role_counts[role_name] == ROWS_PER_ROLE

    assert df["experience_years"].between(0, 12).all()

    assert not df["resume_text"].fillna("").str.strip().eq("").any()
    assert not df["job_description"].fillna("").str.strip().eq("").any()

    # Make sure the generated text doesn't directly expose labels.
    combined_text = (
        df["resume_text"].str.lower()
        + " "
        + df["job_description"].str.lower()
    )

    forbidden_phrases = [
    "strong match",
    "weak match",
    "match score",
    "candidate score",
    "suitability score",
    "predicted label",
]

    for phrase in forbidden_phrases:
        assert not combined_text.str.contains(
            phrase,
            regex=False,
        ).any(), f"Leakage phrase found: {phrase}"

    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("=" * 60)
    print("FairHire AI Dataset V2 Generated Successfully")
    print("=" * 60)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Output: {OUTPUT_PATH}")

    print("\nLabel distribution:")
    print(df["label"].value_counts())

    print("\nJob role distribution:")
    print(df["job_role"].value_counts().sort_index())

    print("\nExperience statistics:")
    print(df["experience_years"].describe())

    print("\nColumn order:")
    print(list(df.columns))

    print("\nValidation: PASS")
    print("=" * 60)


if __name__ == "__main__":
    generate_dataset()