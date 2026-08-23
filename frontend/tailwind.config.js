/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#0B8F3C",
        secondary: "#FFFFFF",
        accent: "#FFD54F",
        bg: "#F8FAF8",
      },
      borderRadius: {
        card: "20px",
      },
      boxShadow: {
        card: "0 8px 30px rgba(11,143,60,0.08)",
        "card-hover": "0 12px 40px rgba(11,143,60,0.15)",
      },
    },
  },
  plugins: [],
};
