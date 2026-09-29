"""Chatbot reply-generation service with session memory, database context,
verified RAG knowledge, and Groq.
"""

import logging
import re

from apps.courses.models import Course

from .groq_service import generate_chat_completion
from .models import ChatMessage
from .rag.retriever import retrieve_context

logger = logging.getLogger("vidyavana")


# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------

GREETING_PATTERNS = re.compile(
    r"\b(hi|hello|hey|namaste|vanakkam)\b",
    re.IGNORECASE,
)

# IMPORTANT:
# Do not use very short words such as "ai" by themselves here.
# "AI voice" should not automatically become a course enquiry.
COURSE_PATTERNS = re.compile(
    r"\b("
    r"course|courses|class|classes|learn|training|program|programming|"
    r"python|java|javascript|web development|backend|django|fastapi|"
    r"excel|tally|big data|hadoop|power bi|database|sql|mongodb|"
    r"artificial intelligence|machine learning|prompt engineering|"
    r"\bai\b|"
    r"computer fundamentals|c programming|react|angular|"
    r"ಕೋರ್ಸ್|ಕೋರ್ಸ್‌ಗಳು|ಕೋರ್ಸು|ಕೋರ್ಸುಗಳು|"
    r"ತರಬೇತಿ|ತರಬೇತಿಗಳು|"
    r"ತರಗತಿ|ತರಗತಿಗಳು|"
    r"ಕಲಿಯ|ಕಲಿಯಲು|"
    r"ಯಾವ|ಲಭ್ಯ|ಲಭ್ಯವಿವೆ|"
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

INSTITUTE_PATTERNS = re.compile(
    r"\b("
    r"certificates?|certification|who can join|eligib|"
    r"about vidyavana|about the institute|institute"
    r")\b",
    re.IGNORECASE,
)

JOIN_PATTERNS = re.compile(
    r"\b(join|admission|enquir|more information|further details)\b",
    re.IGNORECASE,
)


def _is_general_definition_question(message: str) -> bool:
    text = (message or "").lower().strip()
    if not text:
        return False
    if not re.search(r"\b(what is|what are|define|explain)\b", text):
        return False
    institute_cues = (
        "course", "courses", "training", "fee", "fees", "cost", "duration",
        "admission", "timing", "timings", "placement", "contact", "certificate",
        "eligibility", "location", "address", "batch", "career", "job",
        "ಕೋರ್ಸ್", "ಕೋರ್ಸು", "ಶುಲ್ಕ", "ಅವಧಿ", "ಪ್ರವೇಶ", "ವೇಳೆ", "ಸಂಪರ್ಕ",
        "ಪ್ರಮಾಣಪತ್ರ", "ಅರ್ಹತೆ", "ಸ್ಥಳ", "ಫీజು", "ಉದ್ಯೋಗ", "ಕೋರ್ಸು",
    )
    return not any(cue in text for cue in institute_cues)


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

    if any(
        phrase in text
        for phrase in [
            "ನಮಸ್ಕಾರ",
            "ಹಲೋ",
            "ಹಾಯ್",
        ]
    ):
        return "greeting"

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
    # Institute
    # ---------------------------------------------------------------

    if INSTITUTE_PATTERNS.search(text) or any(
        phrase in text
        for phrase in [
            "ಪ್ರಮಾಣಪತ್ರ",
            "ಸರ್ಟಿಫಿಕೇಟ್",
            "ಯಾರು ಸೇರಬಹುದು",
            "ಅರ್ಹತೆ",
            "సర్టిఫికేట్",
            "ధృవీకరణ",
            "ఎవరు చేరవచ్చు",
            "అర్హత",
        ]
    ):
        return "institute_enquiry"

    # ---------------------------------------------------------------
    # Joining / enquiry
    # ---------------------------------------------------------------

    if JOIN_PATTERNS.search(text) or any(
        phrase in text
        for phrase in [
            "ಸೇರಬೇಕು",
            "ಪ್ರವೇಶ",
            "ಹೆಚ್ಚಿನ ಮಾಹಿತಿ",
            "ವಿಚಾರಣೆ",
            "చేరాలి",
            "ప్రవేశం",
            "మరింత సమాచారం",
            "విచారణ",
        ]
    ):
        return "course_enquiry"

    # ---------------------------------------------------------------
    # Courses
    # ---------------------------------------------------------------

    if _is_general_definition_question(text):
        return "general"

    if COURSE_PATTERNS.search(text):
        return "course_enquiry"

    return "general"


def _normalise_relevance_tokens(text: str) -> set[str]:
    value = (text or "").lower()
    tokens = set(re.findall(r"[\w\u0c80-\u0cff\u0c00-\u0c7f]+", value, flags=re.UNICODE))
    stop_words = {
        "a", "an", "the", "what", "which", "when", "where", "how", "why",
        "who", "is", "are", "do", "does", "did", "can", "could", "would",
        "should", "you", "your", "we", "our", "about", "for", "from",
        "tell", "me", "it", "its", "that", "this", "these", "those", "of",
        "in", "on", "at", "to", "and", "or", "be", "with", "about", "many",
        "much", "some", "any", "there", "please", "the", "details", "information",
        "course", "courses", "coarse", "cources", "program", "programs",
    }
    return {token for token in tokens if token and token not in stop_words and len(token) > 1}


def _is_institute_relevant_question(message: str) -> bool:
    text = (message or "").lower()
    if not text:
        return False

    institute_cues = (
        "course", "courses", "class", "classes", "duration", "fee", "fees",
        "admission", "enroll", "location", "address", "timing", "timings",
        "placement", "contact", "certificate", "eligibility", "training", "batch",
        "batch timings", "who can join", "what courses", "which courses",
        "ಕೋರ್ಸ್", "ಕೋರ್ಸ್‌ಗಳು", "ಕೋರ್ಸು", "ಶೈಕ್ಷಣಿಕ", "ವೇಳೆ", "ಸ್ಥಳ", "ಸಂಪರ್ಕ",
        "ಶುಲ್ಕ", "ಅರ್ಹತೆ", "ತರಬೇತಿ", "ಪ್ರಮಾಣಪತ್ರ", "ಉದ್ಯೋಗ", "ಎಷ್ಟು", "ಅವಧಿ",
        "నెలలు", "ప్లేస్‌మెంట్", "ఫీజు", "కోర్సు", "సమయం", "ఎక్కడ", "చిరునామా",
    )
    return any(cue in text for cue in institute_cues)


def _should_use_rag_context(question: str, rag_context: str, matched_course=None) -> bool:
    if not rag_context or not rag_context.strip():
        return False

    if matched_course is not None:
        return True

    if not _is_institute_relevant_question(question):
        return False

    question_tokens = _normalise_relevance_tokens(question)
    context_tokens = _normalise_relevance_tokens(rag_context)
    if not question_tokens or not context_tokens:
        return bool(rag_context)

    overlap = len(question_tokens & context_tokens)
    if overlap:
        return True

    institute_context_terms = (
        "course", "courses", "fee", "fees", "admission", "certificate",
        "placement", "location", "address", "duration", "training", "batch",
        "timing", "contact", "eligibility", "institute", "vidyavana",
    )
    return any(term in rag_context.lower() for term in institute_context_terms)


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(message: str, requested_language: str = "EN") -> str:
    """Prefer the script in the message while retaining UI selection for
    Latin text.
    """

    if re.search(r"[\u0c80-\u0cff]", message):
        return "KN"

    if re.search(r"[\u0c00-\u0c7f]", message):
        return "TE"

    requested = requested_language.upper()

    return requested if requested in {"EN", "KN", "TE"} else "EN"


# ---------------------------------------------------------------------------
# Course/detail detection
# ---------------------------------------------------------------------------

def _course_detail_requested(message: str) -> bool:
    text = message.lower()

    return any(
        phrase in text
        for phrase in (
            "duration",
            "how long",
            "month",
            "months",
            "week",
            "weeks",
            "syllabus",
            "topics",
            "topic",
            "what will i learn",
            "what will i learn in",
            "contents",
            "curriculum",
            "eligibility",
            "eligible",
            "fee",
            "fees",
            "cost",
            "price",
            "certificate",
            "certification",
            "ಶುಲ್ಕ",
            "ಫೀಸ್",
            "ಎಷ್ಟು ತಿಂಗಳು",
            "ಅವಧಿ",
            "ಪಠ್ಯಕ್ರಮ",
            "ವಿಷಯಗಳು",
            "ಏನು ಕಲಿಯ",
            "ఫీజు",
            "ఖర్చు",
            "ఎంత కాలం",
            "నెలలు",
            "వ్యవధి",
            "సిలబస్",
            "విషయాలు",
        )
    )


def _is_course_list_request(message: str) -> bool:
    text = message.lower().strip()

    list_phrases = (
        "what courses do you offer",
        "what courses do you have",
        "which courses do you offer",
        "which courses are available",
        "what courses are available",
        "list courses",
        "available courses",
        "courses available",
        "courses do you offer",
        "course list",
        "what can i learn",
        "ಕೋರ್ಸ್‌ಗಳು ಯಾವುವು",
        "ಯಾವ ಕೋರ್ಸ್‌ಗಳು",
        "ಲಭ್ಯವಿರುವ ಕೋರ್ಸ್‌ಗಳು",
        "ఏ కోర్సులు ఉన్నాయి",
        "ఏ కోర్సులు అందిస్తున్నారు",
        "కోర్సులు ఏవి",
    )

    return any(phrase in text for phrase in list_phrases)


# ---------------------------------------------------------------------------
# Course matching
# ---------------------------------------------------------------------------

def _normalise_course_text(value: str) -> str:
    value = (value or "").lower()
    value = value.replace("-", " ")
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _course_matches(message: str, courses) -> list:
    """
    Match a user's message against course names.

    Matching deliberately avoids treating tiny words such as "ai" as a
    generic substring match across unrelated course names.
    """

    query = _normalise_course_text(message)

    query_words = {
        word
        for word in re.findall(r"[\w]+", query, re.UNICODE)
        if len(word) >= 2
    }

    ignored_words = {
        "the",
        "what",
        "which",
        "how",
        "long",
        "does",
        "do",
        "you",
        "offer",
        "offers",
        "have",
        "course",
        "courses",
        "about",
        "tell",
        "me",
        "is",
        "are",
        "and",
        "for",
        "its",
        "it",
        "will",
        "learn",
        "learning",
        "topics",
        "topic",
        "what",
        "months",
        "month",
        "weeks",
        "week",
        "duration",
        "syllabus",
        "curriculum",
        "contents",
        "eligibility",
        "eligible",
        "fee",
        "fees",
        "cost",
        "price",
        "certificate",
        "certification",
        "ಶುಲ್ಕ",
        "ಫೀಸ್",
        "ಎಷ್ಟು",
        "ತಿಂಗಳು",
        "ಅವಧಿ",
        "ಪಠ್ಯಕ್ರಮ",
        "ವಿಷಯಗಳು",
        "ಕೋರ್ಸ್",
        "ಕೋರ್ಸು",
        "ಕೋರ್ಸುಗಳು",
        "ಕೋರ್ಸ್‌ಗಳು",
        "ఫీజు",
        "ఖర్చు",
        "ఎంత",
        "కాలం",
        "నెలలు",
        "వ్యవధి",
        "సిలబస్",
        "విషయాలు",
        "కోర్సు",
        "కోర్సులు",
    }

    query_words -= ignored_words

    scored = []

    for course in courses:
        name = course.name or ""
        normalised_name = _normalise_course_text(name)
        name_words = set(
            re.findall(r"[\w]+", normalised_name, re.UNICODE)
        )

        score = 0

        # Exact course name.
        if normalised_name and normalised_name in query:
            score += 100

        # Strong exact phrase matches.
        if (
            "artificial intelligence" in query
            and "artificial intelligence" in normalised_name
        ):
            score += 80

        if (
            "machine learning" in query
            and "machine learning" in normalised_name
        ):
            score += 80

        if (
            "prompt engineering" in query
            and "prompt engineering" in normalised_name
        ):
            score += 80

        # Treat "AI course" as Artificial Intelligence course rather than
        # matching every course whose name happens to contain "ai".
        if (
            re.search(r"\bai\s+course\b", query)
            and "artificial intelligence" in normalised_name
        ):
            score += 90

        if (
            re.search(r"\bai\b", query)
            and "artificial intelligence" in normalised_name
        ):
            score += 90

        # Exact meaningful word matches.
        score += sum(
            5 for word in query_words
            if word in name_words
        )

        # Only allow substring matching for meaningful words.
        score += sum(
            1
            for word in query_words
            if len(word) >= 4 and word in normalised_name
        )

        if score:
            scored.append((score, course))

    return [
        course
        for _, course in sorted(
            scored,
            key=lambda item: (-item[0], item[1].name),
        )
    ]


def _get_matched_course(message: str):
    courses = (
        Course.objects
        .filter(is_active=True)
        .select_related("category")
        .order_by("order", "name")
    )

    matches = _course_matches(message, courses)

    return matches[0] if matches else None


def _get_course_from_session(message: str, session=None):
    """
    Resolve follow-up questions using the current conversation.

    Example:
        User: Tell me about the AI course.
        User: What is its duration?

    The second message can use the course mentioned in the first message.
    """

    if session is None:
        return None

    try:
        previous_messages = list(
            session.messages
            .filter(sender=ChatMessage.Sender.USER)
            .order_by("-created_at")
            .values_list("text", flat=True)[:8]
        )

        for previous_message in previous_messages:
            course = _get_matched_course(previous_message)

            if course:
                return course

        # Also try the current message together with recent user messages.
        combined = " ".join(
            reversed(previous_messages)
        )

        if combined:
            course = _get_matched_course(
                f"{combined} {message}"
            )

            if course:
                return course

    except Exception:
        logger.exception(
            "Session course resolution failed"
        )

    return None


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
                "role": (
                    "user"
                    if msg.sender == ChatMessage.Sender.USER
                    else "assistant"
                ),
                "content": msg.text,
            }
        )

    return messages


