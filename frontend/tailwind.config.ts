import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "gov-green": "#1B6B3C",
        "gov-green-dark": "#0F4A28",
        "gov-gold": "#D4A017",
        "gov-sidebar": "#2B2B2B",
      },
    },
  },
  plugins: [],
} satisfies Config;