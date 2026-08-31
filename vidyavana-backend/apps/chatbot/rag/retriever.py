"""Retrieve a small set of relevant verified knowledge chunks."""

import logging

from .embeddings import encode
from .vector_store import load_index

logger = logging.getLogger("vidyavana")


def retrieve(question: str, top_k: int = 4, threshold: float = 0.35) -> list[dict]:
    index, metadata = load_index()
    if index is None or not metadata:
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
