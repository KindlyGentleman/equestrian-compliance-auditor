import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        equestrian: {
          dark: "#0C1F16",
          forest: "#163828",
          emerald: "#23543D",
          sage: "#4B7560",
          mist: "#E8EFEA",
        },
        luxury: {
          gold: "#C5A880",
          brass: "#9E7E50",
          sand: "#EFECE6",
          parchment: "#FBFBF9",
          slate: "#151C22",
          charcoal: "#222B33",
          border: "#E4E0D7",
          borderDark: "#2B3642",
        },
      },
      fontFamily: {
        serif: ["Georgia", "Cambria", "Times New Roman", "serif"],
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
