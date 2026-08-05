"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Mic, Send, Sparkles, LoaderCircle } from "lucide-react";
import { getLanguages, sendChatbotMessage, type LanguageOption } from "@/lib/services";

const DEFAULT_LANGS = ["EN", "KN", "TE"] as const;

const LANGUAGE_LOCALES: Record<string, string> = {
  EN: "en-US",
  KN: "kn-IN",
  TE: "te-IN",
};

type ChatMessage = {
  from: "bot" | "user";
  text: string;
};

const INITIAL_MESSAGES: ChatMessage[] = [
  { from: "bot", text: "Hi! I'm the Vidyavana Assistant. Ask me about courses, batch timings, or admissions." },
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
  const recognitionRef = useRef<any>(null);
  const [speechSupported, setSpeechSupported] = useState(false);

  useEffect(() => {
    let mounted = true;

    const fetchLanguages = async () => {
      try {
        const data = await getLanguages();
        if (mounted) {
          setLanguages(data.filter((item) => item.is_active));
          const defaultOption = data.find((item) => item.is_default || item.code === "EN");
          if (defaultOption) {
            setLang(defaultOption.code);
          }
        }
      } catch {
        if (mounted) {
          setLanguages([]);
        }
      }
    };

    void fetchLanguages();

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results?.[0]?.[0]?.transcript?.trim();
        if (transcript) {
          void sendMessage(transcript);
        }
      };
      recognitionRef.current.onend = () => {
        setRecognizing(false);
      };
      recognitionRef.current.onerror = () => {
        setRecognizing(false);
      };
      setSpeechSupported(true);
    }

    return () => {
      mounted = false;
      recognitionRef.current?.stop?.();
    };
  }, []);

  const languageOptions = useMemo(() => {
    if (languages.length > 0) {
      return languages.map((language) => language.code);
    }

    return [...DEFAULT_LANGS];
  }, [languages]);

  const getLocale = (code: string) => {
    return LANGUAGE_LOCALES[code] || code.toLowerCase();
  };

  const speakText = (text: string) => {
    if (!window.speechSynthesis) {
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = getLocale(lang);
    window.speechSynthesis.speak(utterance);
  };

  const sendMessage = async (messageText: string) => {
    const trimmed = messageText.trim();
    if (!trimmed || loading) {
      return;
    }

    setLoading(true);
    setError(null);
    setMessages((current) => [...current, { from: "user", text: trimmed }]);
    setInput("");

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
      if (botText) {
        setMessages((current) => [...current, { from: "bot", text: botText }]);
        speakText(botText);
      } else {
        setError("The assistant did not return a response. Please try again.");
      }
    } catch {
      setError("The assistant is temporarily unavailable. Please try again in a moment.");
      setMessages((current) => [...current, { from: "bot", text: "The assistant is temporarily unavailable. Please try again in a moment." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    await sendMessage(input);
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
            className="mb-4 w-[92vw] max-w-sm rounded-xl2 border border-border bg-white shadow-softHover overflow-hidden"
          >
            <div className="flex items-center justify-between bg-primary px-5 py-4">
              <div className="flex items-center gap-2.5">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15 text-white">
                  <Sparkles size={16} />
                </span>
                <div>
                  <div className="text-sm font-semibold text-white leading-none">Vidyavana Assistant</div>
                  <div className="mt-1 flex items-center gap-1.5 text-[11px] text-white/75">
                    <span className="h-1.5 w-1.5 rounded-full bg-success" />
                    Online
                  </div>
                </div>
              </div>
              <button
                onClick={() => setOpen(false)}
                aria-label="Close chat"
                className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 hover:bg-white/15 hover:text-white transition-colors"
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
                    code === lang
                      ? "bg-primary text-white"
                      : "bg-section text-paragraph hover:text-primary"
                  }`}
                >
                  {code}
                </button>
              ))}
            </div>

            <div className="max-h-80 overflow-y-auto px-5 py-4 space-y-3">
              {messages.map((m, i) =>
                m.from === "bot" ? (
                  <div
                    key={`${m.from}-${i}`}
                    className="max-w-[85%] rounded-xl2 rounded-tl-sm bg-section px-4 py-2.5 text-sm text-paragraph"
                  >
                    {m.text}
                  </div>
                ) : (
                  <div
                    key={`${m.from}-${i}`}
                    className="ml-auto max-w-[85%] rounded-xl2 rounded-tr-sm bg-primary px-4 py-2.5 text-sm text-white"
                  >
                    {m.text}
                  </div>
                )
              )}
              {error ? <div className="text-xs text-red-500">{error}</div> : null}
            </div>

            <div className="flex items-center gap-2 border-t border-border p-3">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    void handleSend();
                  }
                }}
                type="text"
                placeholder="Type your question…"
                className="flex-1 rounded-full border border-border bg-white px-4 py-2.5 text-sm text-heading placeholder:text-paragraph/40 focus:border-primary transition-colors"
              />
              <button
                type="button"
                aria-label={recognizing ? "Stop voice input" : "Start voice input"}
                onClick={() => {
                  if (!speechSupported) {
                    return;
                  }
                  if (recognizing) {
                    recognitionRef.current?.stop?.();
                  } else {
                    try {
                      recognitionRef.current?.start?.();
                      setRecognizing(true);
                    } catch {
                      setRecognizing(false);
                    }
                  }
                }}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-border text-paragraph hover:border-primary hover:text-primary transition-colors"
              >
                <Mic size={16} />
              </button>
              <button
                aria-label="Send message"
                disabled={loading}
                onClick={() => void handleSend()}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-white hover:bg-primary-hover transition-colors disabled:cursor-not-allowed disabled:bg-primary/70"
              >
                {loading ? <LoaderCircle size={16} className="animate-spin" /> : <Send size={16} />}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        onClick={() => setOpen((o) => !o)}
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.96 }}
        aria-label={open ? "Close AI assistant" : "Open AI assistant"}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-softHover hover:bg-primary-hover transition-colors duration-200"
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
