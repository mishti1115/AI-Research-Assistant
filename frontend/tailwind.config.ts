import type { Config } from "tailwindcss";

// Design language: "the reading room" — a quiet academic library at night.
// Deep forest ink instead of the generic near-black/acid-green pairing, brass
// (not terracotta) as the single warm accent, evoking library lamps and
// leather bindings rather than a generic SaaS palette.
const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0A1210", // page background, dark mode
          900: "#0F1B17",
          800: "#152722",
          700: "#1E362F",
          600: "#2A4A40",
        },
        parchment: {
          50: "#FBF8F1", // page background, light mode
          100: "#F3EEE1",
          200: "#E8DFC9",
        },
        brass: {
          400: "#D8B876",
          500: "#B99356", // primary accent
          600: "#96773F",
        },
        moss: {
          400: "#6B9080",
          500: "#4B7267", // secondary accent (used sparingly: success/ready states)
        },
        ink_text: {
          light: "#EDEAE0", // body text on dark bg
          dark: "#28231C",  // body text on light bg
        },
      },
      fontFamily: {
        display: ["var(--font-source-serif)", "Georgia", "serif"],
        body: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      backgroundImage: {
        "grain": "radial-gradient(circle at 1px 1px, rgba(184,158,102,0.06) 1px, transparent 0)",
      },
      boxShadow: {
        tab: "2px 0 8px rgba(0,0,0,0.15)",
      },
    },
  },
  plugins: [],
};

export default config;
