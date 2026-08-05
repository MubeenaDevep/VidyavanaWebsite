import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Contact — Vidyavana",
};

export default function ContactPage() {
  redirect("/");
}
