import os

import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

django.setup()

from apps.chatbot.tts_service import generate_speech


print("Starting TTS test...")

audio_path = generate_speech(
    "ನಮಸ್ಕಾರ, ವಿದ್ಯಾವನ ಕಂಪ್ಯೂಟರ್ ಶಿಕ್ಷಣ ಸಂಸ್ಥೆಗೆ ಸ್ವಾಗತ.",
    "KN",
)

print()
print("======================================")
print("SUCCESS!")
print("Audio:", audio_path)
print("======================================")