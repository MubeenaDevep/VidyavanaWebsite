import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#3B82F6",
          hover: "#2563EB",
        },
        accent: "#F59E0B",
        surface: "#FFFFFF",
        section: "#F8FAFC",
        heading: "#111827",
        paragraph: "#4B5563",
        border: "#E5E7EB",
        success: "#22C55E",
      },
      fontFamily: {
        heading: ["var(--font-poppins)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
        kannada: ["var(--font-noto-kannada)", "sans-serif"],
        telugu: ["var(--font-noto-telugu)", "sans-serif"],
      },
      borderRadius: {
        xl2: "16px",
      },
      boxShadow: {
        soft: "0 2px 8px rgba(17, 24, 39, 0.04), 0 8px 24px rgba(17, 24, 39, 0.06)",
        softHover: "0 4px 14px rgba(17, 24, 39, 0.06), 0 16px 32px rgba(17, 24, 39, 0.10)",
        card: "0 1px 2px rgba(17, 24, 39, 0.04), 0 4px 16px rgba(17, 24, 39, 0.06)",
      },
      maxWidth: {
        content: "1280px",
      },
      keyframes: {
        floaty: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
      animation: {
        floaty: "floaty 5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
