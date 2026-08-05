"use client";

import { motion } from "framer-motion";
import { Target, Eye, ArrowRight, Building2 } from "lucide-react";
import Image from "next/image";

export default function AboutPreview() {
  return (
    <section id="about" className="py-24 lg:py-32 bg-white">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Image placeholder */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="relative aspect-[4/3] rounded-xl2 bg-section border border-border flex items-center justify-center order-2 lg:order-1"
          >
             <Image
    src="/images/about.png"
    alt="Students learning at Vidyavana Computer Educational Institute"
    fill
    priority
    className="object-cover"
  />
            <Building2 size={96} strokeWidth={1.1} className="text-primary/30" />
            <span className="absolute bottom-6 text-xs font-medium tracking-wide text-paragraph/50">
              Institute campus image placeholder
            </span>
          </motion.div>

          {/* Copy */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="order-1 lg:order-2"
          >
            <span className="text-sm font-semibold uppercase tracking-wide text-primary">
              About Us
            </span>
            <h2 className="mt-3 font-heading text-4xl font-bold text-heading leading-tight">
              Empowering careers through practical computer education
            </h2>
            <p className="mt-5 text-base leading-relaxed text-paragraph">
              We believe everyone deserves an opportunity to build a successful career,
              regardless of their educational background or career gap. Whether you&apos;re a
              10th pass, PUC, or degree student, an ITI or diploma graduate, a homemaker
              returning to work, or a working professional looking to upskill — our institute
              provides practical, affordable, and job-oriented training that helps you become
              confident with computers and industry technologies.
            </p>
            <p className="mt-4 text-base leading-relaxed text-paragraph">
              Our training focuses on real-world projects, hands-on practice, and placement
              preparation to help students become career-ready.
            </p>

            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div className="rounded-xl2 border border-border p-5">
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Target size={20} />
                </span>
                <h3 className="mt-3 font-heading text-base font-semibold text-heading">Our Mission</h3>
                <p className="mt-1.5 text-sm text-paragraph leading-relaxed">
                  To make quality computer education affordable and accessible for everyone
                  while helping students develop practical skills that lead to employment and
                  career growth.
                </p>
              </div>
              <div className="rounded-xl2 border border-border p-5">
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
                  <Eye size={20} />
                </span>
                <h3 className="mt-3 font-heading text-base font-semibold text-heading">Our Vision</h3>
                <p className="mt-1.5 text-sm text-paragraph leading-relaxed">
                  To become the most trusted skill development and placement-focused computer
                  training institute by transforming beginners into confident professionals.
                </p>
              </div>
            </div>

            <a
              href="#courses"
              className="mt-8 inline-flex items-center gap-2 rounded-full bg-heading px-6 py-3 text-sm font-semibold text-white hover:bg-heading/90 transition-colors duration-200"
            >
              Learn More
              <ArrowRight size={16} />
            </a>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
