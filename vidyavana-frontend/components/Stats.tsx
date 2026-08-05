"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useInView, useMotionValue, useSpring } from "framer-motion";
import { Users, BookOpen, Briefcase, Clock, LoaderCircle } from "lucide-react";
import { getDashboardStats, type DashboardStats } from "@/lib/services";

const ICONS = {
  students_trained: Users,
  placements: Briefcase,
  years_of_experience: Clock,
  courses_offered: BookOpen,
};

function Counter({ value, suffix }: { value: number; suffix: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, { duration: 1800, bounce: 0 });
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (inView) motionValue.set(value);
  }, [inView, value, motionValue]);

  useEffect(() => {
    const unsubscribe = springValue.on("change", (v) => setDisplay(Math.floor(v)));
    return () => unsubscribe();
  }, [springValue]);

  return (
    <span ref={ref}>
      {display}
      {suffix}
    </span>
  );
}

export default function Stats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchStats = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getDashboardStats();
        if (mounted) {
          setStats(data);
        }
      } catch {
        if (mounted) {
          setError("Unable to load site statistics right now.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    void fetchStats();

    return () => {
      mounted = false;
    };
  }, []);

  const statItems = stats?.manual_statistics?.length
    ? stats.manual_statistics
        .filter((item) => item.is_active)
        .slice(0, 4)
        .map((item) => {
          const Icon = ICONS[item.key as keyof typeof ICONS] ?? BookOpen;
          const numericValue = typeof item.value === "number" ? item.value : Number.parseInt(String(item.value).replace(/[^\d.]/g, ""), 10);
          return {
            icon: Icon,
            value: Number.isFinite(numericValue) ? numericValue : 0,
            suffix: typeof item.value === "number" ? "" : String(item.value).replace(/\d|\./g, "") || "+",
            label: item.label,
          };
        })
    : [
        {
          icon: Users,
          value: stats?.courses_offered ?? 0,
          suffix: "+",
          label: "Courses Offered",
        },
        {
          icon: BookOpen,
          value: stats?.course_categories ?? 0,
          suffix: "+",
          label: "Categories",
        },
        {
          icon: Briefcase,
          value: stats?.total_reviews ?? 0,
          suffix: "+",
          label: "Verified Reviews",
        },
        {
          icon: Clock,
          value: stats?.languages_supported ?? 0,
          suffix: "+",
          label: "Languages Supported",
        },
      ];

  return (
    <section className="border-y border-border bg-section py-16 lg:py-20">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        {loading ? (
          <div className="flex items-center justify-center gap-2 text-sm text-paragraph">
            <LoaderCircle size={16} className="animate-spin" />
            Loading site statistics...
          </div>
        ) : error ? (
          <div className="rounded-xl2 border border-border bg-white px-4 py-3 text-sm text-paragraph">
            {error}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
            {statItems.map(({ icon: Icon, value, suffix, label }, idx) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="flex flex-col items-center text-center gap-3"
              >
                <span className="flex h-12 w-12 items-center justify-center rounded-xl2 bg-primary/10 text-primary">
                  <Icon size={22} strokeWidth={2.2} />
                </span>
                <span className="font-heading text-4xl lg:text-5xl font-bold text-heading">
                  <Counter value={value} suffix={suffix} />
                </span>
                <span className="text-sm font-medium text-paragraph">{label}</span>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
