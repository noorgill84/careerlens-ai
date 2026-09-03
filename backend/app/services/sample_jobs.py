"""
Sample job catalog for the Job Matcher page.

These are clearly-labeled DEMO jobs (is_sample_data=True on every record),
not live vacancies scraped from a job board — spec §14 explicitly forbids
presenting fake jobs as real ones. Swap point: replace `SAMPLE_JOBS` with
a real jobs table query once a live job-board integration exists.
"""

SAMPLE_JOBS = [
    {
        "id": "job-001", "title": "Machine Learning Engineer", "company": "Demo: NovaAI Labs",
        "location": "Bengaluru, India (Hybrid)", "is_sample_data": True,
        "required_skills": ["Python", "Machine Learning", "PyTorch", "SQL"],
        "preferred_skills": ["AWS", "Docker"],
        "experience_years_required": 1, "education_required": "bachelor",
        "description": "Build and deploy ML models for production NLP systems. Work with PyTorch, "
                        "sentence embeddings, and FastAPI services. 1+ years experience or strong project portfolio.",
    },
    {
        "id": "job-002", "title": "Data Scientist", "company": "Demo: Insight Analytics",
        "location": "Remote", "is_sample_data": True,
        "required_skills": ["Python", "SQL", "Machine Learning", "Pandas"],
        "preferred_skills": ["Scikit-learn", "Communication"],
        "experience_years_required": 0, "education_required": "bachelor",
        "description": "Entry-level data scientist role analyzing product data, building predictive models, "
                        "and communicating insights to stakeholders.",
    },
    {
        "id": "job-003", "title": "Backend Engineer", "company": "Demo: Cloudframe Systems",
        "location": "Pune, India (On-site)", "is_sample_data": True,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "preferred_skills": ["AWS", "Kubernetes"],
        "experience_years_required": 2, "education_required": "bachelor",
        "description": "Design and maintain scalable backend services powering our SaaS platform using "
                        "FastAPI and PostgreSQL, deployed via Docker.",
    },
    {
        "id": "job-004", "title": "AI Engineer (NLP)", "company": "Demo: LinguaTech",
        "location": "Remote", "is_sample_data": True,
        "required_skills": ["Python", "Natural Language Processing", "Hugging Face Transformers", "Deep Learning"],
        "preferred_skills": ["Docker", "AWS"],
        "experience_years_required": 1, "education_required": "bachelor",
        "description": "Work on transformer-based NLP systems: fine-tuning, embeddings, and semantic search, "
                        "shipped as production APIs.",
    },
    {
        "id": "job-005", "title": "Frontend Engineer", "company": "Demo: PixelForge",
        "location": "Remote", "is_sample_data": True,
        "required_skills": ["JavaScript", "TypeScript", "React", "Next.js"],
        "preferred_skills": ["Tailwind CSS"],
        "experience_years_required": 1, "education_required": "bachelor",
        "description": "Build polished, accessible UI in React/Next.js/TypeScript for a growing SaaS product.",
    },
]
