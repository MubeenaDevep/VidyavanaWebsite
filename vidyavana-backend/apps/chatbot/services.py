"""Chatbot reply-generation service with session memory, database context, and Groq."""

import logging
import re

from django.conf import settings

from apps.courses.models import Course

from .groq_service import generate_chat_completion
from .rag.retriever import retrieve_context

logger = logging.getLogger("vidyavana")


# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------

GREETING_PATTERNS = re.compile(
    r"\b(hi|hello|hey|namaste|vanakkam)\b",
    re.IGNORECASE,
)

COURSE_PATTERNS = re.compile(
    r"\b("
    # English
    r"course|courses|class|classes|learn|training|program|programming|"
    r"python|java|web|excel|tally|data|ai|computer|"

    # Kannada
    r"ಕೋರ್ಸ್|ಕೋರ್ಸ್‌ಗಳು|ಕೋರ್ಸು|ಕೋರ್ಸುಗಳು|"
    r"ತರಬೇತಿ|ತರಬೇತಿಗಳು|"
    r"ತರಗತಿ|ತರಗತಿಗಳು|"
    r"ಕಲಿಯ|ಕಲಿಯಲು|"
    r"ಯಾವ|ಲಭ್ಯ|ಲಭ್ಯವಿವೆ|"

    # Telugu
    r"కోర్సు|కోర్సులు|"
    r"శిక్షణ|"
    r"తరగతి|తరగతులు|"
    r"నేర్చుకో|నేర్చుకోవడానికి|"
    r"అందుబాటులో|ఏ"
    r")\b",
    re.IGNORECASE,
)
FEE_PATTERNS = re.compile(
    r"\b(fee|fees|cost|price|payment|pay|charges)\b",
    re.IGNORECASE,
)

PLACEMENT_PATTERNS = re.compile(
    r"\b(placement|placements|job|jobs|career|salary|hiring|company)\b",
    re.IGNORECASE,
)

