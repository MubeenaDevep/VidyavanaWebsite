"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import { LoaderCircle, X } from "lucide-react";
import { api } from "@/lib/api";
import { getCourses, submitEnquiry, type Course } from "@/lib/services";

const enrollFormSchema = z.object({
  name: z.string().trim().min(3, "Full Name must be at least 3 characters"),
  email: z.string().trim().email("Please enter a valid email address"),
  phone: z
    .string()
    .trim()
    .min(10, "Please enter a valid mobile number")
    .max(15, "Please enter a valid mobile number")
    .regex(/^\+?[0-9]{10,15}$/, "Please enter a valid mobile number"),
  course: z.string().trim().min(1, "Please select a course"),
  message: z.string().trim().max(500, "Message must be at most 500 characters").optional().or(z.literal("")),
});

type EnrollFormValues = z.infer<typeof enrollFormSchema>;

type CourseOption = {
  id?: number;
  name: string;
};

type EnrollModalProps = {
  isOpen: boolean;
  onCloseAction: () => void;
  defaultCourse?: string;
};

const defaultValues: EnrollFormValues = {
  name: "",
  email: "",
  phone: "",
  course: "",
  message: "",
};

function normalizeCourseData(data: Course[]): CourseOption[] {
  return data
    .filter((item) => item.is_active)
    .map((item) => ({
      id: item.id,
      name: item.name,
    }));
}

