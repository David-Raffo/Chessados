/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: ["class"],
  theme: {
    extend: {
      colors: {
        bg: "rgb(var(--bg) / <alpha-value>)",
        panel: "rgb(var(--panel) / <alpha-value>)",
        panel2: "rgb(var(--panel-2) / <alpha-value>)",
        line: "rgb(var(--line) / <alpha-value>)",
        fg: "rgb(var(--fg) / <alpha-value>)",
        muted: "rgb(var(--muted) / <alpha-value>)",
        tactics: "rgb(var(--tactics) / <alpha-value>)",
        play: "rgb(var(--play) / <alpha-value>)",
        endgames: "rgb(var(--endgames) / <alpha-value>)",
        openings: "rgb(var(--openings) / <alpha-value>)",
        rush: "rgb(var(--rush) / <alpha-value>)",
        good: "rgb(var(--good) / <alpha-value>)",
        bad: "rgb(var(--bad) / <alpha-value>)",
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "sans-serif"],
      },
      keyframes: {
        shake: {
          "0%, 100%": { transform: "translateX(0)" },
          "20%, 60%": { transform: "translateX(-6px)" },
          "40%, 80%": { transform: "translateX(6px)" },
        },
        pop: {
          "0%": { transform: "scale(.9)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
      },
      animation: {
        shake: "shake .35s ease-in-out",
        pop: "pop .2s ease-out",
      },
    },
  },
  plugins: [],
};
