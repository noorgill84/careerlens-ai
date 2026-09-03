# Model weights are never committed to this repo.

`sentence-transformers` downloads and caches `all-MiniLM-L6-v2` automatically
on first use (see ml/embeddings/embedder.py) into the Hugging Face cache
directory (`~/.cache/huggingface` by default). If your deployment target
has no internet access at runtime, pre-download the model in your build
step instead:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

Then bundle the resulting cache directory into your deployment image.
