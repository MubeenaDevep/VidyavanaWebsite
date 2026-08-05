"""Chatbot reply-generation service with session memory and Ollama fallback."""

import logging
import re

from django.conf import settings

from apps.courses.models import Course

logger = logging.getLogger("vidyavana")

try:
    import ollama
except ImportError:  # pragma: no cover
    ollama = None

GREETING_PATTERNS = re.compile(r"\b(hi|hello|hey|namaste|vanakkam)\b", re.IGNORECASE)
COURSE_PATTERNS = re.compile(r"\b(course|class|learn|training|programming|python|java|web|excel|tally)\b", re.IGNORECASE)
FEE_PATTERNS = re.compile(r"\b(fee|fees|cost|price|payment)\b", re.IGNORECASE)
PLACEMENT_PATTERNS = re.compile(r"\b(placement|job|career|salary|hiring)\b", re.IGNORECASE)
CONTACT_PATTERNS = re.compile(r"\b(contact|phone|address|location|visit)\b", re.IGNORECASE)


def detect_intent(message: str) -> str:
    if GREETING_PATTERNS.search(message):
        return "greeting"
    if FEE_PATTERNS.search(message):
        return "fee_enquiry"
    if PLACEMENT_PATTERNS.search(message):
        return "placement_enquiry"
    if CONTACT_PATTERNS.search(message):
        return "contact_enquiry"
    if COURSE_PATTERNS.search(message):
        return "course_enquiry"
    return "general"


def _build_history(session=None):
    if session is None:
        return []

    messages = []
    for msg in session.messages.order_by("created_at")[:8]:
        messages.append({"role": "user" if msg.sender == "user" else "assistant", "content": msg.text})
    return messages


def _fallback_reply(message: str, language_code: str = "EN", intent=None) -> dict:
    intent = intent or detect_intent(message)

    if intent == "greeting":
        text = "Hi! I'm the Vidyavana Assistant. Ask me about our courses, fees, batch timings, or placements."
    elif intent == "fee_enquiry":
        text = "Course fees vary by program and are kept affordable. Tell me which course you're interested in and I'll share the details."
    elif intent == "placement_enquiry":
        text = "We offer dedicated placement training — resume building, mock interviews, and introductions to hiring partners — for eligible students."
    elif intent == "contact_enquiry":
        text = "You can reach us via the Contact section on our homepage, or share your phone number here and our team will call you back."
    elif intent == "course_enquiry":
        matched = Course.objects.filter(is_active=True, name__icontains=message.split()[-1]).first()
        if matched:
            text = f"{matched.name} is a great choice — {matched.duration}, {matched.get_level_display()} level. Would you like to enroll?"
        else:
            text = "We offer courses in Programming, Web Development, Data & Analytics, AI, Office Productivity, and more. Which area interests you?"
    else:
        text = "I can help with course details, fees, placements, or admissions. Could you tell me a bit more about what you're looking for?"

    return {"text": text, "intent": intent}


def generate_reply(message: str, language_code: str = "EN", session=None) -> dict:
    """Returns {"text": str, "intent": str} using Ollama when available and a safe fallback otherwise."""
    intent = detect_intent(message)

    if ollama is not None:
        try:
            history = _build_history(session=session)
            language_map = {
                "EN": "English",
                "KN": "Kannada",
                "TE": "Telugu",
                }
            selected_language = language_map.get(language_code.upper(), "English")
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""
You are the AI assistant for Vidyavana Computer Educational Institute.

Always reply ONLY in {selected_language}.

Rules:
- If the selected language is English, reply only in English.
- If the selected language is Kannada, reply only in Kannada.
- If the selected language is Telugu, reply only in Telugu.
- Never mix languages.
- Answer naturally and professionally.
- Help users with admissions, courses, fees, placements, certificates, timings, and institute information.
- If you don't know something, politely ask the user for clarification instead of making up information.
""",
                    },
                    *history,
                    {"role": "user", "content": message},
                ],
                options={"temperature": 0.2},
            )
            text = response["message"]["content"].strip()
            logger.info("Ollama reply generated for session=%s", getattr(session, "uuid", None))
            return {"text": text, "intent": intent}
        except Exception:
            logger.exception("Ollama reply generation failed; falling back to rule-based response")

    return _fallback_reply(message=message, language_code=language_code, intent=intent)
