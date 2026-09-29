"use client";

import { useEffect, useState } from "react";
import {
  GraduationCap,
  MapPin,
  Phone,
  Mail,
  Facebook,
  Instagram,
  Youtube,
  Linkedin,
} from "lucide-react";
import ContactForm from "@/components/ContactForm";
import { getCourseCategories, type CourseCategory } from "@/lib/services";

const QUICK_LINKS = ["Home", "About", "Courses", "Placements", "Reviews", "Contact"];

const SOCIALS = [
  { icon: Facebook, label: "Facebook" },
  { icon: Instagram, label: "Instagram" },
  { icon: Youtube, label: "YouTube" },
  { icon: Linkedin, label: "LinkedIn" },
];

export default function Footer() {
  const [categories, setCategories] = useState<CourseCategory[]>([]);

  useEffect(() => {
    let mounted = true;

    const fetchCategories = async () => {
      try {
        const data = await getCourseCategories();
        if (mounted) {
          setCategories(data.filter((item) => item.is_active));
        }
      } catch {
        if (mounted) {
          setCategories([]);
        }
      }
    };

    void fetchCategories();

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <footer id="contact" className="bg-heading text-white/70">
      <div className="max-w-content mx-auto px-6 lg:px-8 py-16 lg:py-20">
        <div className="mb-12 rounded-3xl border border-white/10 bg-white/5 p-6 sm:p-8 lg:p-10">
          <div className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
            <div>
              <h3 className="font-heading text-2xl font-semibold text-white">Let&apos;s talk about your goals</h3>
              <p className="mt-3 max-w-2xl text-sm leading-relaxed text-white/70">
                Have a question about courses, placements, or admissions? Send us a message and we&apos;ll get back to you shortly.
              </p>

              <ul className="mt-6 space-y-3 text-sm text-white/80">
                <li className="flex items-start gap-2.5">
                  <MapPin size={16} className="mt-0.5 shrink-0" />
                  <span>R.N. Street, beside Amrutha Medical Store, Millerpet, Bellari - 583101</span>
                </li>
                <li className="flex items-center gap-2.5">
                  <Phone size={16} className="shrink-0" />
                  <span>+91 9480070183</span>
                </li>
                <li className="flex items-center gap-2.5">
                  <Mail size={16} className="shrink-0" />
                  <span>vidyavanably@gmail.com.</span>
                </li>
              </ul>

              <div className="mt-5 h-32 rounded-xl2 border border-white/15 flex items-center justify-center text-xs text-white/40">
                <iframe
    src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3851.3857760558735!2d76.92784527488381!3d15.137143985415301!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bb71104a4143c89%3A0xbb8aff279bd51110!2svidyavana%20computer%20educational%20centre!5e0!3m2!1sen!2sin!4v1785777807533!5m2!1sen!2sin"
    width="100%"
    height="100%"
    style={{ border: 0 }}
    loading="lazy"
    allowFullScreen
    referrerPolicy="no-referrer-when-downgrade"
    title="Vidyavana Computer Educational Institute Location"
    className="w-full"
  />
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 sm:p-5">
              <ContactForm />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Institute */}
          <div>
            <div className="flex items-center gap-2.5">
              <img
                src="/images/v-logo.png"
                alt="Vidyavana Logo"
                className="h-10 w-auto object-contain"
              />
              <span className="font-heading font-semibold text-white text-lg">Vidyavana</span>
            </div>
            <p className="mt-4 text-sm leading-relaxed">
              Computer Educational Institute — career-ready skills through hands-on,
              industry-led training.
            </p>
            <div className="mt-5 flex gap-3">
              {SOCIALS.map(({ icon: Icon, label }) => (
                <a
                  key={label}
                  href="#"
                  aria-label={label}
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-white/15 hover:border-primary hover:text-primary transition-colors duration-200"
                >
                  <Icon size={16} />
                </a>
              ))}
            </div>
          </div>

          {/* Courses */}
          <div>
            <h3 className="font-heading text-sm font-semibold text-white uppercase tracking-wide">
              Courses
            </h3>
            <ul className="mt-5 space-y-3 text-sm">
              {categories.length > 0 ? (
                categories.slice(0, 6).map((category) => (
                  <li key={category.id}>
                    <a href="#courses" className="hover:text-white transition-colors">
                      {category.name}
                    </a>
                  </li>
                ))
              ) : (
                <li className="text-white/50">Course catalog loading…</li>
              )}
            </ul>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-heading text-sm font-semibold text-white uppercase tracking-wide">
              Quick Links
            </h3>
            <ul className="mt-5 space-y-3 text-sm">
              {QUICK_LINKS.map((l) => (
                <li key={l}>
                  <a
                    href={l === "Contact" ? "#contact" : `#${l.toLowerCase()}`}
                    className="hover:text-white transition-colors"
                  >
                    {l}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact + Map */}
          <div>
            <h3 className="font-heading text-sm font-semibold text-white uppercase tracking-wide">
              Contact
            </h3>
            <ul className="mt-5 space-y-3 text-sm">
              <li className="flex items-start gap-2.5">
                <MapPin size={16} className="mt-0.5 shrink-0" />
                <span>R.N. Street, beside Amrutha Medical Store, Millerpet, Bellari - 583101</span>
              </li>
              <li className="flex items-center gap-2.5">
                <Phone size={16} className="shrink-0" />
                <span>+91 9480070183</span>
              </li>
              <li className="flex items-center gap-2.5">
                <Mail size={16} className="shrink-0" />
                <span>vidyavanably@gmail.com</span>
              </li>
            </ul>

            
          </div>
        </div>

        <div className="mt-14 pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/50">
          <span>© {new Date().getFullYear()} Vidyavana Computer Educational Institute. All rights reserved.</span>
          <div className="flex gap-6">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
