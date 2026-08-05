"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ArrowUpRight, BookOpen, BrainCircuit, Briefcase, Boxes, Code2, Database, FileSpreadsheet, FolderKanban, Globe, Keyboard, LineChart, LoaderCircle, Server } from "lucide-react";
import { getCourseCategories, getCourses, type Course, type CourseCategory } from "@/lib/services";

const CATEGORY_ICONS = {
  "basic-computer-courses": Keyboard,
  "office-productivity": FileSpreadsheet,
  "programming-courses": Code2,
  "web-development": Globe,
  "backend-development": Server,
  "database-technologies": Database,
  "data-analytics": LineChart,
  "ai-emerging-technologies": BrainCircuit,
  "big-data": Boxes,
  "project-based-learning": FolderKanban,
  "placement-training": Briefcase,
};

type FeaturedCoursesProps = {
  enrollAction: (courseName?: string) => void;
};

export default function FeaturedCourses({ enrollAction }: FeaturedCoursesProps) {
  const [categories, setCategories] = useState<CourseCategory[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [categoryData, courseData] = await Promise.all([
          getCourseCategories(),
          getCourses(),
        ]);

        if (mounted) {
          setCategories(categoryData);
          setCourses(courseData);
        }
      } catch {
        if (mounted) {
          setError("Unable to load course catalog right now.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    void fetchData();

    return () => {
      mounted = false;
    };
  }, []);

  const catalog = useMemo(() => {
    if (!categories.length) {
      return [];
    }

    return categories
      .filter((category) => category.is_active)
      .map((category) => {
        const categoryCourses = courses.filter((course) => course.category_slug === category.slug && course.is_active);
        const icon = CATEGORY_ICONS[category.slug as keyof typeof CATEGORY_ICONS] ?? BookOpen;

        return {
          id: category.id,
          icon,
          name: category.name,
          tagline: category.tagline || "",
          courses: categoryCourses.length ? categoryCourses : [],
        };
      })
      .filter((entry) => entry.courses.length > 0);
  }, [categories, courses]);

  return (
    <section id="courses" className="py-24 lg:py-32 bg-white">
      <div className="max-w-content mx-auto px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <span className="text-sm font-semibold uppercase tracking-wide text-primary">
              Courses We Offer
            </span>
            <h2 className="mt-3 font-heading text-4xl font-bold text-heading max-w-lg">
              From your first click to your first job
            </h2>
          </div>
          <button
            type="button"
            onClick={() => enrollAction()}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:text-primary-hover"
          >
            Enroll now
            <ArrowUpRight size={16} />
          </button>
        </div>

        {loading ? (
          <div className="mt-12 flex items-center justify-center gap-2 text-sm text-paragraph">
            <LoaderCircle size={16} className="animate-spin" />
            Loading course catalog...
          </div>
        ) : error ? (
          <div className="mt-12 rounded-xl2 border border-border bg-section px-4 py-3 text-sm text-paragraph">
            {error}
          </div>
        ) : catalog.length === 0 ? (
          <div className="mt-12 rounded-xl2 border border-border bg-section px-4 py-3 text-sm text-paragraph">
            No courses are currently available.
          </div>
        ) : (
          <div className="mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
            {catalog.map(({ id, icon: Icon, name, tagline, courses: categoryCourses }, idx) => (
              <motion.div
                key={id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: (idx % 3) * 0.08 }}
                whileHover={{ y: -4 }}
                className="group flex flex-col rounded-xl2 border border-border bg-white p-6 shadow-card hover:shadow-softHover transition-shadow duration-300"
              >
                <span className="flex h-12 w-12 items-center justify-center rounded-xl2 bg-primary/10 text-primary">
                  <Icon size={22} strokeWidth={2} />
                </span>
                <h3 className="mt-5 font-heading text-lg font-semibold text-heading">{name}</h3>
                <p className="mt-1 text-sm text-paragraph">{tagline}</p>

                <ul className="mt-4 flex-1 space-y-1.5">
                  {categoryCourses.map((course) => (
                    <li key={course.id} className="flex items-start gap-2 text-[13.5px] text-paragraph">
                      <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary/50" />
                      {course.name}
                    </li>
                  ))}
                </ul>

                <button
                  type="button"
                  onClick={() => enrollAction(categoryCourses[0]?.name)}
                  className="mt-5 inline-flex items-center justify-center gap-1.5 rounded-full border border-border py-2.5 text-sm font-semibold text-heading group-hover:border-primary group-hover:bg-primary group-hover:text-white transition-colors duration-200"
                >
                  Enroll
                  <ArrowUpRight size={15} />
                </button>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
