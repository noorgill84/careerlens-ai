"""
Transformer embedding service.

Model choice: `sentence-transformers/all-MiniLM-L6-v2`
  - 384-dim embeddings, ~80MB, ~14k sentences/sec on CPU.
  - Chosen over all-mpnet-base-v2 (768-dim, ~420MB, ~4x slower) because
    resume/job text is short-to-medium length (not long-document retrieval),
    and this app needs to run comfortably on a free/low-tier CPU deployment
    (Railway/Render/HF Spaces) without a GPU. MiniLM's accuracy loss vs
    mpnet on short-text semantic similarity (STS) benchmarks is small
    (~1-2 points) relative to the latency/memory savings, which matters
    more for a live per-request API than for offline batch scoring.
  - Swap point: change MODEL_NAME below to upgrade quality later; nothing
    else in the codebase needs to change since callers only see vectors.

NOTE ON THIS SANDBOX: this module requires `sentence-transformers` + `torch`,
which are not installed in this offline dev sandbox (no network to fetch
them or the model weights). The code below is the real production
implementation. Run `pip install -r backend/requirements.txt` in an
environment with internet access to actually execute it — see
ml/tests/test_embedder.py for how to smoke-test it once installed.
"""
from __future__ import annotations
import functools
import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


@functools.lru_cache(maxsize=1)
def _get_model():
    """
    Lazily load and cache the model as a process-wide singleton.
    lru_cache(maxsize=1) ensures the (relatively expensive, ~1-2s) model
    load happens once per process, not once per request (spec §44).
    """
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> np.ndarray:
    """Embed a single string -> (EMBEDDING_DIM,) float32 vector, L2-normalized."""
    return embed_texts([text])[0]


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Batch-embed strings -> (N, EMBEDDING_DIM) float32 matrix, L2-normalized
    so that dot product == cosine similarity downstream.
    """
    if not texts:
        return np.zeros((0, EMBEDDING_DIM), dtype=np.float32)
    model = _get_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embeddings.astype(np.float32)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Cosine similarity between two (already L2-normalized) vectors, as 0-1."""
    raw = float(np.dot(vec_a, vec_b))
    # embeddings are normalized so raw is already in [-1, 1]; clamp for safety
    # and rescale to [0, 1] since a 0-1 "match" score reads better than
    # a signed cosine value in the product UI.
    raw = max(-1.0, min(1.0, raw))
    return (raw + 1.0) / 2.0
