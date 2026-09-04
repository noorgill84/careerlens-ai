# CareerLens AI backend — portable container for Railway/Render/Fly/HF Spaces.
#
# IMPORTANT: build context must be the REPO ROOT (not backend/), since this
# image also needs the framework-agnostic ml/ package that lives alongside
# backend/ in the monorepo. Build with:
#   docker build -f backend/Dockerfile -t careerlens-backend .
# Railway/Render: set "Root Directory" to the repo root and the Dockerfile
# path to backend/Dockerfile (both platforms support this explicitly).

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model at build time so cold starts don't pay
# the download cost, and the container works even if the runtime host has
# restricted outbound network access (spec §44 — cache models, don't
# reload/re-download per request).
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY backend/ ./backend/
COPY ml/ ./ml/

ENV PYTHONPATH=/app
WORKDIR /app/backend
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