export default function EnrollModal({ isOpen, onCloseAction, defaultCourse }: EnrollModalProps) {
  const modalRef = useRef<HTMLDivElement | null>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const [courses, setCourses] = useState<CourseOption[]>([]);
  const [isLoadingCourses, setIsLoadingCourses] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<EnrollFormValues>({
    resolver: zodResolver(enrollFormSchema),
    defaultValues,
    mode: "onTouched",
  });

  const { register, handleSubmit, reset, setValue, watch, formState: { errors } } = form;
  const selectedCourse = watch("course");

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    previousActiveElement.current = document.activeElement as HTMLElement | null;
    setValue("course", defaultCourse ?? "", { shouldValidate: true, shouldDirty: false, shouldTouch: false });
    const timeout = window.setTimeout(() => {
      const firstInput = modalRef.current?.querySelector("input, select, textarea, button") as HTMLElement | null;
      firstInput?.focus();
    }, 60);

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onCloseAction();
        return;
      }

      if (event.key !== "Tab" || !modalRef.current) {
        return;
      }

      const focusable = modalRef.current.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (!focusable.length) {
        return;
      }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    window.addEventListener("keydown", onKeyDown);

    return () => {
      window.clearTimeout(timeout);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [defaultCourse, isOpen, onCloseAction, setValue]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const fetchCourses = async () => {
      setIsLoadingCourses(true);

      try {
        const data = await getCourses();
        const normalizedCourses = normalizeCourseData(data);
        setCourses(normalizedCourses);
      } catch {
        setCourses([]);
        toast.error("Unable to load courses right now. Please try again.");
      } finally {
        setIsLoadingCourses(false);
      }
    };

    void fetchCourses();
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      reset(defaultValues);
      setCourses([]);

      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    }
  }, [isOpen, reset]);

  const courseCountLabel = useMemo(() => {
    if (isLoadingCourses) {
      return "Loading courses...";
    }

    if (courses.length === 0) {
      return "No courses available";
    }

    return `${courses.length} course${courses.length === 1 ? "" : "s"} available`;
  }, [courses.length, isLoadingCourses]);

  const onSubmit = async (values: EnrollFormValues) => {
    if (isSubmitting) {
      return;
    }

    setIsSubmitting(true);

    const selectedCourseName = values.course.trim();
    const payload = {
      name: values.name.trim(),
      email: values.email.trim(),
      phone: values.phone.trim(),
      course: null,
      preferred_batch_time: "",
      message:
        values.message && values.message.trim().length > 0
          ? values.message.trim()
          : `I am interested in enrolling in the ${selectedCourseName} course. Please contact me.`,
      source: "website" as const,
    };

    try {
      await submitEnquiry(payload);
      toast.success("Thank you! Your enquiry has been submitted successfully. Our team will contact you shortly.");
      reset(defaultValues);
      onCloseAction();
    } catch {
      toast.error("Unable to submit your enquiry. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onCloseAction();
    }
  };

  return (
    <AnimatePresence>
      {isOpen ? (
        <motion.div
          className="fixed inset-0 z-[100] flex items-end justify-center bg-slate-950/35 p-0 sm:items-center sm:p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={handleOverlayClick}
        >
          <motion.div
            ref={modalRef}
            initial={{ opacity: 0, y: 14, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 14, scale: 0.98 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="w-full max-w-[600px] rounded-t-3xl border border-border bg-white p-5 shadow-softHover sm:rounded-3xl md:p-6"
            role="dialog"
            aria-modal="true"
            aria-labelledby="enroll-modal-title"
            onClick={(event) => event.stopPropagation()}
            tabIndex={-1}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-primary">Enrollment</p>
                <h2 id="enroll-modal-title" className="mt-1 font-heading text-2xl font-bold text-heading">
                  Enquire About a Course
                </h2>
              </div>
              <button
                type="button"
                onClick={onCloseAction}
                className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-border text-paragraph transition hover:border-primary hover:text-primary"
                aria-label="Close enrollment modal"
              >
                <X size={18} />
              </button>
            </div>

            <p className="mt-3 text-sm text-paragraph">
              Fill in your details and our team will reach out with the next steps.
            </p>

            <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4" noValidate>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm font-medium text-heading">
                  <span className="mb-1.5 block">Full Name</span>
                  <input
                    {...register("name")}
                    className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                    placeholder="Enter your full name"
                  />
                  {errors.name ? <span className="mt-1 block text-xs text-red-500">{errors.name.message}</span> : null}
                </label>

                <label className="block text-sm font-medium text-heading">
                  <span className="mb-1.5 block">Email Address</span>
                  <input
                    type="email"
                    {...register("email")}
                    className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                    placeholder="name@example.com"
                  />
                  {errors.email ? <span className="mt-1 block text-xs text-red-500">{errors.email.message}</span> : null}
                </label>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm font-medium text-heading">
                  <span className="mb-1.5 block">Phone Number</span>
                  <input
                    type="tel"
                    inputMode="tel"
                    {...register("phone")}
                    className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                    placeholder="Enter mobile number"
                  />
                  {errors.phone ? <span className="mt-1 block text-xs text-red-500">{errors.phone.message}</span> : null}
                </label>

                <label className="block text-sm font-medium text-heading">
                  <span className="mb-1.5 block">Select Course</span>
                  <select
                    {...register("course")}
                    className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                    disabled={isLoadingCourses}
                  >
                    <option value="">Choose a course</option>
                    {courses.map((course) => (
                      <option key={course.id ?? course.name} value={course.name}>
                        {course.name}
                      </option>
                    ))}
                  </select>
                  <span className="mt-1 block text-xs text-paragraph">{courseCountLabel}</span>
                  {errors.course ? <span className="mt-1 block text-xs text-red-500">{errors.course.message}</span> : null}
                </label>
              </div>

              <label className="block text-sm font-medium text-heading">
                <span className="mb-1.5 block">Message</span>
                <textarea
                  {...register("message")}
                  rows={4}
                  maxLength={500}
                  className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  placeholder="Optional message"
                />
                <span className="mt-1 block text-xs text-paragraph">Optional. Maximum 500 characters.</span>
                {errors.message ? <span className="mt-1 block text-xs text-red-500">{errors.message.message}</span> : null}
              </label>

              <div className="flex flex-col-reverse gap-3 pt-1 sm:flex-row sm:justify-end">
                <button
                  type="button"
                  onClick={onCloseAction}
                  className="inline-flex items-center justify-center rounded-full border border-border bg-white px-5 py-2.5 text-sm font-semibold text-heading transition hover:border-primary hover:text-primary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-white shadow-soft transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:bg-primary/70"
                >
                  {isSubmitting ? (
                    <>
                      <LoaderCircle size={16} className="animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    "Submit Enquiry"
                  )}
                </button>
              </div>
            </form>

            {selectedCourse ? (
              <p className="mt-4 rounded-xl bg-primary/5 px-3 py-2 text-xs text-primary">
                Selected course: <span className="font-semibold">{selectedCourse}</span>
              </p>
            ) : null}
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