# ---------------------------------------------------------------------------
# Course knowledge retrieval
# ---------------------------------------------------------------------------

def _get_course_context(
    message: str,
    intent: str,
    matched_course=None,
) -> str:
    """
    Retrieve relevant course information directly from the Django database.

    Course database is authoritative for course-specific structured data.
    """

    if intent != "course_enquiry":
        return ""

    courses = (
        Course.objects
        .filter(is_active=True)
        .select_related("category")
        .order_by("order", "name")
    )

    if matched_course:
        matched_courses = [matched_course]

    else:
        matched_courses = _course_matches(
            message,
            courses,
        )

    # For a general course-list question, return a controlled number
    # of active courses.
    if not matched_courses and _is_course_list_request(message):
        matched_courses = list(courses[:12])

    # Do not send the entire database to the model.
    matched_courses = matched_courses[:12]

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

        certificate = (
            "Yes"
            if course.certificate_included
            else "No"
        )

        course_lines = [
            f"Course: {course.name}",
            f"Category: {category_name}",
            f"Duration: {course.duration or 'Not specified'}",
            f"Level: {course.get_level_display()}",
            f"Certificate: {certificate}",
        ]
        description = course.short_description or course.description
        if description:
            course_lines.insert(2, f"Description: {description}")
        lines.append("\n".join(course_lines))

    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# CTA
