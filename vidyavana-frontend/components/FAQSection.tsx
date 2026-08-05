"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useForm } from "react-hook-form";
import { LoaderCircle, Plus } from "lucide-react";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import { getFAQs, submitFAQQuestion, type FAQItem } from "@/lib/services";

const faqQuestionSchema = z.object({
  name: z.string().trim().optional().or(z.literal("")),
  email: z.string().trim().email("Please enter a valid email address").optional().or(z.literal("")),
  question: z.string().trim().min(10, "Please enter a valid question"),
});

type FAQQuestionFormValues = z.infer<typeof faqQuestionSchema>;

const defaultValues: FAQQuestionFormValues = {
  name: "",
  email: "",
  question: "",
};

export default function FAQSection() {
  const [faqs, setFaqs] = useState<FAQItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState<number | null>(0);
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FAQQuestionFormValues>({
    resolver: zodResolver(faqQuestionSchema),
    defaultValues,
    mode: "onTouched",
  });

  useEffect(() => {
    let mounted = true;

    const fetchFAQs = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getFAQs();
        if (mounted) {
          setFaqs(data);
        }
      } catch {
        if (mounted) {
          setError("Unable to load FAQs right now.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    void fetchFAQs();

    return () => {
      mounted = false;
    };
  }, []);

  const onSubmit = async (values: FAQQuestionFormValues) => {
    if (submitting) {
      return;
    }

    setSubmitting(true);

    try {
      await submitFAQQuestion({
        name: values.name?.trim() || "",
        email: values.email?.trim() || "",
        question: values.question.trim(),
      });
      toast.success("Your question was submitted and is pending review.");
      reset(defaultValues);
    } catch {
      toast.error("Unable to submit your question right now. Please try again later.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section id="faq" className="py-24 lg:py-32 bg-section">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="grid gap-16 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="max-w-3xl">
            <div className="text-center xl:text-left">
              <span className="text-sm font-semibold uppercase tracking-wide text-primary">FAQ</span>
              <h2 className="mt-3 font-heading text-4xl font-bold text-heading">
                Frequently asked questions
              </h2>
            </div>

            {loading ? (
              <div className="mt-12 flex items-center justify-center gap-2 text-sm text-paragraph">
                <LoaderCircle size={16} className="animate-spin" />
                Loading FAQs...
              </div>
            ) : error ? (
              <div className="mt-12 rounded-xl2 border border-border bg-white px-4 py-3 text-sm text-paragraph">
                {error}
              </div>
            ) : faqs.length === 0 ? (
              <div className="mt-12 rounded-xl2 border border-border bg-white px-4 py-3 text-sm text-paragraph">
                No FAQs are available at the moment.
              </div>
            ) : (
              <div className="mt-12 space-y-3">
                {faqs.map(({ id, question, answer }, idx) => {
                  const isOpen = open === idx;
                  return (
                    <div key={id} className="rounded-xl2 border border-border bg-white overflow-hidden">
                      <button
                        onClick={() => setOpen(isOpen ? null : idx)}
                        className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                        aria-expanded={isOpen}
                      >
                        <span className="font-heading text-[15px] font-semibold text-heading">{question}</span>
                        <span
                          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-section text-heading transition-transform duration-300 ${
                            isOpen ? "rotate-45" : ""
                          }`}
                        >
                          <Plus size={16} />
                        </span>
                      </button>
                      <AnimatePresence initial={false}>
                        {isOpen && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.25, ease: "easeInOut" }}
                            className="overflow-hidden"
                          >
                            <p className="px-6 pb-5 text-sm leading-relaxed text-paragraph">{answer}</p>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-border bg-white p-8 shadow-card">
            <div className="text-center">
              <span className="text-sm font-semibold uppercase tracking-wide text-primary">Ask a question</span>
              <h3 className="mt-3 text-3xl font-bold text-heading">Can't find your answer?</h3>
              <p className="mt-3 text-sm text-paragraph">
                Submit your question below and our team will add it to the FAQ after review.
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4" noValidate>
              <label className="block text-sm font-medium text-heading">
                <span className="mb-1.5 block">Name</span>
                <input
                  {...register("name")}
                  className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="Optional"
                />
              </label>

              <label className="block text-sm font-medium text-heading">
                <span className="mb-1.5 block">Email</span>
                <input
                  type="email"
                  {...register("email")}
                  className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="Optional"
                />
                {errors.email ? <span className="mt-1 block text-xs text-red-500">{errors.email.message}</span> : null}
              </label>

              <label className="block text-sm font-medium text-heading">
                <span className="mb-1.5 block">Your Question</span>
                <textarea
                  {...register("question")}
                  rows={5}
                  className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="Type your question here"
                />
                {errors.question ? <span className="mt-1 block text-xs text-red-500">{errors.question.message}</span> : null}
              </label>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:bg-primary/70"
                >
                  {submitting ? (
                    <>
                      <LoaderCircle size={16} className="animate-spin" />
                      Sending...
                    </>
                  ) : (
                    "Submit Question"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
