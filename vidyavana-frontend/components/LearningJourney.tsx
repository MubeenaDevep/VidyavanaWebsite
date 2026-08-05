"use client";

import { motion } from "framer-motion";
import { ClipboardList, BookOpenCheck, Hammer, FolderKanban, Trophy } from "lucide-react";

const STEPS = [
  { icon: BookOpenCheck, title: "Learn", desc: "Attend structured classes led by experienced trainers." },
  { icon: Hammer, title: "Practice", desc: "Reinforce every concept with guided, hands-on practice." },
  { icon: FolderKanban, title: "Build Projects", desc: "Apply your skills to live and mini projects." },
  { icon: ClipboardList, title: "Prepare for Interviews", desc: "Resume, aptitude, mock and technical interview prep." },
  { icon: Trophy, title: "Get Placed", desc: "Connect with hiring companies based on your skills." },
];

export default function LearningJourney() {
  return (
    <section className="py-24 lg:py-32 bg-section">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          <span className="text-sm font-semibold uppercase tracking-wide text-primary">
            Our Training Approach
          </span>
          <h2 className="mt-3 font-heading text-4xl font-bold text-heading">
            Learn → Practice → Build → Prepare → Get Placed
          </h2>
          <p className="mt-4 text-base text-paragraph leading-relaxed">
            Every course emphasizes practical implementation rather than just theory.
          </p>
        </div>

        <div className="mt-16 relative">
          {/* Connector line - desktop */}
          <div className="hidden lg:block absolute top-8 left-0 right-0 h-0.5 bg-border" />

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-10 lg:gap-4">
            {STEPS.map(({ icon: Icon, title, desc }, idx) => (
              <motion.div
                key={title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: idx * 0.12 }}
                className="relative flex flex-col items-center text-center"
              >
                <span className="relative z-10 flex h-16 w-16 items-center justify-center rounded-full bg-white border-2 border-primary text-primary shadow-soft">
                  <Icon size={26} strokeWidth={2} />
                </span>
                <span className="mt-2 text-xs font-bold text-primary">STEP {idx + 1}</span>
                <h3 className="mt-1 font-heading text-base font-semibold text-heading">{title}</h3>
                <p className="mt-1.5 text-sm text-paragraph leading-relaxed max-w-[180px]">{desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
