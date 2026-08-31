# Code Changes - Quick Reference

## 1. Frontend: ChatbotWidget.tsx - State Addition

**Location**: Line 342  
**Change**: Added voice availability tracking state

```typescript
// NEW STATE ADDED
const [voiceAvailability, setVoiceAvailability] = useState<Record<string, boolean>>({
  EN: false,
  KN: false,
  TE: false,
});
```

**Purpose**: Track whether browser has voices available for each language

---

## 2. Frontend: ChatbotWidget.tsx - useEffect Enhancement

**Location**: Lines 360-390  
**Change**: Enhanced voice availability checking with onvoiceschanged handler

```typescript
// BEFORE
const handleVoicesChanged = () => setSpeechSupported(true);
window.speechSynthesis.onvoiceschanged = handleVoicesChanged;

// AFTER
const checkVoices = () => {
  const voices = window.speechSynthesis.getVoices();
  const availability: Record<string, boolean> = {
    EN: voices.some((v) => /^en/.test(v.lang.toLowerCase())),
    KN: voices.some((v) => /^kn/.test(v.lang.toLowerCase())),
    TE: voices.some((v) => /^te/.test(v.lang.toLowerCase())),
  };
  if (mounted) {
    setVoiceAvailability(availability);
  }
};

// Check voices immediately (some browsers have them ready)
checkVoices();

// Also check when voices are loaded (async)
const handleVoicesChanged = () => checkVoices();
window.speechSynthesis.onvoiceschanged = handleVoicesChanged;
```

**Purpose**: Track voice availability immediately and whenever voices are loaded asynchronously

---

## 3. Frontend: ChatbotWidget.tsx - getBestVoice() Improvement

**Location**: Lines 409-445  
**Change**: Added detailed logging and improved voice matching

```typescript
// BEFORE
const exactMatch = voices.find((voice) => lowerOrder.includes(voice.lang.toLowerCase()));
if (exactMatch) return exactMatch;

const prefixMatch = voices.find((voice) =>
  lowerOrder.some((value) => voice.lang.toLowerCase().startsWith(value.replace(/-.*$/, ""))),
);
if (prefixMatch) return prefixMatch;

return voices[0] ?? null;

// AFTER
// Exact match: prefer the most specific regional locale
for (const prefLang of order) {
  const exact = voices.find((voice) => voice.lang.toLowerCase() === prefLang);
  if (exact) {
    console.log(`Found exact voice match for ${normalized}: ${exact.lang} - ${exact.name}`);
    return exact;
  }
}

// Prefix match: accept any voice starting with the language code
for (const prefLang of order) {
  const prefix = voices.find((voice) => voice.lang.toLowerCase().startsWith(prefLang.split("-")[0]));
  if (prefix) {
    console.log(`Found prefix match for ${normalized}: ${prefix.lang} - ${prefix.name}`);
    return prefix;
  }
}

console.warn(`No voice found for language ${normalized}. Available: ${voices.map((v) => `${v.lang}/${v.name}`).join(", ")}`);
return null;
```

**Purpose**: Better debugging, explicit order precedence, better fallback handling

---

## 4. Frontend: ChatbotWidget.tsx - speakBotResponse() Enhancement

**Location**: Lines 468-500  
**Change**: Added voice availability check and user feedback

```typescript
// NEW CHECK ADDED
const normalized = (languageCode || "EN").toUpperCase();

if (speakingMessageId === messageId) {
  stopSpeech();
  return;
}

window.speechSynthesis.cancel();

// Check if this language has voice support
if (!voiceAvailability[normalized as keyof typeof voiceAvailability]) {
  const languageName = { EN: "English", KN: "Kannada", TE: "Telugu" }[normalized] || normalized;
  setError(`${languageName} voice is not available in this browser/device. Text response is shown instead.`);
  console.warn(`${languageName} voice unavailable. Available languages: ${Object.entries(voiceAvailability).filter(([_, v]) => v).map(([k]) => k).join(", ")}`);
  return;
}

const utterance = new SpeechSynthesisUtterance(text);
const voice = getBestVoice(languageCode);

if (voice) {
  utterance.voice = voice;
  console.log(`Speaking with voice: ${voice.lang} - ${voice.name}`);
} else {
  console.warn(`No suitable voice found for ${languageCode}`);
}
```

**Purpose**: Graceful handling when voices unavailable, clear user messaging, detailed logging

---

## 5. Frontend: ChatbotWidget.tsx - startRecording() FormData Fix

**Location**: Line 592  
**Change**: Removed manual Content-Type header from FormData POST

```typescript
// BEFORE (BROKEN)
const response = await api.post("/chatbot/transcribe/", formData, {
  headers: { "Content-Type": "multipart/form-data" },
});

// AFTER (CORRECT)
// IMPORTANT: Do NOT manually set Content-Type header for FormData.
// Axios will automatically set it with the correct boundary parameter.
const response = await api.post("/chatbot/transcribe/", formData);
```

