"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import { LoaderCircle } from "lucide-react";
import { submitContactMessage } from "@/lib/services";

const contactSchema = z.object({
  name: z.string().trim().min(2, "Name must be at least 2 characters"),
  email: z.string().trim().email("Please enter a valid email address"),
  phone: z
    .string()
    .trim()
    .optional()
    .or(z.literal("") )
    .transform((v) => (v === undefined ? "" : v)),
  subject: z.string().trim().optional().or(z.literal("")),
  message: z.string().trim().min(10, "Message must be at least 10 characters"),
});

type ContactFormValues = z.infer<typeof contactSchema>;

const defaultValues: ContactFormValues = {
  name: "",
  email: "",
  phone: "",
  subject: "",
  message: "",
};

export default function ContactForm() {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<ContactFormValues>({
    resolver: zodResolver(contactSchema),
    defaultValues,
    mode: "onTouched",
  });

  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (values: ContactFormValues) => {
    if (submitting) return;
    setSubmitting(true);

    try {
      await submitContactMessage({
        name: values.name.trim(),
        email: values.email.trim(),
        phone: values.phone?.trim() ?? "",
        subject: values.subject?.trim() ?? "",
        message: values.message.trim(),
      });

      toast.success("Thank you! Your message has been submitted.");
      reset(defaultValues);
    } catch (err) {
      toast.error("Unable to submit your message. Please try again later.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-2xl mx-auto space-y-4" noValidate>
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium text-white">
          <span className="mb-1.5 block">Full Name</span>
          <input
            {...register("name")}
            className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
            placeholder="Enter your full name"
          />
          {errors.name ? <span className="mt-1 block text-xs text-red-500">{errors.name.message}</span> : null}
        </label>

        <label className="block text-sm font-medium text-white">
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
        <label className="block text-sm font-medium text-white">
          <span className="mb-1.5 block">Phone Number</span>
          <input
            type="tel"
            {...register("phone")}
            className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
            placeholder="Optional phone number"
          />
          {errors.phone ? <span className="mt-1 block text-xs text-red-500">{errors.phone.message}</span> : null}
        </label>

        <label className="block text-sm font-medium text-white">
          <span className="mb-1.5 block">Subject</span>
          <input
            {...register("subject")}
            className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
            placeholder="Subject (optional)"
          />
        </label>
      </div>

      <label className="block text-sm font-medium text-white">
        <span className="mb-1.5 block">Message</span>
        <textarea
          {...register("message")}
          rows={6}
          className="w-full rounded-xl border border-border bg-white px-3.5 py-2.5 text-sm text-heading shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20"
          placeholder="Write your message"
        />
        {errors.message ? <span className="mt-1 block text-xs text-red-500">{errors.message.message}</span> : null}
      </label>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={submitting}
          className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-white shadow-soft transition hover:bg-primary-hover disabled:cursor-not-allowed disabled:bg-primary/70"
        >
          {submitting ? (
            <>
              <LoaderCircle size={16} className="animate-spin" />
              Sending...
            </>
          ) : (
            "Send Message"
          )}
        </button>
      </div>
    </form>
  );
}
