# CareerLens AI

**Understand Your Resume. Discover Your Potential.**

An AI-powered career intelligence platform that parses resumes, extracts
and normalizes skills, and matches candidates to roles using transformer
sentence embeddings combined with a configurable, explainable hybrid
scoring engine — not keyword matching.

> **Status note:** this repository was built in an offline development
> sandbox with no internet access. Everything that doesn't require
> external packages or model downloads — resume parsing, skill
> normalization, hybrid scoring math, ATS analysis, the FastAPI service
> layer, and the anonymous-demo-vs-signed-in-save logic — is written,
> tested, and confirmed passing in that sandbox (`ml/tests/`,
> `backend/tests/`). The `sentence-transformers` embedding code, the full
> Supabase auth flow (sign-up/sign-in/reset), and `npm install`/`next build`
> are real, complete, production-ready code that has **not been executed**
> in this environment, since it needs internet access this sandbox doesn't
> have. Run through **Local Setup** below in an environment with internet
> access before deploying — that's the first real end-to-end run.

---

## Problem Statement

Resume screening is largely keyword matching today: ATS systems and
recruiters scan for exact term overlap, which misses candidates whose
resumes describe equivalent skills in different words ("built ML models
in production" vs. "MLOps experience"), and gives candidates no
actionable feedback on *why* they weren't matched.

## Solution

CareerLens AI reads resumes and job descriptions the way a person would —
using sentence embeddings to compare meaning, not just words — while
still surfacing the concrete, explainable signals (skill overlap,
experience, education) that make a match score trustworthy and
actionable rather than a black box.

## Features

- Resume parsing (PDF/DOCX) into structured fields — contact info,
  education, experience, projects, skills, certifications, achievements
- Skill normalization ("React.js"/"ReactJS"/"react-js" → "React") via a
  reusable taxonomy
- ATS-style resume analysis with a component breakdown (explicitly *not*
  claimed to be a real commercial ATS score)
- Job description analyzer — extracts required/preferred skills,
  experience, and education requirements from pasted text
- Hybrid candidate-job matching: semantic similarity (35%) + technical
  skills (25%) + experience (15%) + education (10%) + role compatibility
  (10%) + resume quality (5%), fully configurable
- Skill-gap analysis with priority tiers and plain-language reasons
- Career role recommendations ranked by compatibility
- Explainable AI — every score ships with human-readable strengths/gaps
- Resume improvement suggestions that never fabricate content — only
  flags what's missing or could be strengthened
- Career dashboard, job explorer (clearly-labeled sample data), analysis
  history, and per-user data deletion

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full diagram
and request-flow breakdown. Summary:

```
Next.js (Vercel)  →  FastAPI (Railway/Render/HF Spaces)  →  ml/ pipeline + Supabase (Postgres + Auth)
```

## AI/ML Methodology

### Transformer model

`sentence-transformers/all-MiniLM-L6-v2` — chosen over `all-mpnet-base-v2`
for its much smaller memory/latency footprint on CPU-only deployment
targets, at a small accuracy cost on short-text similarity benchmarks.
See the docstring in [`ml/embeddings/embedder.py`](ml/embeddings/embedder.py)
for the full reasoning and the one-line swap point if you want to upgrade.

### Semantic matching

Resume text and job description text are embedded independently and
compared with cosine similarity — this is *one input* to the final score,
never the whole score.

### Hybrid scoring

See [`ml/matching/hybrid_matcher.py`](ml/matching/hybrid_matcher.py).
Weights are a plain dict (`DEFAULT_WEIGHTS`), overridable per call,
enforced to sum to 1.0.

### Explainability

`explain_match()` in the same file converts the numeric breakdown into
plain-language strengths/gaps — this is a rules-based explanation over an
inherently interpretable hybrid score, not a post-hoc technique like SHAP
bolted onto a black-box model (which would be the wrong tool here: the
score is already a weighted sum of named, human-readable components).

## Dataset

See [`docs/DATASET.md`](docs/DATASET.md). No proprietary training data —
uses a pretrained embedding model; sample job postings are original,
synthetic, and clearly labeled as demo data everywhere they appear.

## Evaluation

See [`docs/EVALUATION.md`](docs/EVALUATION.md). Metric implementations
(P/R/F1, P@K, MRR, NDCG) are in `ml/evaluation/metrics.py`; no numbers are
claimed here until run against real labeled data.

## Tech Stack

**Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, Framer Motion, Recharts, lucide-react
**Backend:** Python, FastAPI, Pydantic, Uvicorn
**AI/ML:** sentence-transformers, PyTorch, scikit-learn, pdfplumber, python-docx
**Database/Auth:** Supabase (Postgres + Row Level Security + Auth)
**Deployment:** Vercel (frontend), Railway/Render/HF Spaces (backend), Supabase (data)

## Project Structure

```
careerlens-ai/
├── frontend/          Next.js app (App Router)
├── backend/           FastAPI app
│   └── app/
│       ├── api/       HTTP route handlers
│       ├── services/  orchestration layer (thin, wraps ml/)
│       └── schemas/   Pydantic request/response models
├── ml/                framework-agnostic AI/NLP pipeline (importable standalone)
│   ├── preprocessing/ text cleaning
│   ├── extraction/    resume parsing, section detection, skill extraction/taxonomy
│   ├── embeddings/    sentence-transformer wrapper
│   ├── matching/      hybrid scoring, ATS analyzer
│   ├── recommendation/ role recommender, skill gap
│   ├── evaluation/    P/R/F1, P@K, MRR, NDCG
│   └── tests/
├── supabase/
│   └── schema.sql     Postgres schema + Row Level Security policies
├── docs/               architecture, evaluation methodology, dataset notes
└── notebooks/
```

## Local Setup

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Supabase credentials
uvicorn app.main:app --reload --port 8000
```
API docs at `http://localhost:8000/docs`.

Run tests:
```bash
PYTHONPATH=..:. pytest tests/ ../ml/tests/
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local   # fill in Supabase + NEXT_PUBLIC_API_URL
npm run dev
```
App at `http://localhost:3000`.

### Database
Create a Supabase project, then run `supabase/schema.sql` in the SQL editor
(or `supabase db push` with the CLI). Enable email auth under
Authentication → Providers. Then create the private Storage bucket used
for uploaded resume files:
```bash
cd backend
export SUPABASE_URL=...  SUPABASE_SERVICE_ROLE_KEY=...
python scripts/setup_storage_bucket.py
```

## Testing

```bash
# ml/ + backend service-layer tests (no fastapi/torch required)
PYTHONPATH=backend:. pytest backend/tests/test_services.py ml/tests/ -v

# HTTP-level backend tests (requires fastapi + httpx from requirements.txt)
cd backend && PYTHONPATH=..:. pytest tests/test_api.py -v

# frontend unit tests (requires npm install)
cd frontend && npm test
```

## Environment Variables

See `frontend/.env.example` and `backend/.env.example`. Never commit `.env`.

## API Documentation

Auto-generated OpenAPI docs are served at `/docs` once the backend is
running. Key endpoints:

```
POST   /api/resume/upload
POST   /api/resume/analyze/{resume_id}
DELETE /api/resume/{resume_id}
GET    /api/jobs
GET    /api/jobs/{id}
POST   /api/jobs/analyze
POST   /api/match
GET    /api/career-insights
GET    /api/skill-gap
GET    /api/history
GET    /health
```

## Deployment

1. **Database**: create the Supabase project, run `supabase/schema.sql`,
   enable Email auth under Authentication → Providers.
2. **Backend**: this repo ships a ready-to-use `backend/Dockerfile` plus
   `railway.json` and `render.yaml` at the repo root.
   - **Railway**: New Project → Deploy from GitHub repo → it auto-detects
     `railway.json` and builds `backend/Dockerfile` with the repo root as
     build context. Add the env vars from `backend/.env.example` in the
     Railway dashboard (Variables tab), plus `CORS_ORIGINS` set to your
     deployed frontend's URL once you have it.
   - **Render**: New → Blueprint → point at this repo; it reads
     `render.yaml` automatically. Fill in the `sync: false` env vars
     (Supabase keys, CORS_ORIGINS) in the Render dashboard.
   - Either way, confirm `GET /health` returns `{"status": "ok"}` once deployed.
3. **Frontend**: deploy `frontend/` to Vercel — New Project → Import this
   GitHub repo → set **Root Directory to `frontend`** (important, since
   this is a monorepo) → add `NEXT_PUBLIC_SUPABASE_URL`,
   `NEXT_PUBLIC_SUPABASE_ANON_KEY`, and `NEXT_PUBLIC_API_URL` (your
   deployed backend's URL) as environment variables → Deploy.
4. **Wire CORS both ways**: once the frontend has a real Vercel URL,
   update `CORS_ORIGINS` on the backend to match it and redeploy the backend.
5. **Supabase auth redirect URLs**: in Supabase → Authentication → URL
   Configuration, add your deployed frontend's `/auth/callback` URL
   (e.g. `https://your-app.vercel.app/auth/callback`) to the allowed
   redirect list, or sign-up/reset-password emails will link back to
   `localhost`.

## Pushing to GitHub

```bash
cd careerlens-ai
git init
git add .
git commit -m "Initial commit: CareerLens AI"
git branch -M main
git remote add origin https://github.com/<your-username>/careerlens-ai.git
git push -u origin main
```
`.gitignore` already excludes `.env`, `node_modules/`, `.next/`,
`__pycache__/`, and model weights — nothing secret should end up in the repo.
The included `.github/workflows/ci.yml` will automatically run the `ml/`
and backend test suites, plus a frontend typecheck/lint/build, on every
push once the repo is on GitHub.

## Screenshots

_Add screenshots here once the app is running against a live backend —
intentionally left out rather than faked._

## Limitations

- No live job-board integration — `job-matcher` uses a small, clearly
  labeled sample catalog (spec-compliant: never presented as real
  vacancies).
- Experience-duration parsing from resume text uses a heuristic (count of
  detected experience entries), not full date-range parsing — a real
  date parser would improve `candidate_years_experience` accuracy.
- No evaluation numbers are published yet (see `docs/EVALUATION.md` for
  why, and how to produce real ones).
- The `db_client.py` in-memory fallback is dev-only — not multi-instance
  safe, not persistent across restarts. It only activates when
  `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` aren't set; a real deployment
  with those configured always uses Postgres + Supabase Storage.
- `/resume-analyzer`, `/job-matcher`, and `/job-analyzer` work without an
  account (so the landing page's "Try Demo" never hits a login wall);
  anonymous resume uploads run the real pipeline but aren't persisted
  (`saved: false` in the response). `/dashboard`, `/career-insights`,
  `/compare`, `/history`, and `/settings` require a signed-in Supabase
  session, enforced client-side by `RequireAuth` and server-side by Row
  Level Security + the `get_current_user` FastAPI dependency.
- Job search (`/api/jobs?q=...`) uses true semantic ranking when the
  embedding model is loadable, and falls back to skill/keyword ranking
  otherwise (see `app/services/job_service.py::search_jobs`) — neither
  path has been run end-to-end yet since neither `npm install` nor
  `pip install` of the heavy deps has executed anywhere (no internet in
  the build sandbox — see the Status note at the top of this README).
- `backend/tests/test_api.py` (HTTP-level, via FastAPI's TestClient) and
  `frontend/**/__tests__/*.test.tsx` (Vitest + React Testing Library) are
  written and syntax-checked but not executed for the same reason.

## Known-fixed bugs (worth knowing about even though they're fixed)

- **Resume re-analysis was silently broken**: the dev-mode file store used
  to hardcode `file_bytes: None`, so `POST /api/resume/analyze/{id}` would
  crash. Fixed in `db_client.py` (now stores real bytes in-memory, and
  uploads/downloads them from a private Supabase Storage bucket in
  production — see `backend/scripts/setup_storage_bucket.py`). Covered by
  `test_reanalyze_resume_actually_works` in `backend/tests/test_services.py`.
- **`MAX_UPLOAD_SIZE_MB` was dead config** — the real limit was hardcoded
  in `ml/extraction/resume_parser.py` and never read the env var. Fixed:
  the limit is now a parameter threaded through from `app.config.settings`.

## Future Improvements

- Real date-range parsing for experience duration
- A larger, curated skill taxonomy (currently a hand-maintained dict)
- Fine-tuning or a cross-encoder re-ranker on top of the bi-encoder for
  higher-precision top-K matching
- A real evaluation run against a labeled dataset, with results published
  in `docs/EVALUATION.md`
- Live job-board integration behind a clearly labeled "live data" toggle

## Author

Built as a placement/portfolio project demonstrating deep learning, NLP,
full-stack engineering, and production-oriented software architecture.

## License

MIT — see [`LICENSE`](LICENSE).
