# Model Evaluation

This project ships evaluation code (`ml/evaluation/metrics.py`) but does
**not** ship pre-filled performance numbers, because none have been run
yet against a labeled dataset in this environment. Filling in fake numbers
would violate the project's own "no fake claims" rule (spec §49) — so
this doc is the honest alternative: exactly how to produce real ones.

## 1. Information extraction (resume parsing)

Build a small labeled set: 30-50 resumes with hand-annotated ground truth
for `email`, `phone`, `linkedin`, `github`, `education[].degree`,
`skills_raw`, etc.

```python
from ml.evaluation.metrics import precision_recall_f1
from ml.extraction.resume_parser import parse_resume

predicted_skills = {s.lower() for s in profile.skills_raw}
actual_skills = {s.lower() for s in ground_truth["skills"]}
print(precision_recall_f1(predicted_skills, actual_skills))
```

Report precision/recall/F1 per field, not just skills — extraction quality
varies a lot by field (structured fields like email are near-perfect;
free-text fields like "responsibilities" are much harder).

## 2. Ranking / matching quality

Build labeled (resume, job, relevance) triples — even a few dozen pairs
rated 0-3 by a human is enough for a first pass.

```python
from ml.evaluation.metrics import precision_at_k, mean_reciprocal_rank, ndcg_at_k

# ranked_job_ids: job IDs sorted by the hybrid matcher's score, descending
# relevant_job_ids: the set of job IDs a human rated as genuinely relevant
print(precision_at_k(ranked_job_ids, relevant_job_ids, k=5))
```

## 3. Component-level ablation

Because `compute_hybrid_match` takes each sub-score independently, you can
measure how much each component (semantic similarity vs. skill overlap vs.
experience, etc.) actually contributes to ranking quality by re-running
`ndcg_at_k` with different `weights` dicts and comparing. This is the kind
of ablation that's genuinely defensible in a placement interview — it's
real experimental evidence about *this* system, not a claimed accuracy
number copied from a paper.

## Reporting results

When you do run this against real data, put the results in a table here
with: dataset size, date run, exact weights/config used, and a link to the
script that produced them — so the numbers stay reproducible and honest.
