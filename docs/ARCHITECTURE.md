# Architecture

```
                            CareerLens AI

                                 USER
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   Next.js Frontend         │
                    │   (Vercel)                 │
                    │   TypeScript / Tailwind    │
                    └─────────────┬──────────────┘
                                  │ HTTPS (NEXT_PUBLIC_API_URL)
                                  ▼
                    ┌───────────────────────────┐
                    │   FastAPI Backend          │
                    │   (Railway / Render / HF   │
                    │    Spaces — Python-capable)│
                    └─────────────┬──────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
   ┌─────────────────┐ ┌───────────────────┐ ┌──────────────────┐
   │ ml/ pipeline     │ │ Supabase Postgres  │ │ Supabase Auth     │
   │ - parsing        │ │ - resumes          │ │ - JWT issuance    │
   │ - normalization  │ │ - jobs             │ │ - session mgmt    │
   │ - embeddings     │ │ - matches          │ │                    │
   │ - hybrid scoring │ │ - history          │ │                    │
   └─────────────────┘ └───────────────────┘ └──────────────────┘
```

## Why this split

- **Frontend on Vercel, backend elsewhere**: Vercel's serverless functions
  are a poor fit for a ~90MB PyTorch model that needs to stay warm in
  memory between requests (spec §38/§44 — don't reload the model per
  request). A long-running Python process on Railway/Render/HF Spaces
  keeps the model loaded via the `lru_cache` singleton in
  `ml/embeddings/embedder.py`.
- **`ml/` is framework-agnostic**: nothing in `ml/` imports FastAPI,
  Pydantic, or Supabase. `backend/app/services/*` are thin adapters that
  call into `ml/` and handle HTTP/DB concerns. This is what makes the ML
  code independently unit-testable (see `ml/tests/`) and reusable from a
  notebook or a batch evaluation script without spinning up a server.
- **Supabase for both auth and Postgres**: avoids hand-rolling password
  storage (explicitly disallowed by spec §26) and gives Row Level Security
  for free, so `user_id` scoping is enforced at the database layer, not
  just in application code.

## Request flow: resume upload

```
Browser --(multipart file)--> POST /api/resume/upload
    -> app/api/resume.py           (HTTP layer, auth check)
    -> app/services/resume_service.py   (orchestration)
        -> ml/extraction/resume_parser.py   (bytes -> ResumeProfile)
        -> ml/extraction/skill_taxonomy.py  (normalize skills)
        -> ml/matching/ats_analyzer.py      (ATS-style score)
        -> app/services/improvement_engine.py (grounded suggestions)
    -> app/services/db_client.py    (persist to Supabase, or in-memory in dev)
<- ResumeAnalysisResponse (JSON)
```

## Request flow: resume-to-job matching

```
Browser --(resume_id, job_id)--> POST /api/match
    -> app/api/matching.py
    -> app/services/matching_service.py
        -> ml/embeddings/embedder.py         (semantic_similarity, 0-1)
        -> ml/matching/hybrid_matcher.py     (weighted combination -> 0-100)
<- MatchResponse (breakdown + explanations)
```