# ---------------------------------------------------------------------------

def _contact_cta(language_code: str) -> dict:
    labels = {
        "EN": "Contact / Enquire",
        "KN": "ಸಂಪರ್ಕಿಸಿ / ವಿಚಾರಿಸಿ",
        "TE": "సంప్రదించండి / విచారించండి",
    }

    return {
        "label": labels.get(
            language_code,
            labels["EN"],
        ),
        "href": "#contact",
    }


# ---------------------------------------------------------------------------
# Direct institute replies
# ---------------------------------------------------------------------------

def _institute_reply(
    language_code: str,
    message: str,
) -> str:

    text = message.lower()

    # ---------------------------------------------------------------
    # Certification
    # ---------------------------------------------------------------

    if any(
        term in text
        for term in (
            "certificate",
            "certification",
            "ಪ್ರಮಾಣಪತ್ರ",
            "ಸರ್ಟಿಫಿಕೇಟ್",
            "ಸერტಿಫಿಕೇಟ್",
            "సర్టిఫికేట్",
            "ధృవీకరణ",
        )
    ):
        return {
            "EN": (
                "Certification will be provided after completion "
                "of the course by Vidyavana Computer Educational Center."
            ),
            "KN": (
                "ವಿದ್ಯಾವನ ಕಂಪ್ಯೂಟರ್ ಎಜುಕೇಶನಲ್ ಸೆಂಟರ್‌ನಲ್ಲಿ "
                "ಕೋರ್ಸ್ ಪೂರ್ಣಗೊಳಿಸಿದ ನಂತರ ಪ್ರಮಾಣಪತ್ರವನ್ನು ನೀಡಲಾಗುತ್ತದೆ."
            ),
            "TE": (
                "విద్యావన కంప్యూటర్ ఎడ్యుకేషనల్ సెంటర్‌లో "
                "కోర్సు పూర్తయిన తర్వాత సర్టిఫికేషన్ అందించబడుతుంది."
            ),
        }[language_code]

    # ---------------------------------------------------------------
    # Eligibility
    # ---------------------------------------------------------------

    if any(
        term in text
        for term in (
            "who can join",
            "eligib",
            "ಯಾರು ಸೇರಬಹುದು",
            "ಅರ್ಹತೆ",
            "ఎవరు చేరవచ్చు",
            "అర్హత",
        )
    ):
        return {
            "EN": (
                "Vidyavana welcomes 10th pass students, students who "
                "discontinued studies, PUC, degree, ITI, diploma, B.Com, "
                "BBA/BBM, BCA and BE/B.Tech students, fresh graduates, "
                "job seekers, women restarting careers and working "
                "professionals. Beginner courses do not require prior "
                "computer knowledge."
            ),
            "KN": (
                "ವಿದ್ಯಾವನಕ್ಕೆ 10ನೇ ತರಗತಿ ಪಾಸಾದವರು, ವಿದ್ಯಾಭ್ಯಾಸವನ್ನು "
                "ನಿಲ್ಲಿಸಿದವರು, PUC, ಪದವಿ, ITI, ಡಿಪ್ಲೊಮಾ, B.Com, BBA/BBM, "
                "BCA ಮತ್ತು BE/B.Tech ವಿದ್ಯಾರ್ಥಿಗಳು, ಹೊಸ ಪದವೀಧರರು, "
                "ಉದ್ಯೋಗ ಹುಡುಕುವವರು, ವೃತ್ತಿಜೀವನ ಪುನರಾರಂಭಿಸುವ ಮಹಿಳೆಯರು "
                "ಮತ್ತು ಉದ್ಯೋಗದಲ್ಲಿರುವವರು ಸೇರಬಹುದು. ಆರಂಭಿಕ ಕೋರ್ಸ್‌ಗಳಿಗೆ "
                "ಹಿಂದಿನ ಕಂಪ್ಯೂಟರ್ ಜ್ಞಾನ ಅಗತ್ಯವಿಲ್ಲ."
            ),
            "TE": (
                "విద్యావనలో 10వ తరగతి పాస్ అయినవారు, చదువు ఆపినవారు, "
                "PUC, డిగ్రీ, ITI, డిప్లొమా, B.Com, BBA/BBM, BCA మరియు "
                "BE/B.Tech విద్యార్థులు, కొత్త గ్రాడ్యుయేట్లు, ఉద్యోగార్థులు, "
                "కెరీర్‌ను తిరిగి ప్రారంభించే మహిళలు మరియు ఉద్యోగులు "
                "చేరవచ్చు. ప్రారంభ కోర్సులకు ముందస్తు కంప్యూటర్ జ్ఞానం "
                "అవసరం లేదు."
            ),
        }[language_code]

    return {
        "EN": (
            "Vidyavana Computer Educational Center, Bellari provides "
            "practical, affordable and job-oriented computer education "
            "with hands-on training, live projects and career preparation."
        ),
        "KN": (
            "ವಿದ್ಯಾವನ ಕಂಪ್ಯೂಟರ್ ಎಜುಕೇಶನಲ್ ಸೆಂಟರ್, ಬೆಲ್ಲಾರಿ ಪ್ರಾಯೋಗಿಕ, "
            "ಕೈಗೆಟುಕುವ ಮತ್ತು ಉದ್ಯೋಗಕೇಂದ್ರಿತ ಕಂಪ್ಯೂಟರ್ ಶಿಕ್ಷಣವನ್ನು "
            "ಕೈಹಿಡಿದು ತರಬೇತಿ, ಲೈವ್ ಪ್ರಾಜೆಕ್ಟ್‌ಗಳು ಮತ್ತು ವೃತ್ತಿ "
            "ಸಿದ್ಧತೆಯೊಂದಿಗೆ ನೀಡುತ್ತದೆ."
        ),
        "TE": (
            "విద్యావన కంప్యూటర్ ఎడ్యుకేషనల్ సెంటర్, బెల్లారి ప్రాక్టికల్, "
            "అందుబాటు ధరలో మరియు ఉద్యోగోద్దేశ్య కంప్యూటర్ విద్యను "
            "హ్యాండ్స్-ఆన్ శిక్షణ, లైవ్ ప్రాజెక్టులు మరియు కెరీర్ "
            "సిద్ధతతో అందిస్తుంది."
        ),
    }[language_code]


