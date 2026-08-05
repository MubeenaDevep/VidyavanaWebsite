"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { LoaderCircle, Star, User } from "lucide-react";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import { getReviews, submitReview, type Review } from "@/lib/services";

const reviewSchema = z.object({
  name: z.string().trim().min(2, "Name must be at least 2 characters"),
  email: z.string().trim().email("Please enter a valid email address").optional().or(z.literal("")),
  rating: z.number().min(1, "Please select a rating").max(5),
  title: z.string().trim().optional().or(z.literal("")),
  message: z.string().trim().min(10, "Review message must be at least 10 characters"),
});

type ReviewFormValues = z.infer<typeof reviewSchema>;

const defaultValues: ReviewFormValues = {
  name: "",
  email: "",
  rating: 5,
  title: "",
  message: "",
};

export default function ReviewSection() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ReviewFormValues>({
    resolver: zodResolver(reviewSchema),
    defaultValues,
    mode: "onTouched",
  });

  useEffect(() => {
    let mounted = true;

    const fetchReviews = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getReviews();
        if (mounted) {
          setReviews(data);
        }
      } catch {
        if (mounted) {
          setError("Unable to load reviews right now.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    void fetchReviews();

    return () => {
      mounted = false;
    };
  }, []);

  const onSubmit = async (values: ReviewFormValues) => {
    if (submitting) {
      return;
    }

    setSubmitting(true);

    try {
      await submitReview({
        name: values.name.trim(),
        email: values.email?.trim() || "",
        rating: values.rating,
        title: values.title?.trim() || "",
        message: values.message.trim(),
      });
      toast.success("Thank you! Your review has been submitted for admin approval.");
      reset(defaultValues);
    } catch {
      toast.error("Unable to submit your review right now. Please try again later.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section id="reviews" className="py-24 lg:py-32 bg-section">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          <span className="text-sm font-semibold uppercase tracking-wide text-primary">Reviews</span>
          <h2 className="mt-3 font-heading text-4xl font-bold text-heading">
            What our students say
          </h2>
        </div>

        {loading ? (
          <div className="mt-12 flex items-center justify-center gap-2 text-sm text-paragraph">
            <LoaderCircle size={16} className="animate-spin" />
            Loading reviews...
          </div>
        ) : error ? (
          <div className="mt-12 rounded-xl2 border border-border bg-white px-4 py-3 text-sm text-paragraph">
            {error}
          </div>
        ) : reviews.length === 0 ? (
          <div className="mt-12 rounded-xl2 border border-border bg-white px-4 py-3 text-sm text-paragraph">
            No reviews are available at the moment.
          </div>
        ) : (
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
            {reviews.map(({ id, name, course_name, message, rating, title }, idx) => (
              <motion.div
                key={id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="rounded-xl2 bg-white border border-border p-7 shadow-card"
              >
                <div className="flex gap-1 text-accent">
                  {Array.from({ length: rating || 5 }).map((_, i) => (
                    <Star key={i} size={16} fill="currentColor" strokeWidth={0} />
                  ))}
                </div>

                {title ? <div className="mt-4 text-lg font-semibold text-heading">{title}</div> : null}
                <p className="mt-4 text-[15px] leading-relaxed text-paragraph">{message}</p>

                <div className="mt-6 flex items-center gap-3">
                  <span className="flex h-11 w-11 items-center justify-center rounded-full bg-section border border-border text-paragraph/50">
                    <User size={18} />
                  </span>
                  <div>
                    <div className="text-sm font-semibold text-heading">{name}</div>
                    {course_name ? <div className="text-xs text-paragraph">{course_name}</div> : null}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        <div className="mt-16 rounded-3xl border border-border bg-white p-8 shadow-card">
          <div className="flex flex-col gap-2 text-center sm:text-left">
            <span className="text-sm font-semibold uppercase tracking-wide text-primary">Submit Review</span>
            <h3 className="text-3xl font-bold text-heading">Share your experience</h3>
            <p className="text-sm text-paragraph">
              Your review helps others learn about Vidyavana. Submit your feedback below and our team will review it.
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-5" noValidate>
            <div className="grid gap-4 lg:grid-cols-2">
              <label className="block text-sm font-medium text-heading">
                <span className="mb-1.5 block">Full Name</span>
                <input
                  {...register("name")}
                  className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="Enter your full name"
                />
                {errors.name ? <span className="mt-1 block text-xs text-red-500">{errors.name.message}</span> : null}
              </label>

              <label className="block text-sm font-medium text-heading">
                <span className="mb-1.5 block">Email Address</span>
                <input
                  type="email"
                  {...register("email")}
                  className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="name@example.com"
                />
                {errors.email ? <span className="mt-1 block text-xs text-red-500">{errors.email.message}</span> : null}
              </label>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <label className="block text-sm font-medium text-heading">
                <span className="mb-1.5 block">Rating</span>
                <select
                  {...register("rating", { valueAsNumber: true })}
                  className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                >
                  {[5, 4, 3, 2, 1].map((value) => (
                    <option key={value} value={value}>
                      {value} Star{value > 1 ? "s" : ""}
                    </option>
                  ))}
                </select>
                {errors.rating ? <span className="mt-1 block text-xs text-red-500">{errors.rating.message}</span> : null}
              </label>

              <label className="block text-sm font-medium text-heading">
                <span className="mb-1.5 block">Review Title</span>
                <input
                  {...register("title")}
                  className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="Optional title"
                />
              </label>
            </div>

            <label className="block text-sm font-medium text-heading">
              <span className="mb-1.5 block">Review</span>
              <textarea
                {...register("message")}
                rows={5}
                className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                placeholder="Tell us about your experience"
              />
              {errors.message ? <span className="mt-1 block text-xs text-red-500">{errors.message.message}</span> : null}
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
                    Submitting...
                  </>
                ) : (
                  "Submit Review"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}
