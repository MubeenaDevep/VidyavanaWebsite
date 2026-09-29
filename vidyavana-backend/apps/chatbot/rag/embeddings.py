"""Shared multilingual embedding model for indexing and retrieval."""

import logging
import threading

_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model = None
_model_lock = threading.Lock()
_preload_lock = threading.Lock()
_preload_started = False

logger = logging.getLogger("vidyavana")


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


def preload_model():
    """Warm the cached model during startup with a safe lazy fallback."""

    global _preload_started

    with _preload_lock:
        if _preload_started:
            return
        _preload_started = True

    try:
        _get_model()
        logger.info("RAG embedding model preloaded: %s", _MODEL_NAME)
    except Exception:
        logger.exception(
            "RAG embedding model preload failed; lazy loading remains available"
        )


def encode(texts: list[str]):
    return _get_model().encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
