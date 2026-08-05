"use client";

import { motion } from "framer-motion";
import { ArrowRight, PlayCircle, BadgeCheck, Hammer, Rocket, GraduationCap } from "lucide-react";

type HeroProps = {
  enrollAction: (courseName?: string) => void;
};

const floatCards = [
  { icon: Rocket, label: "Start Learning Today", position: "top-4 -left-6 lg:-left-10" },
  { icon: Hammer, label: "Learn by Doing", position: "top-1/3 -right-6 lg:-right-12" },
  { icon: BadgeCheck, label: "Placement Assistance", position: "bottom-16 -left-8 lg:-left-14" },
  { icon: GraduationCap, label: "Affordable Fees", position: "bottom-0 right-4 lg:right-0" },
];

export default function Hero({ enrollAction }: HeroProps) {
  return (
    <section id="home" className="relative overflow-hidden bg-white pt-32 pb-20 lg:pt-40 lg:pb-28">
      {/* Ambient background shape */}
      <div className="pointer-events-none absolute top-0 right-0 h-[600px] w-[600px] rounded-full bg-primary/5 blur-3xl" />

      <div className="relative max-w-content mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center min-h-[70vh]">
          {/* Left: copy */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-section px-4 py-1.5 text-sm font-medium text-paragraph">
              <span className="h-2 w-2 rounded-full bg-success" />
              Admissions open for 2026 batches
            </span>

            <h1 className="mt-6 font-heading text-5xl sm:text-6xl lg:text-[60px] font-bold leading-[1.1] text-heading">
              Learn Computer Skills.
              <br />
              Build Your Career.
            </h1>

            <p className="mt-6 max-w-lg text-lg leading-relaxed text-paragraph">
              From complete beginners to graduates, we help students gain practical
              computer skills, industry-ready technical knowledge, and placement support —
              all at an affordable fee.
            </p>

            <div className="mt-5 flex flex-wrap gap-2.5">
              {["Start Learning Today", "Learn by Doing", "Placement Assistance"].map((tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-primary/5 px-3.5 py-1.5 text-xs font-semibold text-primary"
                >
                  {tag}
                </span>
              ))}
            </div>

            <div className="mt-9 flex flex-wrap items-center gap-4">
              <button
                type="button"
                onClick={() => enrollAction()}
                className="group inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3.5 text-[15px] font-semibold text-white shadow-soft hover:bg-primary-hover hover:shadow-softHover transition-all duration-200"
              >
                Enroll Now
                <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
              </button>
              <a
                href="#courses"
                className="inline-flex items-center gap-2 rounded-full border border-border bg-white px-7 py-3.5 text-[15px] font-semibold text-heading hover:border-primary hover:text-primary transition-colors duration-200"
              >
                <PlayCircle size={18} />
                View Courses
              </a>
            </div>

            <div className="mt-10 flex items-center gap-6 text-sm text-paragraph">
              <div className="flex -space-x-3">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="h-9 w-9 rounded-full border-2 border-white bg-section"
                  />
                ))}
              </div>
              <span>Trusted by 1000+ students across Karnataka &amp; Andhra Pradesh</span>
            </div>
          </motion.div>

          {/* Right: illustration + floating cards */}
          <motion.div
            initial={{ opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, ease: "easeOut", delay: 0.15 }}
            className="relative mx-auto w-full max-w-md lg:max-w-none aspect-square"
          >
            {/* Illustration placeholder */}
            <div className="relative h-full w-full rounded-xl2 bg-section border border-border flex items-center justify-center overflow-hidden shadow-soft">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(59,130,246,0.12),transparent_55%)]" />
              <img
              src="/images/v-logo.png"
              alt="Vidyavana Logo"
              className="h-60 w-auto object-contain"
            />
              <span className="absolute bottom-6 text-xs font-medium tracking-wide text-paragraph/50">
                Education illustration placeholder
              </span>
            </div>

            {/* Floating cards */}
            {floatCards.map(({ icon: Icon, label, position }, idx) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + idx * 0.12 }}
                className={`absolute ${position} hidden sm:flex items-center gap-2.5 rounded-xl2 bg-white border border-border px-4 py-3 shadow-softHover animate-floaty`}
                style={{ animationDelay: `${idx * 0.6}s` }}
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-success/10 text-success">
                  <Icon size={16} strokeWidth={2.4} />
                </span>
                <span className="text-sm font-semibold text-heading whitespace-nowrap">{label}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
