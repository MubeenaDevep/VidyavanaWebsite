"use client";

import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";

const PROFILES = [
  "10th Pass Students",
  "Students who discontinued studies",
  "PUC Students",
  "Degree Students",
  "ITI Students",
  "Diploma Students",
  "B.Com",
  "BBA / BBM",
  "BCA",
  "BE / B.Tech Students",
  "Fresh Graduates",
  "Job Seekers",
  "Housewives & Women Restarting Their Careers",
  "Working Professionals",
];

export default function WhoCanJoin() {
  return (
    <section className="py-24 lg:py-32 bg-section">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          <span className="text-sm font-semibold uppercase tracking-wide text-primary">
            Who Can Join?
          </span>
          <h2 className="mt-3 font-heading text-4xl font-bold text-heading">
            Our courses are designed for everyone
          </h2>
          <p className="mt-4 text-base text-paragraph leading-relaxed">
            No prior computer knowledge is required for beginner courses.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-w-4xl mx-auto">
          {PROFILES.map((profile, idx) => (
            <motion.div
              key={profile}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: (idx % 6) * 0.06 }}
              className="flex items-center gap-3 rounded-xl2 bg-white border border-border px-4 py-3.5"
            >
              <CheckCircle2 size={18} className="shrink-0 text-success" />
              <span className="text-sm font-medium text-heading">{profile}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
