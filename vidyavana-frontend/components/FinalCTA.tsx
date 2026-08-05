"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

type FinalCTAProps = {
  enrollAction: (courseName?: string) => void;
};

export default function FinalCTA({ enrollAction }: FinalCTAProps) {
  return (
    <section id="enroll" className="py-24 lg:py-28 bg-white">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="relative overflow-hidden rounded-xl2 bg-primary px-8 py-16 lg:py-20 text-center"
        >
          <div className="pointer-events-none absolute -top-24 -right-24 h-72 w-72 rounded-full bg-white/10" />
          <div className="pointer-events-none absolute -bottom-24 -left-24 h-72 w-72 rounded-full bg-white/10" />

          <h2 className="relative font-heading text-4xl lg:text-5xl font-bold text-white leading-tight">
            Your Career Starts Here
          </h2>
          <p className="relative mt-4 text-white/85 text-lg max-w-xl mx-auto">
            Whether you&apos;re learning computers for the first time or preparing for a
            software career, we have the right course to help you succeed.
          </p>

          <button
            type="button"
            onClick={() => enrollAction()}
            className="relative mt-8 inline-flex items-center gap-2 rounded-full bg-white px-8 py-4 text-base font-semibold text-primary shadow-softHover hover:bg-white/90 transition-colors duration-200"
          >
            Join Today & Build Your Future
            <ArrowRight size={19} />
          </button>
        </motion.div>
      </div>
    </section>
  );
}
