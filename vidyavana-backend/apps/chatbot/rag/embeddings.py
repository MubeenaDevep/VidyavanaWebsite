"""Lazy multilingual embedding model shared by indexing and retrieval."""

import threading

_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model = None
_model_lock = threading.Lock()


def _get_model():
    global _model
    if _model is not None:
        return _model
    with _model_lock:
        if _model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    "RAG dependencies are missing. Install requirements.txt."
                ) from exc
            _model = SentenceTransformer(_MODEL_NAME)
    return _model


def encode(texts: list[str]):
    return _get_model().encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