**Purpose**: 🔴 FIX FOR 400 BAD REQUEST ERROR

**Why This Matters**:
- Manually setting `Content-Type: multipart/form-data` without boundary breaks axios
- Axios needs full header: `multipart/form-data; boundary=----abc123...`
- Without boundary, Django can't parse the multipart data
- Results in 400 Bad Request

---

## 6. Frontend: ChatbotWidget.tsx - Error Handling Enhancement

**Location**: Lines 600-620  
**Change**: Improved error handling with type-specific messages

```typescript
// BEFORE (GENERIC)
catch (error) {
  console.error("Speech transcription failed:", error);
  setError("Sorry, I couldn't understand the audio. Please try again.");
}

// AFTER (SPECIFIC)
catch (error: any) {
  console.error("Speech transcription failed:", error);
  if (error.response?.status === 400) {
    console.error("Bad request:", error.response.data);
    setError(error.response.data?.error || "Audio validation failed. Please try again.");
  } else if (error.response?.status === 500) {
    setError("Server error during transcription. Please try again.");
  } else {
    setError("Network error or server unavailable. Please try again.");
  }
}
```

**Purpose**: Better debugging, user-friendly error messages, logging of bad requests

---

## 7. Backend: views.py - ChatTranscribeView Logging

**Location**: Lines 178-236  
**Change**: Added comprehensive debugging logging

```python
# NEW LOGGING ADDED AT START
logger.info(
    "ChatTranscribeView.post called. "
    f"request.FILES keys: {list(request.FILES.keys())}, "
    f"request.POST keys: {list(request.POST.keys())}, "
    f"request.data: {dict(request.data)}"
)

# DETAILED LOGGING FOR EACH VALIDATION STEP
logger.info(
    f"Audio file received. name={audio_file.name}, "
    f"size={audio_file.size}, "
    f"content_type={audio_file.content_type}"
)

logger.info(f"Language code: {language_code}")

# SUCCESS LOGGING
logger.info(f"Transcription success. text={text[:50]}..., language={language_code}")

# ERROR LOGGING WITH CONTEXT
logger.warning(
    f"Unsupported MIME type: {audio_file.content_type}. "
    f"Supported: {supported}"
)
```

**Purpose**: Enable debugging of 400 errors by capturing exact request state

**What's Logged** (No Audio Content):
- ✅ File keys present
- ✅ File name
- ✅ File size
- ✅ MIME type
- ✅ Language code
- ✅ Validation failures with reasons
- ✅ First 50 chars of transcribed text
- ❌ NO Audio bytes/content
- ❌ NO Sensitive data

---

## 8. Backend: groq_service.py - No Changes (Already Correct)

**Location**: Line 86  
**Current Code**:
```python
language=(language_code or "en").lower()
```

**Status**: Already handles uppercase to lowercase conversion correctly
- Frontend sends: EN, KN, TE
- Backend converts to: en, kn, te
- Groq Whisper API accepts: en, kn, te
- No changes needed ✅

---

## Summary of Changes by File

| File | Changes | Lines | Purpose |
|------|---------|-------|---------|
| ChatbotWidget.tsx | State addition | 342 | Track voice availability |
| ChatbotWidget.tsx | useEffect enhancement | 360-390 | Monitor voice loading |
| ChatbotWidget.tsx | getBestVoice() improvement | 409-445 | Better voice matching + logging |
| ChatbotWidget.tsx | speakBotResponse() enhancement | 468-500 | Check availability + user feedback |
| ChatbotWidget.tsx | FormData fix (CRITICAL) | 592 | FIX 400 error |
| ChatbotWidget.tsx | Error handling | 600-620 | Better error messages |
| views.py | Logging addition | 178-236 | Enable debugging |
| groq_service.py | No changes | - | Already correct |

---

## Test Commands

### Frontend
```bash
# Build to check for TypeScript errors
npm run build

# Build and serve locally
npm run dev
```

### Backend
```bash
# Check Django setup
python manage.py check

# Run chatbot tests
python manage.py test apps.chatbot

# Run development server with logging
python manage.py runserver
```

### Manual Testing
1. Open http://localhost:3000 in browser
2. Open DevTools → Console
3. Test microphone with English language
4. Should see logs: "Sending audio transcription request..."
5. Should NOT see 400 error

---

## Code Review Checklist

- ✅ All changes are backward compatible
- ✅ No breaking changes to API
- ✅ No database migrations needed
- ✅ No new dependencies added
- ✅ Error handling is improved
- ✅ Logging doesn't expose sensitive data
- ✅ Console logs are helpful for debugging
- ✅ User-facing messages are clear
- ✅ Commented critical code sections
- ✅ Maintains existing code style

