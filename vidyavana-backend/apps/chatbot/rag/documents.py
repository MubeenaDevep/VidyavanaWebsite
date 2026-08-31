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
        heading = lines[0].strip() if lines[0].endswith(":") else ""
        content = " ".join(line.strip() for line in lines if line.strip())
        if heading:
            content = content[len(heading):].strip()
        if content:
            chunks.append({
                "text": content,
                "source": document_name,
                "section": heading.rstrip(":") or None,
            })
    return chunks
