// "use client";

// import { useEffect, useMemo, useRef, useState } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import { MessageCircle, X, Mic, Send, Sparkles, LoaderCircle } from "lucide-react";
// import { getLanguages, sendChatbotMessage, type LanguageOption } from "@/lib/services";

// const DEFAULT_LANGS = ["EN", "KN", "TE"] as const;

// const LANGUAGE_LOCALES: Record<string, string> = {
//   EN: "en-US",
//   KN: "kn-IN",
//   TE: "te-IN",
// };

// type ChatMessage = {
//   from: "bot" | "user";
//   text: string;
// };

// const INITIAL_MESSAGES: ChatMessage[] = [
//   { from: "bot", text: "Hi! I'm the Vidyavana Assistant. Ask me about courses, batch timings, or admissions." },
// ];

// export default function ChatbotWidget() {
//   const [open, setOpen] = useState(false);
//   const [lang, setLang] = useState<string>("EN");
//   const [input, setInput] = useState("");
//   const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
//   const [sessionUuid, setSessionUuid] = useState<string | null>(null);
//   const [languages, setLanguages] = useState<LanguageOption[]>([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState<string | null>(null);
//   const [recognizing, setRecognizing] = useState(false);
//   const recognitionRef = useRef<any>(null);
//   const [speechSupported, setSpeechSupported] = useState(false);

//   useEffect(() => {
//     let mounted = true;

//     const fetchLanguages = async () => {
//       try {
//         const data = await getLanguages();
//         if (mounted) {
//           setLanguages(data.filter((item) => item.is_active));
//           const defaultOption = data.find((item) => item.is_default || item.code === "EN");
//           if (defaultOption) {
//             setLang(defaultOption.code);
//           }
//         }
//       } catch {
//         if (mounted) {
//           setLanguages([]);
//         }
//       }
//     };

//     void fetchLanguages();

//     const SpeechRecognition =
//       (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

//     if (SpeechRecognition) {
//       recognitionRef.current = new SpeechRecognition();
//       recognitionRef.current.continuous = false;
//       recognitionRef.current.interimResults = false;
//       recognitionRef.current.onresult = (event: any) => {
//         const transcript = event.results?.[0]?.[0]?.transcript?.trim();
//         if (transcript) {
//           void sendMessage(transcript);
//         }
//       };
//       recognitionRef.current.onend = () => {
//         setRecognizing(false);
//       };
//       recognitionRef.current.onerror = () => {
//         setRecognizing(false);
//       };
//       setSpeechSupported(true);
//     }

//     return () => {
//       mounted = false;
//       recognitionRef.current?.stop?.();
//     };
//   }, []);

//   const languageOptions = useMemo(() => {
//     if (languages.length > 0) {
//       return languages.map((language) => language.code);
//     }

//     return [...DEFAULT_LANGS];
//   }, [languages]);

//   const getLocale = (code: string) => {
//     return LANGUAGE_LOCALES[code] || code.toLowerCase();
//   };

//   const speakText = (text: string) => {
//     if (!window.speechSynthesis) {
//       return;
//     }

//     const utterance = new SpeechSynthesisUtterance(text);
//     utterance.lang = getLocale(lang);
//     window.speechSynthesis.speak(utterance);
//   };

//   const sendMessage = async (messageText: string) => {
//     const trimmed = messageText.trim();
//     if (!trimmed || loading) {
//       return;
//     }

//     setLoading(true);
//     setError(null);
//     setMessages((current) => [...current, { from: "user", text: trimmed }]);
//     setInput("");

//     try {
//       const payload = await sendChatbotMessage({
//         session_uuid: sessionUuid,
//         message: trimmed,
//         language_code: lang,
//         visitor_name: "Website Visitor",
//       });

//       if (payload?.session_uuid) {
//         setSessionUuid(payload.session_uuid);
//       }

//       const botText = payload?.bot_message?.text;
//       if (botText) {
//         setMessages((current) => [...current, { from: "bot", text: botText }]);
//         speakText(botText);
//       } else {
//         setError("The assistant did not return a response. Please try again.");
//       }
//     } catch {
//       setError("The assistant is temporarily unavailable. Please try again in a moment.");
//       setMessages((current) => [...current, { from: "bot", text: "The assistant is temporarily unavailable. Please try again in a moment." }]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleSend = async () => {
//     await sendMessage(input);
//   };

