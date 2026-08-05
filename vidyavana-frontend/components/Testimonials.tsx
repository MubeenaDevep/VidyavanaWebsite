"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { LoaderCircle, Star, User } from "lucide-react";
import { getTestimonials, type Testimonial } from "@/lib/services";

export default function Testimonials() {
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchTestimonials = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getTestimonials();
        if (mounted) {
          setTestimonials(data.filter((item) => item.is_active && item.is_featured));
        }
      } catch {
        if (mounted) {
          setError("Unable to load testimonials right now.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    void fetchTestimonials();

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <section id="reviews" className="py-24 lg:py-32 bg-section">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          <span className="text-sm font-semibold uppercase tracking-wide text-primary">
            Testimonials
          </span>
          <h2 className="mt-3 font-heading text-4xl font-bold text-heading">
            What our students say
          </h2>
        </div>

        {loading ? (
          <div className="mt-12 flex items-center justify-center gap-2 text-sm text-paragraph">
            <LoaderCircle size={16} className="animate-spin" />
            Loading testimonials...
          </div>
        ) : error ? (
          <div className="mt-12 rounded-xl2 border border-border bg-white px-4 py-3 text-sm text-paragraph">
            {error}
          </div>
        ) : testimonials.length === 0 ? (
          <div className="mt-12 rounded-xl2 border border-border bg-white px-4 py-3 text-sm text-paragraph">
            No testimonials are available at the moment.
          </div>
        ) : (
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map(({ id, name, role_or_course, quote, rating }, idx) => (
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
                <p className="mt-4 text-[15px] leading-relaxed text-paragraph">&ldquo;{quote}&rdquo;</p>

                <div className="mt-6 flex items-center gap-3">
                  <span className="flex h-11 w-11 items-center justify-center rounded-full bg-section border border-border text-paragraph/50">
                    <User size={18} />
                  </span>
                  <div>
                    <div className="text-sm font-semibold text-heading">{name}</div>
                    <div className="text-xs text-paragraph">{role_or_course}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
