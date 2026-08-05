"use client";

import { motion } from "framer-motion";
import {
  Sparkles,
  Wrench,
  FolderKanban,
  Users2,
  Wallet,
  Clock3,
  CalendarDays,
  UsersRound,
  UserCheck,
  Building2,
  MessagesSquare,
  Briefcase,
} from "lucide-react";

const FEATURES = [
  { icon: Sparkles, title: "Beginner-Friendly Learning", desc: "Courses start from the fundamentals, so no prior computer knowledge is needed." },
  { icon: Wrench, title: "Practical Hands-on Training", desc: "Every module pairs theory with lab time, so you practice what you learn." },
  { icon: FolderKanban, title: "Live Projects", desc: "Work on real, industry-style projects that build a portfolio you can show." },
  { icon: Users2, title: "Experienced Trainers", desc: "Learn from trainers with real industry background in their subject." },
  { icon: Wallet, title: "Affordable Fees", desc: "Transparent, accessible pricing that keeps quality education within reach." },
  { icon: Clock3, title: "Flexible Timings", desc: "Morning, evening, and weekend slots built around your schedule." },
  { icon: CalendarDays, title: "Weekend & Weekday Batches", desc: "Choose the batch that fits around study, work, or family commitments." },
  { icon: UsersRound, title: "Small Batch Size", desc: "Focused class sizes so every student gets real attention." },
  { icon: UserCheck, title: "Individual Attention", desc: "Trainers track your progress and adapt pace to how you learn best." },
  { icon: Building2, title: "Industry-Oriented Curriculum", desc: "Course content is shaped by what employers actually look for." },
  { icon: MessagesSquare, title: "Interview Preparation", desc: "Mock interviews and technical & HR prep built into every course." },
  { icon: Briefcase, title: "Placement Assistance", desc: "Support connecting eligible students with hiring companies." },
];

export default function WhyChooseUs() {
  return (
    <section className="py-24 lg:py-32 bg-section">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          <span className="text-sm font-semibold uppercase tracking-wide text-primary">
            Why Choose Us
          </span>
          <h2 className="mt-3 font-heading text-4xl font-bold text-heading">
            Why students trust Vidyavana
          </h2>
          <p className="mt-4 text-base text-paragraph leading-relaxed">
            Every part of the Vidyavana experience is designed around one outcome:
            getting you job-ready, at a fee you can afford.
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {FEATURES.map(({ icon: Icon, title, desc }, idx) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: (idx % 4) * 0.08 }}
              whileHover={{ y: -4 }}
              className="rounded-xl2 bg-white border border-border p-6 shadow-card hover:shadow-softHover transition-shadow duration-300"
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-xl2 bg-primary/10 text-primary">
                <Icon size={20} strokeWidth={2.1} />
              </span>
              <h3 className="mt-4 font-heading text-[15px] font-semibold text-heading leading-snug">{title}</h3>
              <p className="mt-1.5 text-[13.5px] leading-relaxed text-paragraph">{desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
