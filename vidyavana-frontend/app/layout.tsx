import type { Metadata } from "next";
import { Poppins, Inter, Noto_Sans_Kannada, Noto_Sans_Telugu } from "next/font/google";
import { Toaster } from "react-hot-toast";
import ChatbotWidget from "@/components/ChatbotWidget";
import "./globals.css";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter",
  display: "swap",
});

const notoKannada = Noto_Sans_Kannada({
  subsets: ["kannada"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-noto-kannada",
  display: "swap",
});

const notoTelugu = Noto_Sans_Telugu({
  subsets: ["telugu"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-noto-telugu",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Vidyavana Computer Educational Institute | Learn Today. Build Tomorrow.",
  description:
    "Vidyavana Computer Educational Institute — industry-led computer courses in Programming, Web Development, Data Science and more, with placement assistance and hands-on training.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${poppins.variable} ${inter.variable} ${notoKannada.variable} ${notoTelugu.variable}`}>
      <body className="font-body bg-surface text-paragraph antialiased">
        <Toaster position="top-right" toastOptions={{ duration: 4000 }} />
        {children}
        <ChatbotWidget />
      </body>
    </html>
  );
}
