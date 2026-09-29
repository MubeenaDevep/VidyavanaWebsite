"""Load and chunk verified text documents used by chatbot RAG."""

from pathlib import Path

from django.conf import settings


def knowledge_directory() -> Path:
    return Path(settings.BASE_DIR) / "knowledge"


def load_documents() -> list[dict]:
    documents = []
    for path in sorted(knowledge_directory().glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        documents.extend(_chunk_document(path.name, text))
    return documents


def _chunk_document(document_name: str, text: str) -> list[dict]:
    chunks = []
    for section in text.split("\n\n"):
        section = section.strip()
        if not section:
            continue
        lines = section.splitlines()
        heading = lines[0].strip().rstrip(":")
        has_heading = len(lines) > 1 and (
            lines[0].strip().endswith(":")
            or not lines[0].strip().endswith((".", "!", "?"))
        )
        if not has_heading:
            heading = ""
        content = " ".join(line.strip() for line in lines if line.strip())
        if heading:
            content = " ".join(lines[1:]).strip()
        if content:
            chunks.append({
                "text": content,
                "source": document_name,
                "section": heading or None,
            })
    return chunks
