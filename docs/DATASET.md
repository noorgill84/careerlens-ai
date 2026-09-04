# Dataset

CareerLens AI does not ship a bundled training dataset — the core NLP
components (`ml/embeddings/embedder.py`) use a **pretrained** sentence
embedding model (`all-MiniLM-L6-v2`) rather than a model trained from
scratch on resume data, so no proprietary training corpus is required to
run the app.

## What data the app itself generates/uses

| Source | Nature | License / provenance |
|---|---|---|
| User-uploaded resumes | Real, user-owned, private (spec §28) | Never redistributed; stored per-user in Supabase with RLS |
| `backend/app/services/sample_jobs.py` | Synthetic, hand-written demo job postings | Original content written for this project; clearly labeled `is_sample_data: true` everywhere it's returned by the API — never presented as real vacancies |
| `all-MiniLM-L6-v2` | Pretrained sentence-transformer weights | Apache 2.0, from the `sentence-transformers` project on Hugging Face |

## If you extend this with a labeled dataset (for evaluation, per docs/EVALUATION.md)

Recommended public sources, to be documented here once actually used:
- Hugging Face Hub — search `resume`, `job description`, or `skills` datasets
- Kaggle — several public resume/job-posting datasets exist; check each one's license before redistribution
- Synthetic data you generate yourself for development — must be clearly
  labeled as synthetic in any report or README claim (spec §33), never
  presented as real-world data

## Privacy

- Real user resumes are never used to fine-tune or otherwise train any
  model in this project.
- No personal information from uploaded resumes is included in this repo,
  its documentation, or any example/demo data.