# ---------------------------------------------------------------------------
# Course-specific structured replies
# ---------------------------------------------------------------------------

def _course_specific_reply(
    course,
    message: str,
    language_code: str,
) -> str | None:

    if not course:
        return None

    text = message.lower()

    # ---------------------------------------------------------------
    # Duration
    # ---------------------------------------------------------------

    if any(
        term in text
        for term in (
            "duration",
            "how long",
            "month",
            "months",
            "week",
            "weeks",
            "ಎಷ್ಟು ತಿಂಗಳು",
            "ಅವಧಿ",
            "ಎಷ್ಟು ದಿನ",
            "ఎంత కాలం",
            "నెలలు",
            "వ్యవధి",
        )
    ):
        duration = course.duration or None

        if not duration:
            return {
                "EN": (
                    f"The duration of the {course.name} course "
                    "is not currently available in the verified information."
                ),
                "KN": (
                    f"{course.name} ಕೋರ್ಸ್‌ನ ಅವಧಿಯ ಮಾಹಿತಿ "
                    "ಪ್ರಸ್ತುತ ಲಭ್ಯವಿಲ್ಲ."
                ),
                "TE": (
                    f"{course.name} కోర్సు వ్యవధి సమాచారం "
                    "ప్రస్తుతం అందుబాటులో లేదు."
                ),
            }[language_code]

        return {
            "EN": (
                f"The duration of the {course.name} course "
                f"is {duration}."
            ),
            "KN": (
                f"{course.name} ಕೋರ್ಸ್‌ನ ಅವಧಿ {duration}."
            ),
            "TE": (
                f"{course.name} కోర్సు వ్యవధి {duration}."
            ),
        }[language_code]

    # ---------------------------------------------------------------
    # Fee
    # ---------------------------------------------------------------

    if any(
        term in text
        for term in (
            "fee",
            "fees",
            "cost",
            "price",
            "ಶುಲ್ಕ",
            "ಫೀಸ್",
            "ವೆಚ್ಚ",
            "ಬೆಲೆ",
            "ಫీజు",
            "ఖర్చు",
            "ధర",
        )
    ):
        return {
            "EN": (
                "The current fee for this course is not currently available "
                "in the verified information. Please contact Vidyavana "
                "for the latest fee details."
            ),
            "KN": (
                "ಈ ಕೋರ್ಸ್‌ನ ಪ್ರಸ್ತುತ ಶುಲ್ಕದ ಮಾಹಿತಿ ಪರಿಶೀಲಿಸಿದ "
                "ಮಾಹಿತಿಯಲ್ಲಿ ಲಭ್ಯವಿಲ್ಲ. ಇತ್ತೀಚಿನ ಶುಲ್ಕ ವಿವರಗಳಿಗಾಗಿ "
                "ವಿದ್ಯಾವನವನ್ನು ಸಂಪರ್ಕಿಸಿ."
            ),
            "TE": (
                "ఈ కోర్సు ప్రస్తుత ఫీజు సమాచారం ధృవీకరించిన "
                "సమాచారంలో అందుబాటులో లేదు. తాజా ఫీజు వివరాల కోసం "
                "విద్యావనను సంప్రదించండి."
            ),
        }[language_code]

    # ---------------------------------------------------------------
    # Certificate
    # ---------------------------------------------------------------

    if any(
        term in text
        for term in (
            "certificate",
            "certification",
            "ಪ್ರಮಾಣಪತ್ರ",
            "ಸರ್ಟಿಫಿಕೇಟ್",
            "సర్టిఫికేట్",
        )
    ):
        if course.certificate_included:
            return {
                "EN": (
                    f"Yes. The {course.name} course includes a certificate."
                ),
                "KN": (
                    f"ಹೌದು. {course.name} ಕೋರ್ಸ್‌ನಲ್ಲಿ ಪ್ರಮಾಣಪತ್ರವನ್ನು ನೀಡಲಾಗುತ್ತದೆ."
                ),
                "TE": (
                    f"అవును. {course.name} కోర్సులో సర్టిఫికేట్ అందించబడుతుంది."
                ),
            }[language_code]

        return {
            "EN": (
                f"Certificate information for the {course.name} course "
                "is not currently available in the verified information."
            ),
            "KN": (
                f"{course.name} ಕೋರ್ಸ್‌ನ ಪ್ರಮಾಣಪತ್ರದ ಮಾಹಿತಿ "
                "ಪ್ರಸ್ತುತ ಲಭ್ಯವಿಲ್ಲ."
            ),
            "TE": (
                f"{course.name} కోర్సు సర్టిఫికేట్ సమాచారం "
                "ప్రస్తుతం అందుబాటులో లేదు."
            ),
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
You are a helpful assistant for Vidyavana Computer Educational Institute.

Your goal is to answer the user's question clearly, naturally, and accurately.

Language rules:
- Reply in {selected_language} whenever the user asks in that language or the current interface indicates it.
- Do not mix English, Kannada, and Telugu in the same response.
- Keep official course names and technical terms in their original form when appropriate.

Answering rules:
- Use the verified Vidyavana information only when it is directly relevant to the user's question.
- Use general knowledge when the question is not about the institute or when the retrieved institute context is not relevant.
- Never invent institute-specific facts such as fees, durations, placements, addresses, timings, phone numbers, certificates, or other institute details.
- If an institute detail is not available in the verified information, say so clearly and, when relevant, direct the user to the institute contact details.
- Do not copy raw retrieved text into the final answer; instead, answer the question in natural language.
- Be conversational, concise, and helpful.
- Answer the actual question instead of discussing internal process or tool use.
- Handle follow-up questions naturally when the previous context makes the meaning clear.
- Avoid repetitive refusal templates.
- Distinguish clearly between official institute information and general knowledge.

Domain rules:
- If the user asks about courses, admissions, fees, locations, timings, placement, certificate status, or institute information, use the relevant verified context when available.
- If the user asks a general question such as "What is Python?" and the institute knowledge base does not contain a relevant answer, answer from general knowledge without comparing it to institute information.
- For missing institute-specific information, say that the available information does not include it and, where appropriate, suggest contacting the institute.

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
            "KN": (
                "ನಮಸ್ಕಾರ! ನಾನು ವಿದ್ಯಾವನ ಸಹಾಯಕ. "
                "ಕೋರ್ಸ್‌ಗಳು, ತರಬೇತಿ, ಉದ್ಯೋಗಾವಕಾಶಗಳು ಮತ್ತು "
                "ಸಂಸ್ಥೆಯ ಮಾಹಿತಿಯ ಬಗ್ಗೆ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಹುದು."
            ),
            "TE": (
                "నమస్కారం! నేను విద్యావన సహాయకుడిని. "
                "కోర్సులు, శిక్షణ, ప్లేస్‌మెంట్‌లు మరియు సంస్థ "
                "సమాచారం గురించి మీకు సహాయం చేయగలను."
            ),
        }.get(
            language_code,
            "Hi! I'm the Vidyavana Assistant. I can help you with our courses, training, placements, and institute information.",
        )

    elif intent == "fee_enquiry":

        text = {
            "KN": (
                "ಪ್ರಸ್ತುತ ಕೋರ್ಸ್ ಶುಲ್ಕದ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ. "
                "ಇತ್ತೀಚಿನ ಶುಲ್ಕ ವಿವರಗಳಿಗಾಗಿ ವಿದ್ಯಾವನವನ್ನು ಸಂಪರ್ಕಿಸಿ."
            ),
            "TE": (
                "ప్రస్తుతం కోర్సు ఫీజు సమాచారం అందుబాటులో లేదు. "
                "తాజా ఫీజు వివరాల కోసం విద్యావనను సంప్రదించండి."
            ),
        }.get(
            language_code,
            "Current course fee information is not available at the moment. Please contact Vidyavana for the latest fee details.",
        )

    elif intent == "placement_enquiry":

        text = {
            "KN": (
                "ವಿದ್ಯಾವನ ಉದ್ಯೋಗಕೇಂದ್ರಿತ ತರಬೇತಿ ಮತ್ತು ವೃತ್ತಿ ಸಹಾಯವನ್ನು "
                "ನೀಡುತ್ತದೆ. ಇತ್ತೀಚಿನ ಉದ್ಯೋಗ ಮಾಹಿತಿಗಾಗಿ ಸಂಸ್ಥೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
            ),
            "TE": (
                "విద్యావన ప్లేస్‌మెంట్ ఆధారిత శిక్షణ మరియు కెరీర్ "
                "సహాయాన్ని అందిస్తుంది. తాజా ప్లేస్‌మెంట్ సమాచారం కోసం "
                "సంస్థను సంప్రదించండి."
            ),
        }.get(
            language_code,
            "Vidyavana provides placement-focused training and career support. For the latest placement information, please contact the institute.",
        )

    elif intent == "contact_enquiry":

        text = {
            "KN": (
                "ವಿದ್ಯಾವನ ಕಂಪ್ಯೂಟರ್ ಎಜುಕೇಶನಲ್ ಸೆಂಟರ್, ಬೆಲ್ಲಾರಿ: "
                "R.N. ಸ್ಟ್ರೀಟ್, ಅಮೃತ ಮೆಡಿಕಲ್ ಸ್ಟೋರ್ ಪಕ್ಕದಲ್ಲಿ, ಮಿಲ್ಲರ್‌ಪೇಟೆ, "
                "ಬೆಲ್ಲಾರಿ - 583101. ಫೋನ್: 9480070183. "
                "ಇಮೇಲ್: vidyavanably@gmail.com."
            ),
            "TE": (
                "విద్యావన కంప్యూటర్ ఎడ్యుకేషనల్ సెంటర్, బెల్లారి చిరునామా: "
                "R.N. స్ట్రీట్, అమృత మెడికల్ స్టోర్ పక్కన, మిల్లర్‌పేట్, "
                "బెల్లారి - 583101. ఫోన్: 9480070183. "
                "ఇమెయిల్: vidyavanably@gmail.com."
            ),
        }.get(
            language_code,
            "Vidyavana Computer Educational Center, Bellari is at R.N. Street, beside Amrutha Medical Store, Millerpet, Bellari - 583101. Phone: 9480070183. Email: vidyavanably@gmail.com.",
        )

    elif intent == "course_enquiry":

        matched_courses = (
            Course.objects
            .filter(is_active=True)
            .order_by("order", "name")[:12]
        )

        if matched_courses and _is_course_list_request(message):

            course_names = ", ".join(
                course.name
                for course in matched_courses
            )

            text = {
                "KN": (
                    f"ವಿದ್ಯಾವನದಲ್ಲಿ ಪ್ರಸ್ತುತ {course_names} ಮುಂತಾದ "
                    "ಕೋರ್ಸ್‌ಗಳು ಲಭ್ಯವಿವೆ. ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಕೋರ್ಸ್ "
                    "ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕೇ?"
                ),
                "TE": (
                    f"విద్యావనలో ప్రస్తుతం {course_names} వంటి "
                    "కోర్సులు అందుబాటులో ఉన్నాయి. ఏదైనా ప్రత్యేక "
                    "కోర్సు గురించి సమాచారం కావాలా?"
                ),
            }.get(
                language_code,
                f"We currently offer courses such as {course_names}. Would you like information about a particular course?",
            )

        else:

            text = {
                "KN": (
                    "ಪ್ರಸ್ತುತ ಲಭ್ಯವಿರುವ ಕೋರ್ಸ್‌ಗಳ ಮಾಹಿತಿಗಾಗಿ "
                    "ವಿದ್ಯಾವನವನ್ನು ಸಂಪರ್ಕಿಸಿ."
                ),
                "TE": (
                    "ప్రస్తుతం అందుబాటులో ఉన్న కోర్సుల సమాచారం కోసం "
                    "విద్యావనను సంప్రదించండి."
                ),
            }.get(
                language_code,
                "I can help with Vidyavana-related course and institute information. Please mention a specific course or ask about the institute.",
            )

    else:

        text = {
            "KN": (
                "ಪ್ರಸ್ತುತ ಲಭ್ಯವಿರುವ ಮಾಹಿತಿ ಮತ್ತು ಸಾಮಾನ್ಯ ವಿಷಯಗಳ ಬಗ್ಗೆ ನಾನು ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. "
                "ನಿಮಗೆ ಯಾರು, ಯಾವ ಕೋರ್ಸ್ ಅಥವಾ ಸಂಸ್ಥೆಯ ಮಾಹಿತಿ ಬೇಕು?"
            ),
            "TE": (
                "ప్రస్తుతం అందుబాటులో ఉన్న సమాచారం మరియు సాధారణ సమాచారంపై నేను సహాయం చేయగలను. "
                "మీకు ఏ కోర్సు, సంస్థ సమాచారం లేదా ఇతర వివరాలు కావాలి?"
            ),
        }.get(
            language_code,
            "I can help with the available institute information or answer general questions. What would you like to know?",
        )

    return {
        "text": text,
        "intent": intent,
        "cta": (
            _contact_cta(language_code)
            if intent in {
                "fee_enquiry",
                "contact_enquiry",
                "course_enquiry",
                "placement_enquiry",
            }
            else None
        ),
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

    Flow:
    1. Detect language.
    2. Detect intent.
    3. Resolve course from the current message or conversation history.
    4. Use Django Course database for structured course information.
    5. Use verified RAG for institute knowledge that is not structured
       in the Course database.
    6. Use Groq only when an AI-generated response is actually needed.
    7. Never invent missing institute information.
    """

    message = (message or "").strip()

    if not message:
        return _fallback_reply(
            message="",
            language_code=language_code,
            intent="general",
        )

    intent = detect_intent(message)

    # ---------------------------------------------------------------
    # Language
    # ---------------------------------------------------------------

    language_code = detect_language(
        message,
        language_code,
    )

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
    # Resolve course
    #
    # First try current message.
    # Then use previous conversation for follow-ups.
    # ---------------------------------------------------------------

    matched_course = None

    if intent == "course_enquiry" or _course_detail_requested(message):
        try:
            matched_course = _get_matched_course(message)

            if not matched_course:
                matched_course = _get_course_from_session(
                    message,
                    session=session,
                )

        except Exception:
            logger.exception(
                "Specific course lookup failed"
            )

    # ---------------------------------------------------------------
    # If a specific course is clearly resolved, treat it as a
    # course enquiry even when the current message is a follow-up.
    # ---------------------------------------------------------------

    if matched_course:
        intent = "course_enquiry"

    # ---------------------------------------------------------------
    # Retrieve verified database course information.
    # ---------------------------------------------------------------

    try:

        course_context = _get_course_context(
            message=message,
            intent=intent,
            matched_course=matched_course,
        )

    except Exception:

        logger.exception(
            "Database knowledge retrieval failed"
        )

        course_context = ""

    # ---------------------------------------------------------------
    # Direct course-specific answer.
    #
    # This happens BEFORE RAG/Groq so questions such as:
    # "What is the duration of Python?"
    # "Does AI course provide a certificate?"
    # are answered deterministically.
    # ---------------------------------------------------------------

    if matched_course and intent == "course_enquiry":

        specific_reply = _course_specific_reply(
            matched_course,
            message,
            language_code,
        )

        if specific_reply:

            logger.info(
                "Course detail answered directly from database "
                "session=%s course=%s language=%s",
                getattr(session, "uuid", None),
                matched_course.name,
                language_code,
            )

            return {
                "text": specific_reply,
                "intent": intent,
                "cta": _contact_cta(language_code),
            }

    # ---------------------------------------------------------------
    # Course list.
    #
    # Only return the course list for an actual course-list request.
    # Do not return it for questions such as:
    # "What topics are covered in AI?"
    # ---------------------------------------------------------------

    if intent == "course_enquiry" and course_context:

        if _is_course_list_request(message):

            courses = (
                Course.objects
                .filter(is_active=True)
                .select_related("category")
                .order_by("order", "name")[:12]
            )

            course_names = [
                course.name
                for course in courses
            ]

            if language_code == "KN":

                text = (
                    "ವಿದ್ಯಾವನದಲ್ಲಿ ಪ್ರಸ್ತುತ ಲಭ್ಯವಿರುವ ಕೆಲವು ಕೋರ್ಸ್‌ಗಳು:\n\n"
                    + "\n".join(
                        f"• {name}"
                        for name in course_names
                    )
                    + "\n\n"
                    "ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಕೋರ್ಸ್ ಬಗ್ಗೆ ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಬೇಕಾದರೆ ಕೇಳಬಹುದು."
                )

            elif language_code == "TE":

                text = (
                    "విద్యావనలో ప్రస్తుతం అందుబాటులో ఉన్న కొన్ని కోర్సులు:\n\n"
                    + "\n".join(
                        f"• {name}"
                        for name in course_names
                    )
                    + "\n\n"
                    "మీకు ఏదైనా ప్రత్యేక కోర్సు గురించి మరింత సమాచారం కావాలంటే అడగండి."
                )

            else:

                text = (
                    "Vidyavana currently offers courses such as:\n\n"
                    + "\n".join(
                        f"• {name}"
                        for name in course_names
                    )
                    + "\n\n"
                    "Would you like more information about a particular course?"
                )

            logger.info(
                "Course list answered directly from database "
                "session=%s language=%s",
                getattr(session, "uuid", None),
                language_code,
            )

            return {
                "text": text,
                "intent": intent,
                "cta": _contact_cta(language_code),
            }

    # ---------------------------------------------------------------
    # Simple institute enquiries.
    # ---------------------------------------------------------------

    if intent == "institute_enquiry":

        return {
            "text": _institute_reply(
                language_code,
                message,
            ),
            "intent": intent,
            "cta": _contact_cta(language_code),
        }

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

        return fallback

    # ---------------------------------------------------------------
    # RAG retrieval
    #
    # RAG is especially important for questions such as:
    # "What is the training approach?"
    # "Do you provide accommodation?"
    # "What are the benefits?"
    # "What topics are covered?"
    #
    # But retrieved information must remain verified.
    # ---------------------------------------------------------------

    rag_query = message
    if matched_course:
        category_name = (
            matched_course.category.name
            if matched_course.category
            else ""
        )
        rag_query = f"{message}\nCourse: {matched_course.name}\nCategory: {category_name}"

    try:
        rag_context = retrieve_context(rag_query)
        if rag_context and not _should_use_rag_context(message, rag_context, matched_course):
            logger.info(
                "Ignoring irrelevant RAG context for question=%r context_len=%s",
                message,
                len(rag_context),
            )
            rag_context = ""
        logger.info(
            "RAG context available=%s course=%s",
            bool(rag_context),
            getattr(matched_course, "name", None),
        )

    except Exception:

        logger.exception(
            "RAG context retrieval failed"
        )

        rag_context = ""

    verified_context = "\n\n".join(
        context
        for context in (
            rag_context,
            course_context,
        )
        if context
    )

    # ---------------------------------------------------------------
    # Groq for questions that need natural-language generation.
    # ---------------------------------------------------------------

    try:

        history = _build_history(
            session=session
        )

        system_prompt = _build_system_prompt(
            selected_language=selected_language,
        )

        text = generate_chat_completion(
            system_prompt=system_prompt,
            history=history,
            user_message=message,
            rag_context=verified_context,
        )

        # -----------------------------------------------------------
        # Protect against empty or obviously invalid responses.
        # -----------------------------------------------------------

        if not text or not text.strip():
            raise ValueError(
                "Groq returned an empty response."
            )

        logger.info(
            "Groq reply generated for session=%s intent=%s "
            "rag=%s course=%s",
            getattr(session, "uuid", None),
            intent,
            bool(rag_context),
            getattr(matched_course, "name", None),
        )

        return {
            "text": text.strip(),
            "intent": intent,
            "cta": (
                _contact_cta(language_code)
                if intent == "course_enquiry"
                else None
            ),
        }

    except Exception:

        logger.exception(
            "Groq reply generation failed; "
            "falling back to rule-based response"
        )

    # ---------------------------------------------------------------
    # Safe fallback.
    # ---------------------------------------------------------------

    return _fallback_reply(
        message=message,
        language_code=language_code,
        intent=intent,
    )