CONTACT_PATTERNS = re.compile(
    r"\b(contact|phone|address|location|visit|where|reach)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

def detect_intent(message: str) -> str:
    text = message.strip().lower()

    # ---------------------------------------------------------------
    # Greetings
    # ---------------------------------------------------------------
    if GREETING_PATTERNS.search(text):
        return "greeting"

    # Kannada greetings
    if any(
        phrase in text
        for phrase in [
            "ನಮಸ್ಕಾರ",
            "ಹಲೋ",
            "ಹಾಯ್",
        ]
    ):
        return "greeting"

    # Telugu greetings
    if any(
        phrase in text
        for phrase in [
            "నమస్కారం",
            "హలో",
            "హాయ్",
        ]
    ):
        return "greeting"

    # ---------------------------------------------------------------
    # Fees
    # ---------------------------------------------------------------
    if FEE_PATTERNS.search(text):
        return "fee_enquiry"

    if any(
        phrase in text
        for phrase in [
            "ಶುಲ್ಕ",
            "ಫೀಸ್",
            "ವೆಚ್ಚ",
            "ಬೆಲೆ",
            "ಪಾವತಿ",
        ]
    ):
        return "fee_enquiry"

    if any(
        phrase in text
        for phrase in [
            "ఫీజు",
            "ఫీజులు",
            "ఖర్చు",
            "ధర",
            "చెల్లింపు",
        ]
    ):
        return "fee_enquiry"

    # ---------------------------------------------------------------
    # Placement
    # ---------------------------------------------------------------
    if PLACEMENT_PATTERNS.search(text):
        return "placement_enquiry"

    if any(
        phrase in text
        for phrase in [
            "ಉದ್ಯೋಗ",
            "ಉದ್ಯೋಗಗಳು",
            "ಪ್ಲೇಸ್‌ಮೆಂಟ್",
            "ವೃತ್ತಿ",
            "ಕೆಲಸ",
        ]
    ):
        return "placement_enquiry"

    if any(
        phrase in text
        for phrase in [
            "ఉద్యోగం",
            "ఉద్యోగాలు",
            "ప్లేస్‌మెంట్",
            "కెరీర్",
        ]
    ):
        return "placement_enquiry"

    # ---------------------------------------------------------------
    # Contact
    # ---------------------------------------------------------------
    if CONTACT_PATTERNS.search(text):
        return "contact_enquiry"

    if any(
        phrase in text
        for phrase in [
            "ಸಂಪರ್ಕ",
            "ವಿಳಾಸ",
            "ಸ್ಥಳ",
            "ಎಲ್ಲಿ",
            "ಭೇಟಿ",
        ]
    ):
        return "contact_enquiry"

    if any(
        phrase in text
        for phrase in [
            "సంప్రదించ",
            "చిరునామా",
            "స్థలం",
            "ఎక్కడ",
            "సందర్శించ",
        ]
    ):
        return "contact_enquiry"

    # ---------------------------------------------------------------
    # Courses
    # ---------------------------------------------------------------
    if COURSE_PATTERNS.search(text):
        return "course_enquiry"

    if any(
        phrase in text
        for phrase in [
            "ಕೋರ್ಸ್",
            "ಕೋರ್ಸ್‌ಗಳು",
            "ಕೋರ್ಸು",
            "ಕೋರ್ಸುಗಳು",
            "ತರಬೇತಿ",
            "ತರಗತಿ",
            "ಕಲಿಯಲು",
            "ಕಲಿಯುವ",
            "ಲಭ್ಯವಿವೆ",
            "ಲಭ್ಯವಿದೆ",
        ]
    ):
        return "course_enquiry"

    if any(
        phrase in text
        for phrase in [
            "కోర్సు",
            "కోర్సులు",
            "శిక్షణ",
            "తరగతి",
            "నేర్చుకోవడానికి",
            "అందుబాటులో",
        ]
    ):
        return "course_enquiry"

    return "general"


def detect_language(message: str, requested_language: str = "EN") -> str:
    """Prefer the script in the message while retaining the UI selection for Latin text."""
    if re.search(r"[\u0c80-\u0cff]", message):
        return "KN"
    if re.search(r"[\u0c00-\u0c7f]", message):
        return "TE"
    return requested_language.upper() if requested_language.upper() in {"EN", "KN", "TE"} else "EN"


def _course_detail_requested(message: str) -> bool:
    text = message.lower()
    return any(
        phrase in text
        for phrase in (
            "duration", "how long", "month", "months", "week", "weeks",
            "syllabus", "eligibility", "eligible", "fee", "fees", "cost",
            "price", "ಶುಲ್ಕ", "ಫೀಸ್", "ಎಷ್ಟು ತಿಂಗಳು", "ಅವಧಿ", "ಪಠ್ಯಕ್ರಮ",
            "ఫీజు", "ఖర్చు", "ఎంత కాలం", "నెలలు", "వ్యవధి", "సిలబస్",
        )
    )


def _course_matches(message: str, courses) -> list:
    query = message.lower()
    query_words = {
        word for word in re.findall(r"[\w]+", query, re.UNICODE)
        if len(word) >= 2
    }
    ignored_words = {
        "the", "what", "which", "how", "long", "does", "course", "courses",
        "about", "for", "tell", "me", "is", "are", "and", "fee", "fees",
        "duration", "syllabus", "eligibility", "cost", "price", "ಎಷ್ಟು", "ತಿಂಗಳು",
        "కోర్సు", "కోర్సులు", "ఎంత", "నెలలు",
    }
    query_words -= ignored_words
    scored = []
    for course in courses:
        name = (course.name or "").lower()
        name_words = set(re.findall(r"[\w]+", name, re.UNICODE))
        score = 0
        if name in query:
            score += 100
        score += sum(3 for word in name_words if word in query_words)
        score += sum(1 for word in query_words if word in name)
        if score:
            scored.append((score, course))
    return [course for _, course in sorted(scored, key=lambda item: (-item[0], item[1].name))]


# ---------------------------------------------------------------------------
# Conversation history
# ---------------------------------------------------------------------------

def _build_history(session=None):
    if session is None:
        return []

    messages = []

    for msg in session.messages.order_by("created_at")[:8]:
        messages.append(
            {
                "role": "user" if msg.sender == "user" else "assistant",
                "content": msg.text,
            }
        )

    return messages


# ---------------------------------------------------------------------------
# Course knowledge retrieval
# ---------------------------------------------------------------------------

def _get_course_context(message: str, intent: str) -> str:
    """
    Retrieve relevant course information directly from the Django database.

    No embeddings or vector database are used here.
    """

    courses = (
        Course.objects
        .filter(is_active=True)
        .select_related("category")
        .order_by("order", "name")
    )

    # ---------------------------------------------------------------
    # If user asks generally about courses, give course overview.
    # ---------------------------------------------------------------

    if intent == "course_enquiry":
        words = [
            word.lower()
            for word in re.findall(r"[A-Za-z0-9]+", message)
            if len(word) >= 3
        ]

        matched_courses = _course_matches(message, courses)

        # If the question is general, show available courses.
        if not matched_courses and not _course_detail_requested(message):
            matched_courses = list(courses[:12])

        # Don't send all 57 courses to Qwen.
        matched_courses = matched_courses[:12]

    else:
        # For non-course questions, don't unnecessarily send courses.
        return ""

    if not matched_courses:
        return ""

    lines = [
        "COURSE INFORMATION FROM THE VIDYAVANA DATABASE:"
    ]

    for course in matched_courses:
        category_name = (
            course.category.name
            if course.category
            else "Not specified"
        )

        description = (
            course.short_description
            or course.description
            or "Not specified"
        )

        certificate = (
            "Yes"
            if course.certificate_included
            else "No"
        )

        lines.append(
            f"""
Course: {course.name}
Category: {category_name}
Description: {description}
Duration: {course.duration or "Not specified"}
Level: {course.get_level_display()}
Certificate: {certificate}
""".strip()
        )

    return "\n\n".join(lines)


def _get_matched_course(message: str):
    courses = (
        Course.objects.filter(is_active=True)
        .select_related("category")
        .order_by("order", "name")
    )
    matches = _course_matches(message, courses)
    return matches[0] if matches else None


def _course_specific_reply(course, message: str, language_code: str) -> str | None:
    if not course:
        return None
    text = message.lower()
    if any(term in text for term in ("duration", "how long", "month", "months", "week", "weeks", "ಎಷ್ಟು ತಿಂಗಳು", "ಅವಧಿ", "ఎంత కాలం", "నెలలు", "వ్యవధి")):
        templates = {
            "EN": f"The duration of the {course.name} course is {course.duration}.",
            "KN": f"{course.name} ಕೋರ್ಸ್‌ನ ಅವಧಿ {course.duration}.",
            "TE": f"{course.name} కోర్సు వ్యవధి {course.duration}.",
        }
        return templates[language_code]
    if any(term in text for term in ("fee", "fees", "cost", "price", "ಶುಲ್ಕ", "ಫೀಸ್", "ఫీజు", "ఖర్చు")):
        value = str(course.fee) if course.fee is not None else None
        if value is None:
            return {
                "EN": "The fee for this course is not currently available. Please contact Vidyavana for the latest fee details.",
                "KN": "ಈ ಕೋರ್ಸ್‌ನ ಶುಲ್ಕದ ಮಾಹಿತಿ ಪ್ರಸ್ತುತ ಲಭ್ಯವಿಲ್ಲ. ಇತ್ತೀಚಿನ ವಿವರಗಳಿಗಾಗಿ ವಿದ್ಯಾವನವನ್ನು ಸಂಪರ್ಕಿಸಿ.",
                "TE": "ఈ కోర్సు ఫీజు సమాచారం ప్రస్తుతం అందుబాటులో లేదు. తాజా వివరాల కోసం విద్యావనను సంప్రదించండి.",
            }[language_code]
        return {
            "EN": f"The fee for the {course.name} course is {value}.",
            "KN": f"{course.name} ಕೋರ್ಸ್‌ನ ಶುಲ್ಕ {value}.",
            "TE": f"{course.name} కోర్సు ఫీజు {value}.",
        }[language_code]
    return None


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def _build_system_prompt(
    selected_language: str,
    context: str = "",
) -> str:

    context_section = ""

    if context:
        context_section = f"""

==============================
VERIFIED VIDYAVANA INFORMATION
==============================

{context}

==============================
END VERIFIED INFORMATION
==============================
"""

    return f"""
You are the AI assistant for Vidyavana Computer Educational Institute.

Always reply ONLY in {selected_language}.

LANGUAGE RULES:
- English → reply only in English.
- Kannada → reply only in Kannada.
- Telugu → reply only in Telugu.
- Never mix languages.
- Keep technical course names in their original form when appropriate.

IMPORTANT ACCURACY RULES:
- Vidyavana is a real educational institute.
- Use the verified Vidyavana information provided below when answering institute-specific questions.
- NEVER invent course names, course durations, certificates, fees, placement statistics, addresses, phone numbers, timings, or other institute information.
- If the requested information is not available in the verified information, clearly say that the information is not currently available.
- Do not guess.
- Do not pretend that information exists when it does not.

CURRENT BUSINESS RULES:
- Course enrollment is currently NOT available through the website.
- Online payment is currently NOT available.
- Course fees are currently NOT displayed/provided by the institute.
- If someone asks about fees, politely explain that current fee information is not available and suggest contacting the institute.
- Do NOT tell users to "enroll now".
- You may encourage interested visitors to contact the institute or submit an enquiry.
- The website's purpose is to help visitors learn about courses, training, placements, and the institute.

LEAD GENERATION:
- If a visitor shows strong interest in a course, training, placement, or joining the institute, politely encourage them to contact the institute or submit an enquiry.
- Do not pressure the visitor.
- Do not collect sensitive information unnecessarily.

RESPONSE STYLE:
- Be helpful, natural, concise, and professional.
- Answer the user's actual question first.
- Do not give long explanations unless the user asks for details.
- If the user asks for a course, provide the relevant course information available in the database.
{context_section}
""".strip()


# ---------------------------------------------------------------------------
# Fallback response
# ---------------------------------------------------------------------------

def _fallback_reply(
    message: str,
    language_code: str = "EN",
    intent=None,
) -> dict:

    intent = intent or detect_intent(message)

    if intent == "greeting":
        text = {
            "KN": "ನಮಸ್ಕಾರ! ನಾನು ವಿದ್ಯಾವನ ಸಹಾಯಕ. ಕೋರ್ಸ್‌ಗಳು, ತರಬೇತಿ, ಉದ್ಯೋಗಾವಕಾಶಗಳು ಮತ್ತು ಸಂಸ್ಥೆಯ ಮಾಹಿತಿಯ ಬಗ್ಗೆ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಹುದು.",
            "TE": "నమస్కారం! నేను విద్యావన సహాయకుడిని. కోర్సులు, శిక్షణ, ప్లేస్‌మెంట్‌లు మరియు సంస్థ సమాచారం గురించి మీకు సహాయం చేయగలను.",
        }.get(language_code, "Hi! I'm the Vidyavana Assistant. I can help you with our courses, training, placements, and institute information.")

    elif intent == "fee_enquiry":

        text = {
            "KN": "ಪ್ರಸ್ತುತ ಕೋರ್ಸ್ ಶುಲ್ಕದ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ. ಇತ್ತೀಚಿನ ಶುಲ್ಕ ವಿವರಗಳಿಗಾಗಿ ವಿದ್ಯಾವನವನ್ನು ಸಂಪರ್ಕಿಸಿ.",
            "TE": "ప్రస్తుతం కోర్సు ఫీజు సమాచారం అందుబాటులో లేదు. తాజా ఫీజు వివరాల కోసం విద్యావనను సంప్రదించండి.",
        }.get(language_code, "Current course fee information is not available at the moment. Please contact Vidyavana for the latest fee details.")

    elif intent == "placement_enquiry":

        text = {
            "KN": "ವಿದ್ಯಾವನ ಉದ್ಯೋಗಕೇಂದ್ರಿತ ತರಬೇತಿ ಮತ್ತು ವೃತ್ತಿ ಸಹಾಯವನ್ನು ನೀಡುತ್ತದೆ. ಇತ್ತೀಚಿನ ಉದ್ಯೋಗ ಮಾಹಿತಿಗಾಗಿ ಸಂಸ್ಥೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ.",
            "TE": "విద్యావన ప్లేస్‌మెంట్ ఆధారిత శిక్షణ మరియు కెరీర్ సహాయాన్ని అందిస్తుంది. తాజా ప్లేస్‌మెంట్ సమాచారం కోసం సంస్థను సంప్రదించండి.",
        }.get(language_code, "Vidyavana provides placement-focused training and career support. For the latest placement information, please contact the institute.")

    elif intent == "contact_enquiry":

        text = {
            "KN": "ವೆಬ್‌ಸೈಟ್‌ನ ಸಂಪರ್ಕ ವಿಭಾಗದ ಮೂಲಕ ವಿದ್ಯಾವನವನ್ನು ಸಂಪರ್ಕಿಸಬಹುದು. ನಮ್ಮ ತಂಡವು ಕೋರ್ಸ್ ಮತ್ತು ತರಬೇತಿ ವಿಚಾರಣೆಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
            "TE": "వెబ్‌సైట్‌లోని సంప్రదింపు విభాగం ద్వారా విద్యావనను సంప్రదించవచ్చు. మా బృందం కోర్సు మరియు శిక్షణ ప్రశ్నల్లో సహాయం చేస్తుంది.",
        }.get(language_code, "You can contact Vidyavana through the Contact section on the website. Our team can help you with course and training enquiries.")

    elif intent == "course_enquiry":

        matched_courses = Course.objects.filter(
            is_active=True
        ).select_related("category")[:5]

        if matched_courses:

            course_names = ", ".join(
                course.name for course in matched_courses
            )

            text = {
                "KN": f"ನಾವು ಪ್ರಸ್ತುತ {course_names} ಮುಂತಾದ ಕೋರ್ಸ್‌ಗಳನ್ನು ನೀಡುತ್ತೇವೆ. ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಕೋರ್ಸ್ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕೇ?",
                "TE": f"మేము ప్రస్తుతం {course_names} వంటి కోర్సులను అందిస్తున్నాము. ఏదైనా ప్రత్యేక కోర్సు గురించి సమాచారం కావాలా?",
            }.get(language_code, f"We currently offer courses such as {course_names}. Would you like information about a particular course?")

        else:

            text = {
                "KN": "ಪ್ರಸ್ತುತ ಲಭ್ಯವಿರುವ ಕೋರ್ಸ್‌ಗಳ ಮಾಹಿತಿಗಾಗಿ ವಿದ್ಯಾವನವನ್ನು ಸಂಪರ್ಕಿಸಿ.",
                "TE": "ప్రస్తుతం అందుబాటులో ఉన్న కోర్సుల సమాచారం కోసం విద్యావనను సంప్రదించండి.",
            }.get(language_code, "Please contact Vidyavana for information about the currently available courses.")

    else:

        text = {
            "KN": "ವಿದ್ಯಾವನದ ಕೋರ್ಸ್‌ಗಳು, ತರಬೇತಿ, ಉದ್ಯೋಗಾವಕಾಶಗಳು ಮತ್ತು ಸಂಸ್ಥೆಯ ಮಾಹಿತಿಯಲ್ಲಿ ನಾನು ಸಹಾಯ ಮಾಡಬಹುದು. ನಿಮಗೆ ಏನು ತಿಳಿದುಕೊಳ್ಳಬೇಕು?",
            "TE": "విద్యావన కోర్సులు, శిక్షణ, ప్లేస్‌మెంట్‌లు మరియు సంస్థ సమాచారం గురించి నేను సహాయం చేయగలను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
        }.get(language_code, "I can help you with Vidyavana's courses, training, placements, and institute information. What would you like to know?")

    return {
        "text": text,
        "intent": intent,
    }


# ---------------------------------------------------------------------------
# Main reply generation
# ---------------------------------------------------------------------------

def generate_reply(
    message: str,
    language_code: str = "EN",
    session=None,
) -> dict:

    """
    Generate chatbot response.

    Simple institute-specific questions are answered directly from
    verified Django database information.

    Ollama is used only for questions that actually require
    AI-generated reasoning.
    """

    intent = detect_intent(message)

    language_code = detect_language(message, language_code)

    # A course-specific fee question is still a structured course enquiry.
    # This lets it use the Course record instead of the generic fee fallback.
    matched_course = None
    if intent == "fee_enquiry" or _course_detail_requested(message):
        try:
            matched_course = _get_matched_course(message)
        except Exception:
            logger.exception("Specific course lookup failed")
        if matched_course:
            intent = "course_enquiry"

    language_map = {
        "EN": "English",
        "KN": "Kannada",
        "TE": "Telugu",
    }

    selected_language = language_map.get(
        language_code,
        "English",
    )

    # ---------------------------------------------------------------
    # Retrieve verified database information.
    # ---------------------------------------------------------------

    try:
        course_context = _get_course_context(
            message=message,
            intent=intent,
        )

    except Exception:
        logger.exception(
            "Database knowledge retrieval failed"
        )
        course_context = ""

    try:
        rag_context = retrieve_context(message)
    except Exception:
        logger.exception("RAG context retrieval failed")
        rag_context = ""

    verified_context = "\n\n".join(
        context
        for context in (rag_context, course_context)
        if context
    )

    # ---------------------------------------------------------------
    # COURSE ENQUIRY
    #
    # Do NOT send simple course-list questions to Ollama.
    # The database already contains the verified information.
    # ---------------------------------------------------------------

    if intent == "course_enquiry" and course_context:

        specific_reply = _course_specific_reply(
            matched_course,
            message,
            language_code,
        )
        if specific_reply:
            return {
                "text": specific_reply,
                "intent": intent,
            }

        courses = (
            Course.objects
            .filter(is_active=True)
            .select_related("category")
            .order_by("order", "name")[:12]
        )

        matched_courses = _course_matches(message, courses)
        course_names = [course.name for course in (matched_courses or courses)]

        if language_code == "KN":

            text = (
                "ವಿದ್ಯಾವನದಲ್ಲಿ ಪ್ರಸ್ತುತ ಲಭ್ಯವಿರುವ ಕೆಲವು ಕೋರ್ಸ್‌ಗಳು:\n\n"
                + "\n".join(
                    f"• {name}"
                    for name in course_names
                )
                + "\n\nಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಕೋರ್ಸ್ ಬಗ್ಗೆ ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಬೇಕಾದರೆ ಕೇಳಬಹುದು."
            )

        elif language_code == "TE":

            text = (
                "విద్యావనలో ప్రస్తుతం అందుబాటులో ఉన్న కొన్ని కోర్సులు:\n\n"
                + "\n".join(
                    f"• {name}"
                    for name in course_names
                )
                + "\n\nమీకు ఏదైనా ప్రత్యేక కోర్సు గురించి మరింత సమాచారం కావాలంటే అడగండి."
            )

        else:

            text = (
                "Vidyavana currently offers courses such as:\n\n"
                + "\n".join(
                    f"• {name}"
                    for name in course_names
                )
                + "\n\nWould you like more information about a particular course?"
            )

        logger.info(
            "Course enquiry answered directly from database "
            "session=%s language=%s",
            getattr(session, "uuid", None),
            language_code,
        )

        return {
            "text": text,
            "intent": intent,
        }

    # ---------------------------------------------------------------
    # Other simple enquiries can also use the safe fallback.
    # This avoids unnecessary Ollama calls for known intents.
    # ---------------------------------------------------------------

    if intent in {
        "greeting",
        "fee_enquiry",
        "placement_enquiry",
        "contact_enquiry",
    }:
        fallback = _fallback_reply(
            message=message,
            language_code=language_code,
            intent=intent,
        )

        # The fallback currently contains English text.
        # Keep this path unchanged for now; we will improve
        # multilingual responses in the next step.

        return fallback

    # ---------------------------------------------------------------
    # Use Groq only for general questions that need AI reasoning.
    # ---------------------------------------------------------------

    try:
        history = _build_history(session=session)
        system_prompt = _build_system_prompt(
            selected_language=selected_language,
            context=verified_context,
        )
        text = generate_chat_completion(
            system_prompt=system_prompt,
            history=history,
            user_message=message,
            rag_context=verified_context,
        )

        logger.info(
            "Groq reply generated for session=%s intent=%s",
            getattr(session, "uuid", None),
            intent,
        )

        return {
            "text": text,
            "intent": intent,
        }

    except Exception:
        logger.exception(
            "Groq reply generation failed; falling back to rule-based response"
        )

    # ---------------------------------------------------------------
    # Safe fallback.
    # ---------------------------------------------------------------

    return _fallback_reply(
        message=message,
        language_code=language_code,
        intent=intent,
    )