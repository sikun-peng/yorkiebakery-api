// tailwind.config.js
import defaultTheme from 'tailwindcss/defaultTheme'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        yorkieBrown: "#7a5c42",
        yorkieBg: "#faf7f2",
        yorkieAccent: "#f8e8b0",
        yorkieBorder: "#f1e6c8",
        yorkieCard: "#ffffffee",
      },
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
    },
  },
}