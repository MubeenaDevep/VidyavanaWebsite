"use client";

import { motion } from "framer-motion";
import {
  FileText,
  Brain,
  MessagesSquare,
  Users,
  Mic2,
  Handshake,
  Linkedin,
  CheckCircle2,
} from "lucide-react";

const TRAINING = [
  { icon: FileText, label: "Resume Building" },
  { icon: Brain, label: "Aptitude Training" },
  { icon: MessagesSquare, label: "Technical Interview Prep" },
  { icon: Handshake, label: "HR Interview Prep" },
  { icon: Users, label: "Group Discussions" },
  { icon: Mic2, label: "Mock Interviews" },
  { icon: MessagesSquare, label: "Communication Skills" },
  { icon: Linkedin, label: "LinkedIn Profile Guidance" },
];

const ELIGIBLE = [
  "ITI Students",
  "Diploma Students",
  "Degree Students",
  "Fresh Graduates",
  "Job Seekers",
];

export default function Placements() {
  return (
    <section id="placements" className="py-24 lg:py-32 bg-white">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="max-w-2xl">
          <span className="text-sm font-semibold uppercase tracking-wide text-primary">
            Placement Training & Assistance
          </span>
          <h2 className="mt-3 font-heading text-4xl font-bold text-heading">
            We prepare students for corporate careers
          </h2>
          <p className="mt-4 text-base text-paragraph leading-relaxed">
            Eligible students receive placement assistance — we help connect students
            with companies based on their skills and eligibility.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-4">
          {TRAINING.map(({ icon: Icon, label }, idx) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: (idx % 4) * 0.08 }}
              className="rounded-xl2 border border-border bg-section p-5 flex flex-col items-center text-center gap-2.5"
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-xl2 bg-white border border-border text-primary">
                <Icon size={18} />
              </span>
              <span className="text-[13px] font-semibold text-heading leading-snug">{label}</span>
            </motion.div>
          ))}
        </div>

        <div className="mt-14 rounded-xl2 bg-section border border-border p-8">
          <p className="text-sm font-semibold text-heading mb-5">
            Placement assistance is available for
          </p>
          <div className="flex flex-wrap gap-3">
            {ELIGIBLE.map((item) => (
              <span
                key={item}
                className="inline-flex items-center gap-2 rounded-full bg-white border border-border px-4 py-2 text-sm font-medium text-paragraph"
              >
                <CheckCircle2 size={15} className="text-success" />
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