//   return (
//     <div className="fixed bottom-5 right-5 lg:bottom-8 lg:right-8 z-[60]">
//       <AnimatePresence>
//         {open && (
//           <motion.div
//             initial={{ opacity: 0, y: 16, scale: 0.96 }}
//             animate={{ opacity: 1, y: 0, scale: 1 }}
//             exit={{ opacity: 0, y: 16, scale: 0.96 }}
//             transition={{ duration: 0.2, ease: "easeOut" }}
//             className="mb-4 w-[92vw] max-w-sm rounded-xl2 border border-border bg-white shadow-softHover overflow-hidden"
//           >
//             <div className="flex items-center justify-between bg-primary px-5 py-4">
//               <div className="flex items-center gap-2.5">
//                 <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15 text-white">
//                   <Sparkles size={16} />
//                 </span>
//                 <div>
//                   <div className="text-sm font-semibold text-white leading-none">Vidyavana Assistant</div>
//                   <div className="mt-1 flex items-center gap-1.5 text-[11px] text-white/75">
//                     <span className="h-1.5 w-1.5 rounded-full bg-success" />
//                     Online
//                   </div>
//                 </div>
//               </div>
//               <button
//                 onClick={() => setOpen(false)}
//                 aria-label="Close chat"
//                 className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 hover:bg-white/15 hover:text-white transition-colors"
//               >
//                 <X size={17} />
//               </button>
//             </div>

//             <div className="flex items-center gap-2 border-b border-border px-5 py-2.5">
//               {languageOptions.map((code) => (
//                 <button
//                   key={code}
//                   onClick={() => setLang(code)}
//                   className={`rounded-full px-3 py-1 text-xs font-semibold transition-colors ${
//                     code === lang
//                       ? "bg-primary text-white"
//                       : "bg-section text-paragraph hover:text-primary"
//                   }`}
//                 >
//                   {code}
//                 </button>
//               ))}
//             </div>

//             <div className="max-h-80 overflow-y-auto px-5 py-4 space-y-3">
//               {messages.map((m, i) =>
//                 m.from === "bot" ? (
//                   <div
//                     key={`${m.from}-${i}`}
//                     className="max-w-[85%] rounded-xl2 rounded-tl-sm bg-section px-4 py-2.5 text-sm text-paragraph"
//                   >
//                     {m.text}
//                   </div>
//                 ) : (
//                   <div
//                     key={`${m.from}-${i}`}
//                     className="ml-auto max-w-[85%] rounded-xl2 rounded-tr-sm bg-primary px-4 py-2.5 text-sm text-white"
//                   >
//                     {m.text}
//                   </div>
//                 )
//               )}
//               {error ? <div className="text-xs text-red-500">{error}</div> : null}
//             </div>

//             <div className="flex items-center gap-2 border-t border-border p-3">
//               <input
//                 value={input}
//                 onChange={(e) => setInput(e.target.value)}
//                 onKeyDown={(e) => {
//                   if (e.key === "Enter") {
//                     void handleSend();
//                   }
//                 }}
//                 type="text"
//                 placeholder="Type your question…"
//                 className="flex-1 rounded-full border border-border bg-white px-4 py-2.5 text-sm text-heading placeholder:text-paragraph/40 focus:border-primary transition-colors"
//               />
//               <button
//                 type="button"
//                 aria-label={recognizing ? "Stop voice input" : "Start voice input"}
//                 onClick={() => {
//                   if (!speechSupported) {
//                     return;
//                   }
//                   if (recognizing) {
//                     recognitionRef.current?.stop?.();
//                   } else {
//                     try {
//                       recognitionRef.current?.start?.();
//                       setRecognizing(true);
//                     } catch {
//                       setRecognizing(false);
//                     }
//                   }
//                 }}
//                 className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-border text-paragraph hover:border-primary hover:text-primary transition-colors"
//               >
//                 <Mic size={16} />
//               </button>
//               <button
//                 aria-label="Send message"
//                 disabled={loading}
//                 onClick={() => void handleSend()}
//                 className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-white hover:bg-primary-hover transition-colors disabled:cursor-not-allowed disabled:bg-primary/70"
//               >
//                 {loading ? <LoaderCircle size={16} className="animate-spin" /> : <Send size={16} />}
//               </button>
//             </div>
//           </motion.div>
//         )}
//       </AnimatePresence>

