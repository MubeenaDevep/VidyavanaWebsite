"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, GraduationCap } from "lucide-react";

const NAV_LINKS = [
  { label: "Home", href: "#home" },
  { label: "About", href: "#about" },
  { label: "Courses", href: "#courses" },
  { label: "Placements", href: "#placements" },
  { label: "Reviews", href: "#reviews" },
  { label: "Contact", href: "#contact" },
];

type NavbarProps = {
  enrollAction: (courseName?: string) => void;
};

export default function Navbar({ enrollAction }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-white/95 backdrop-blur-sm shadow-soft" : "bg-white/80"
      }`}
    >
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <a href="#home" className="flex items-center gap-2.5 shrink-0">
            <img
              src="/images/v-logo.png"
              alt="Vidyavana Logo"
              className="h-12 w-auto object-contain"
            />
            
            <span className="font-heading font-semibold text-lg text-heading leading-none">
              Vidyavana
              <span className="block text-[11px] font-body font-medium tracking-wide text-paragraph/80">
                Computer Educational Institute
              </span>
            </span>
          </a>

          {/* Desktop Nav */}
          <nav className="hidden lg:flex items-center gap-8">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-[15px] font-medium text-paragraph hover:text-primary transition-colors duration-200"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* Right controls */}
          <div className="hidden lg:flex items-center gap-4">
            <button
              type="button"
              onClick={() => enrollAction()}
              className="rounded-full bg-primary px-6 py-2.5 text-sm font-semibold text-white shadow-soft hover:bg-primary-hover hover:shadow-softHover transition-all duration-200"
            >
              Enroll Now
            </button>
          </div>

          {/* Mobile toggle */}
          <button
            className="lg:hidden flex h-10 w-10 items-center justify-center rounded-xl2 text-heading"
            onClick={() => setMobileOpen((o) => !o)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="lg:hidden overflow-hidden border-t border-border bg-white"
          >
            <nav className="flex flex-col px-6 py-4 gap-1">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="rounded-xl2 px-3 py-3 text-[15px] font-medium text-paragraph hover:bg-section hover:text-primary transition-colors"
                >
                  {link.label}
                </a>
              ))}
              <button
                type="button"
                onClick={() => {
                  setMobileOpen(false);
                  enrollAction();
                }}
                className="mt-2 rounded-full bg-primary px-6 py-3 text-center text-sm font-semibold text-white shadow-soft"
              >
                Enroll Now
              </button>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
