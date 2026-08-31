import logging
import os
import time
import uuid

from django.conf import settings
from gtts import gTTS

logger = logging.getLogger("vidyavana")

def generate_speech(
    text: str,
    language_code: str = "EN",
    filename: str | None = None,
) -> str:
    """
    Generate speech from chatbot text using Google TTS (gTTS).
    
    Returns:
        Relative media path, for example:
        tts/abc123.mp3
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    # --------------------------------------------------------
    # Normalize language
    # --------------------------------------------------------
    language_code = language_code.upper()
    lang_map = {
        "EN": "en",
        "KN": "kn",
        "TE": "te",
    }
    gtts_lang = lang_map.get(language_code, "en")

    # --------------------------------------------------------
    # Generate filename if one wasn't supplied
    # --------------------------------------------------------
    if not filename:
        filename = f"{uuid.uuid4().hex}.mp3"
    else:
        # If the view passed a .wav extension, we should probably 
        # ensure it uses .mp3 since gTTS outputs mp3 format
        if filename.endswith(".wav"):
            filename = filename[:-4] + ".mp3"
        filename = os.path.basename(filename)

    total_started = time.perf_counter()

    logger.info(
        "Generating speech with gTTS: language=%s filename=%s",
        language_code,
        filename,
    )

    # ========================================================
    # MEDIA DIRECTORY
    # ========================================================
    media_root = getattr(settings, "MEDIA_ROOT", None)

    if not media_root:
        raise RuntimeError("MEDIA_ROOT is not configured.")

    tts_directory = os.path.join(media_root, "tts")
    os.makedirs(tts_directory, exist_ok=True)

    file_path = os.path.join(tts_directory, filename)

    # ========================================================
    # GENERATE AND SAVE AUDIO
    # ========================================================
    tts = gTTS(text=text, lang=gtts_lang)
    tts.save(file_path)

    logger.info(
        "Speech generated successfully via gTTS: %s total=%.2fs",
        file_path,
        time.perf_counter() - total_started,
    )

    # ========================================================
    # RETURN RELATIVE PATH
    # ========================================================
    return f"tts/{filename}"