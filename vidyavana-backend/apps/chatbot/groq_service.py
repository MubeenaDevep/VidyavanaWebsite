import logging
import os

from django.conf import settings
from groq import Groq

logger = logging.getLogger("vidyavana")


def _get_groq_client():
    api_key = getattr(settings, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")
    return Groq(api_key=api_key)


def _normalise_text(response_content):
    if response_content is None:
        return ""
    if isinstance(response_content, str):
        return response_content.strip()
    if isinstance(response_content, list):
        chunks = []
        for item in response_content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if text:
                    chunks.append(str(text))
            elif isinstance(item, str):
                chunks.append(item)
        return " ".join(chunks).strip()
    return str(response_content).strip()


def generate_chat_completion(
    system_prompt: str,
    history: list | None = None,
    user_message: str = "",
    rag_context: str = "",
):
    history = history or []
    client = _get_groq_client()
    model = getattr(settings, "GROQ_MODEL", None) or os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b"

    messages = [{"role": "system", "content": system_prompt}]
    if rag_context:
        messages.append({"role": "system", "content": f"Verified context:\n{rag_context}"})

    for item in history:
        role = item.get("role", "user")
        content = item.get("content", "")
        if role and content:
            messages.append({"role": role, "content": content})

    if user_message:
        messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=800,
    )

    message = response.choices[0].message
    content = _normalise_text(getattr(message, "content", ""))
    if not content:
        raise ValueError("Groq returned an empty response.")
    return content


def transcribe_audio(audio_file, language_code: str | None = None):
    if audio_file is None:
        raise ValueError("Audio file is required.")

    client = _get_groq_client()
    model = getattr(settings, "GROQ_STT_MODEL", None) or os.getenv("GROQ_STT_MODEL") or "whisper-large-v3-turbo"

    audio_name = getattr(audio_file, "name", "audio.wav") or "audio.wav"
    file_bytes = audio_file.read() if hasattr(audio_file, "read") else audio_file

    if not file_bytes:
        raise ValueError("Audio file is empty.")

    response = client.audio.transcriptions.create(
        file=(audio_name, file_bytes),
        model=model,
        language=(language_code or "en").lower()
    )

    text = getattr(response, "text", "")
    if not text or not text.strip():
        raise ValueError("Groq transcription returned no text.")
    return text.strip()
