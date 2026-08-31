import logging
import os
import threading
import time
import uuid

import soundfile as sf
import torch
from django.conf import settings
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

logger = logging.getLogger("vidyavana")


MODEL_ID = "ai4bharat/indic-parler-tts"

DEVICE = "cpu"


# ============================================================
# GLOBAL MODEL CACHE
# ============================================================

_tts_model = None
_text_tokenizer = None
_description_tokenizer = None

# Prevent multiple background threads from loading the
# huge TTS model at the same time.
_model_lock = threading.Lock()
_generation_lock = threading.Lock()


# ============================================================
# VOICE DESCRIPTIONS
# ============================================================

VOICE_DESCRIPTIONS = {
    "EN": (
        "A clear and natural female voice speaking English. "
        "The speaker speaks at a moderate speed with a friendly "
        "and professional tone."
    ),

    "KN": (
        "A clear and natural female voice speaking Kannada. "
        "The speaker speaks at a moderate speed with a friendly "
        "and professional tone."
    ),

    "TE": (
        "A clear and natural female voice speaking Telugu. "
        "The speaker speaks at a moderate speed with a friendly "
        "and professional tone."
    ),
}


# ============================================================
# LOAD MODEL
# ============================================================

def load_tts_model():
    global _tts_model
    global _text_tokenizer
    global _description_tokenizer

    # Already loaded
    if _tts_model is not None:
        return

    # Prevent two requests from loading the model simultaneously
    with _model_lock:

        # Check again after acquiring the lock
        if _tts_model is not None:
            return

        load_started = time.perf_counter()
        logger.info("Loading Indic Parler TTS model...")

        # ----------------------------------------------------
        # Load Parler TTS model
        # ----------------------------------------------------

        _tts_model = (
            ParlerTTSForConditionalGeneration
            .from_pretrained(MODEL_ID)
            .to(DEVICE)
        )
        _tts_model.eval()
        model_loaded_at = time.perf_counter()

        # ----------------------------------------------------
        # Speech text tokenizer
        # ----------------------------------------------------

        _text_tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID
        )
        text_tokenizer_loaded_at = time.perf_counter()

        # ----------------------------------------------------
        # Voice description tokenizer
        # ----------------------------------------------------

        _description_tokenizer = AutoTokenizer.from_pretrained(
            "google/flan-t5-large"
        )
        description_tokenizer_loaded_at = time.perf_counter()

        logger.info(
            "Indic Parler TTS model loaded successfully. TTS model ready "
            "model=%.2fs text_tokenizer=%.2fs description_tokenizer=%.2fs total=%.2fs",
            model_loaded_at - load_started,
            text_tokenizer_loaded_at - model_loaded_at,
            description_tokenizer_loaded_at - text_tokenizer_loaded_at,
            description_tokenizer_loaded_at - load_started,
        )


# ============================================================
# GENERATE SPEECH
# ============================================================

def generate_speech(
    text: str,
    language_code: str = "EN",
    filename: str | None = None,
) -> str:

    """
    Generate speech from chatbot text.

    The filename comes from the chatbot view so that the
    frontend URL and generated file always match.

    Returns:
        Relative media path, for example:

        tts/abc123.wav
    """

    # --------------------------------------------------------
    # Validate text
    # --------------------------------------------------------

    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty."
        )

    # --------------------------------------------------------
    # Normalize language
    # --------------------------------------------------------

    language_code = language_code.upper()

    if language_code not in VOICE_DESCRIPTIONS:
        language_code = "EN"

    # --------------------------------------------------------
    # Generate filename if one wasn't supplied
    # --------------------------------------------------------

    if not filename:
        filename = f"{uuid.uuid4()}.wav"

    # Make sure filename is only a filename
    filename = os.path.basename(filename)

    # Serializing generation avoids unsafe concurrent access to the model and
    # prevents multiple requests from competing for CPU memory.
    with _generation_lock:
        return _generate_speech_locked(text, language_code, filename)


def _generate_speech_locked(
    text: str,
    language_code: str,
    filename: str,
) -> str:
    total_started = time.perf_counter()
    load_started = time.perf_counter()
    load_tts_model()
    load_seconds = time.perf_counter() - load_started

    description = VOICE_DESCRIPTIONS[language_code]

    logger.info(
        "Generating speech: language=%s filename=%s",
        language_code,
        filename,
    )

    # ========================================================
    # TOKENIZE SPEECH TEXT
    # ========================================================

    tokenization_started = time.perf_counter()
    prompt_inputs = _text_tokenizer(
        text,
        return_tensors="pt",
        padding=True,
    )

    # ========================================================
    # TOKENIZE VOICE DESCRIPTION
    # ========================================================

    description_inputs = _description_tokenizer(
        description,
        return_tensors="pt",
        padding=True,
    )
    tokenization_seconds = time.perf_counter() - tokenization_started

    input_ids = prompt_inputs.input_ids.to(
        DEVICE
    )

    attention_mask = prompt_inputs.attention_mask.to(
        DEVICE
    )

    description_input_ids = (
        description_inputs.input_ids.to(DEVICE)
    )

    description_attention_mask = (
        description_inputs.attention_mask.to(DEVICE)
    )

    # ========================================================
    # GENERATE AUDIO
    # ========================================================

    inference_started = time.perf_counter()
    with torch.inference_mode():

        generation = _tts_model.generate(
            input_ids=description_input_ids,
            attention_mask=description_attention_mask,
            prompt_input_ids=input_ids,
            prompt_attention_mask=attention_mask,
        )
    inference_seconds = time.perf_counter() - inference_started

    audio = (
        generation
        .cpu()
        .numpy()
        .squeeze()
    )

    # ========================================================
    # MEDIA DIRECTORY
    # ========================================================

    media_root = getattr(
        settings,
        "MEDIA_ROOT",
        None,
    )

    if not media_root:
        raise RuntimeError(
            "MEDIA_ROOT is not configured."
        )

    tts_directory = os.path.join(
        media_root,
        "tts",
    )

    os.makedirs(
        tts_directory,
        exist_ok=True,
    )

    # ========================================================
    # IMPORTANT:
    # USE THE SAME FILENAME RECEIVED FROM views.py
    # ========================================================

    file_path = os.path.join(
        tts_directory,
        filename,
    )
    temporary_path = f"{file_path}.{uuid.uuid4().hex}.tmp"

    # ========================================================
    # SAVE WAV
    # ========================================================

    save_started = time.perf_counter()
    try:
        sf.write(
            temporary_path,
            audio,
            _tts_model.config.sampling_rate,
            format="WAV",
        )

        file_info = sf.info(temporary_path)
        if file_info.frames <= 0 or file_info.samplerate <= 0:
            raise RuntimeError("Generated audio file is empty or invalid.")

        os.replace(temporary_path, file_path)
    except Exception:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise
    save_seconds = time.perf_counter() - save_started

    logger.info(
        "Speech generated successfully: %s load=%.2fs tokenize=%.2fs "
        "inference=%.2fs save=%.2fs total=%.2fs",
        file_path,
        load_seconds,
        tokenization_seconds,
        inference_seconds,
        save_seconds,
        time.perf_counter() - total_started,
    )

    # ========================================================
    # RETURN SAME PATH
    # ========================================================

    return f"tts/{filename}"