//       <motion.button
//         onClick={() => setOpen((o) => !o)}
//         whileHover={{ scale: 1.06 }}
//         whileTap={{ scale: 0.96 }}
//         aria-label={open ? "Close AI assistant" : "Open AI assistant"}
//         className="flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-softHover hover:bg-primary-hover transition-colors duration-200"
//       >
//         <AnimatePresence mode="wait" initial={false}>
//           <motion.span
//             key={open ? "close" : "open"}
//             initial={{ opacity: 0, rotate: -45 }}
//             animate={{ opacity: 1, rotate: 0 }}
//             exit={{ opacity: 0, rotate: 45 }}
//             transition={{ duration: 0.15 }}
//           >
//             {open ? <X size={22} /> : <MessageCircle size={22} />}
//           </motion.span>
//         </AnimatePresence>
//       </motion.button>
//     </div>
//   );
// }



"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  LoaderCircle,
  MessageCircle,
  Mic,
  Pause,
  Send,
  Sparkles,
  Volume2,
  X,
} from "lucide-react";

import { api } from "@/lib/api";
import { getLanguages, sendChatbotMessage, type LanguageOption } from "@/lib/services";

const DEFAULT_LANGS = ["EN", "KN", "TE"] as const;

type ChatMessage = {
  id: string;
  from: "bot" | "user";
  text: string;
};

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: "welcome",
    from: "bot",
    text: "Hi! I'm the Vidyavana Assistant. Ask me about courses, batch timings, or admissions.",
  },
];

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [lang, setLang] = useState<string>("EN");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [sessionUuid, setSessionUuid] = useState<string | null>(null);
  const [languages, setLanguages] = useState<LanguageOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recognizing, setRecognizing] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const [voiceAvailability, setVoiceAvailability] = useState<Record<string, boolean>>({
    EN: false,
    KN: false,
    TE: false,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const pendingRequestsRef = useRef(0);

  useEffect(() => {
    let mounted = true;

    const fetchLanguages = async () => {
      try {
        const data = await getLanguages();
        if (!mounted) return;
        setLanguages(data.filter((item) => item.is_active));
        const defaultOption = data.find((item) => item.is_default || item.code === "EN");
        if (defaultOption) {
          setLang(defaultOption.code);
        }
      } catch {
        if (mounted) {
          setLanguages([]);
        }
      }
    };

    void fetchLanguages();

    // Initialize Speech Synthesis and check voice availability
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      setSpeechSupported(true);
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
    }

    if (typeof navigator !== "undefined" && navigator.mediaDevices && window.MediaRecorder) {
      setSpeechSupported(true);
    }

    return () => {
      mounted = false;
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      mediaRecorderRef.current?.stop();
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const languageOptions = useMemo(() => {
    if (languages.length > 0) return languages.map((language) => language.code);
    return [...DEFAULT_LANGS];
  }, [languages]);

  const getBestVoice = (languageCode: string): SpeechSynthesisVoice | null => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return null;

    const normalized = (languageCode || "EN").toUpperCase();
    const preferences: Record<string, string[]> = {
      EN: ["en-in", "en-us", "en-gb", "en"],
      KN: ["kn-in", "kn"],
      TE: ["te-in", "te"],
    };

    const order = preferences[normalized] ?? [normalized.toLowerCase()];
    const voices = window.speechSynthesis.getVoices();
    if (!voices.length) {
      console.warn("No voices available from browser speechSynthesis");
      return null;
    }

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
  };

  const stopSpeech = () => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setSpeakingMessageId(null);
    }
  };

  const speakBotResponse = (messageId: string, text: string, languageCode: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

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

    utterance.lang = normalized === "KN" ? "kn-IN" : normalized === "TE" ? "te-IN" : "en-IN";
    utterance.onstart = () => setSpeakingMessageId(messageId);
    utterance.onend = () => setSpeakingMessageId((current) => (current === messageId ? null : current));
    utterance.onerror = (event) => {
      console.error(`Speech synthesis error: ${event.error}`);
      setSpeakingMessageId((current) => (current === messageId ? null : current));
    };

    window.speechSynthesis.speak(utterance);
  };

  const sendMessage = async (messageText: string) => {
    const trimmed = messageText.trim();
    if (!trimmed || loading) return;

    setMessages((current) => [...current, { id: `user-${Date.now()}-${Math.random()}`, from: "user", text: trimmed }]);
    setInput("");
    setError(null);
    setLoading(true);
    pendingRequestsRef.current += 1;

    try {
      const payload = await sendChatbotMessage({
        session_uuid: sessionUuid,
        message: trimmed,
        language_code: lang,
        visitor_name: "Website Visitor",
      });

      if (payload?.session_uuid) {
        setSessionUuid(payload.session_uuid);
      }

      const botText = payload?.bot_message?.text;
      if (!botText) {
        setError("The assistant did not return a response. Please try again.");
        return;
      }

      const messageId = `bot-${Date.now()}-${Math.random()}`;
      setMessages((current) => [...current, { id: messageId, from: "bot", text: botText }]);
      speakBotResponse(messageId, botText, lang);
    } catch (error) {
      console.error("Chatbot request failed:", error);
      setError("The assistant is temporarily unavailable. Please try again in a moment.");
      setMessages((current) => [
        ...current,
        {
          id: `bot-error-${Date.now()}-${Math.random()}`,
          from: "bot",
          text: "The assistant is temporarily unavailable. Please try again in a moment.",
        },
      ]);
    } finally {
      pendingRequestsRef.current -= 1;
      setLoading(pendingRequestsRef.current > 0);
    }
  };

  const handleSend = async () => {
    await sendMessage(input);
  };

  const startRecording = async () => {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      setError("Voice input is not supported in this browser.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : MediaRecorder.isTypeSupported("audio/mp4")
          ? "audio/mp4"
          : "audio/wav";
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      recorder.onstop = async () => {
        const actualMimeType = recorder.mimeType || "audio/webm";

const blob = new Blob(audioChunksRef.current, {
  type: actualMimeType,
});
        if (!blob.size) {
          setError("No audio was recorded. Please try again.");
          setTranscribing(false);
          return;
        }

        setTranscribing(true);
        const formData = new FormData();
       const extension =
  actualMimeType.includes("mp4")
    ? "mp4"
    : actualMimeType.includes("wav")
      ? "wav"
      : "webm";

formData.append(
  "audio",
  blob,
  `voice-${Date.now()}.${extension}`
);
        formData.append("language_code", lang);

        try {
          console.log(`Sending audio transcription request. Language: ${lang}, Blob size: ${blob.size}`);
          // IMPORTANT: Do NOT manually set Content-Type header for FormData.
          // Axios will automatically set it with the correct boundary parameter.
          const response = await api.post("/chatbot/transcribe/", formData);
          console.log("Transcription response:", response.data);

          const success = response.data?.success;
          const transcript = response.data?.data?.text || response.data?.text;
          if (success && transcript) {
            console.log(`Transcription successful: ${transcript}`);
            setInput(transcript);
            await sendMessage(transcript);
          } else {
            const errorMsg = response.data?.error || "Sorry, I couldn't understand the audio. Please try again.";
            console.warn(`Transcription failed: ${errorMsg}`);
            setError(errorMsg);
          }
        } catch (error: any) {
          console.error("Speech transcription failed:", error);
          if (error.response?.status === 400) {
            console.error("Bad request:", error.response.data);
            setError(error.response.data?.error || "Audio validation failed. Please try again.");
          } else if (error.response?.status === 500) {
            setError("Server error during transcription. Please try again.");
          } else {
            setError("Network error or server unavailable. Please try again.");
          }
        } finally {
          setTranscribing(false);
          setRecognizing(false);
          streamRef.current?.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }
      };

      recorder.start();
      setRecognizing(true);
    } catch {
      setError("Microphone access was denied. Please allow microphone access and try again.");
      setRecognizing(false);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecognizing(false);
  };

  return (
    <div className="fixed bottom-5 right-5 lg:bottom-8 lg:right-8 z-[60]">
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.96 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="mb-4 w-[92vw] max-w-sm overflow-hidden rounded-xl2 border border-border bg-white shadow-softHover"
          >
            <div className="flex items-center justify-between bg-primary px-5 py-4">
              <div className="flex items-center gap-2.5">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15 text-white">
                  <Sparkles size={16} />
                </span>
                <div>
                  <div className="text-sm font-semibold leading-none text-white">Vidyavana Assistant</div>
                  <div className="mt-1 flex items-center gap-1.5 text-[11px] text-white/75">
                    <span className="h-1.5 w-1.5 rounded-full bg-success" />
                    Online
                  </div>
                </div>
              </div>
              <button
                onClick={() => setOpen(false)}
                aria-label="Close chat"
                className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 transition-colors hover:bg-white/15 hover:text-white"
              >
                <X size={17} />
              </button>
            </div>

            <div className="flex items-center gap-2 border-b border-border px-5 py-2.5">
              {languageOptions.map((code) => (
                <button
                  key={code}
                  onClick={() => setLang(code)}
                  className={`rounded-full px-3 py-1 text-xs font-semibold transition-colors ${
                    code === lang ? "bg-primary text-white" : "bg-section text-paragraph hover:text-primary"
                  }`}
                >
                  {code}
                </button>
              ))}
            </div>

            <div className="max-h-80 space-y-3 overflow-y-auto px-5 py-4">
              {messages.map((message) =>
                message.from === "bot" ? (
                  <div key={message.id} className="max-w-[85%] rounded-xl2 rounded-tl-sm bg-section px-4 py-2.5 text-sm text-paragraph">
                    {message.text}
                    <div className="mt-2 border-t border-border/60 pt-2">
                      {speakingMessageId === message.id ? (
                        <button
                          type="button"
                          onClick={() => stopSpeech()}
                          className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:text-primary-hover"
                          aria-label="Stop assistant audio"
                        >
                          <Pause size={12} /> Stop
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => speakBotResponse(message.id, message.text, lang)}
                          className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:text-primary-hover"
                          aria-label="Play assistant audio"
                        >
                          <Volume2 size={13} /> Play
                        </button>
                      )}
                    </div>
                  </div>
                ) : (
                  <div key={message.id} className="ml-auto max-w-[85%] rounded-xl2 rounded-tr-sm bg-primary px-4 py-2.5 text-sm text-white">
                    {message.text}
                  </div>
                ),
              )}

              {loading && (
                <div className="max-w-[85%] rounded-xl2 rounded-tl-sm bg-section px-4 py-2.5 text-sm text-paragraph">
                  <div className="flex items-center gap-2">
                    <LoaderCircle size={14} className="animate-spin" />
                    <span>Thinking...</span>
                  </div>
                </div>
              )}

              {transcribing && (
                <div className="max-w-[85%] rounded-xl2 rounded-tl-sm bg-section px-4 py-2.5 text-sm text-paragraph">
                  <div className="flex items-center gap-2">
                    <LoaderCircle size={14} className="animate-spin" />
                    <span>Transcribing...</span>
                  </div>
                </div>
              )}

              {error ? <div className="text-xs text-red-500">{error}</div> : null}
            </div>

            <div className="flex items-center gap-2 border-t border-border p-3">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    void handleSend();
                  }
                }}
                type="text"
                placeholder="Type your question…"
                className="flex-1 rounded-full border border-border bg-white px-4 py-2.5 text-sm text-heading placeholder:text-paragraph/40 transition-colors focus:border-primary"
              />

              <button
                type="button"
                aria-label={recognizing ? "Stop voice input" : transcribing ? "Transcribing voice" : "Start voice input"}
                onClick={() => {
                  if (!speechSupported) {
                    setError("Speech input is unavailable in this browser.");
                    return;
                  }
                  if (recognizing) {
                    stopRecording();
                  } else {
                    void startRecording();
                  }
                }}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-border text-paragraph transition-colors hover:border-primary hover:text-primary"
              >
                {transcribing ? <LoaderCircle size={16} className="animate-spin" /> : <Mic size={16} />}
              </button>

              <button
                aria-label="Send message"
                disabled={loading}
                onClick={() => void handleSend()}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-white transition-colors hover:bg-primary-hover disabled:cursor-not-allowed disabled:bg-primary/70"
              >
                {loading ? <LoaderCircle size={16} className="animate-spin" /> : <Send size={16} />}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        onClick={() => setOpen((current) => !current)}
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.96 }}
        aria-label={open ? "Close AI assistant" : "Open AI assistant"}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-softHover transition-colors duration-200 hover:bg-primary-hover"
      >
        <AnimatePresence mode="wait" initial={false}>
          <motion.span
            key={open ? "close" : "open"}
            initial={{ opacity: 0, rotate: -45 }}
            animate={{ opacity: 1, rotate: 0 }}
            exit={{ opacity: 0, rotate: 45 }}
            transition={{ duration: 0.15 }}
          >
            {open ? <X size={22} /> : <MessageCircle size={22} />}
          </motion.span>
        </AnimatePresence>
      </motion.button>
    </div>
  );
}
