"""Retrieve a small set of relevant verified knowledge chunks."""

import logging
import os

from django.conf import settings

from .embeddings import encode
from .vector_store import load_index

logger = logging.getLogger("vidyavana")


def _get_setting_float(name: str, default: float) -> float:
    value = getattr(settings, name, None)
    if value is None:
        value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_setting_int(name: str, default: int) -> int:
    value = getattr(settings, name, None)
    if value is None:
        value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def retrieve(question: str, top_k: int | None = None, threshold: float | None = None) -> list[dict]:
    top_k = top_k if top_k is not None else _get_setting_int("RAG_TOP_K", 4)
    threshold = threshold if threshold is not None else _get_setting_float("RAG_RELEVANCE_THRESHOLD", 0.28)

    logger.info("RAG query=%r top_k=%s threshold=%s", question, top_k, threshold)
    index, metadata = load_index()
    if index is None or not metadata:
        logger.warning("RAG index is unavailable or contains no metadata")
        return []

    scores, positions = index.search(encode([question]), min(top_k, len(metadata)))
    results = []
    for score, position in zip(scores[0], positions[0]):
        if position < 0 or float(score) < threshold:
            continue
        item = metadata[int(position)]
        results.append({
            "text": item["text"],
            "source": item["source"],
            "section": item.get("section"),
            "score": round(float(score), 4),
        })
    logger.info(
        "RAG retrieved %s/%s chunks: %s",
        len(results),
        len(metadata),
        [(item.get("section"), item["score"]) for item in results],
    )
    return results


def retrieve_context(question: str) -> str:
    try:
        results = retrieve(question)
    except Exception:
        logger.exception("RAG retrieval failed; continuing without RAG context")
        return ""
    if not results:
        return ""
    return "\n\n".join(
        f"Source: {item['source']}"
        + (f" | Section: {item['section']}" if item.get("section") else "")
        + f"\n{item['text']}"
        for item in results
    )
