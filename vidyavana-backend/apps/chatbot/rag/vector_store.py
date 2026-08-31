"""Persistent FAISS index and chunk metadata storage."""

import json
from pathlib import Path

import numpy as np
from django.conf import settings

from .documents import load_documents
from .embeddings import encode


def index_directory() -> Path:
    return Path(settings.BASE_DIR) / "data" / "rag"


def build_index() -> int:
    try:
        import faiss
    except ImportError as exc:
        raise RuntimeError(
            "FAISS is missing. Install requirements.txt."
        ) from exc

    documents = load_documents()
    if not documents:
        raise RuntimeError("No knowledge documents found.")

    vectors = np.asarray(encode([item["text"] for item in documents]), dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    directory = index_directory()
    directory.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(directory / "knowledge.faiss"))
    (directory / "metadata.json").write_text(
        json.dumps(documents, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(documents)


def load_index():
    try:
        import faiss
    except ImportError as exc:
        raise RuntimeError(
            "FAISS is missing. Install requirements.txt."
        ) from exc

    directory = index_directory()
    index_path = directory / "knowledge.faiss"
    metadata_path = directory / "metadata.json"
    if not index_path.exists() or not metadata_path.exists():
        return None, []
    return faiss.read_index(str(index_path)), json.loads(
        metadata_path.read_text(encoding="utf-8")
    )
