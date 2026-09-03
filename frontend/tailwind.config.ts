/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0A0E17",       // page background
        surface: "#10151F",    // card background
        "surface-raised": "#161C29",
        border: "#232B3D",
        "text-primary": "#E8EAF0",
        "text-muted": "#8891A7",
        "text-faint": "#5A6378",
        spectrum: {
          blue: "#3B82F6",
          violet: "#8B5CF6",
          cyan: "#22D3EE",
        },
        signal: {
          good: "#34D399",
          warn: "#FBBF24",
          bad: "#F87171",
        },
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      backgroundImage: {
        "spectrum-gradient": "linear-gradient(90deg, #3B82F6 0%, #8B5CF6 55%, #22D3EE 100%)",
        "spectrum-gradient-radial": "radial-gradient(circle at 30% 20%, rgba(139,92,246,0.18), transparent 55%), radial-gradient(circle at 80% 60%, rgba(34,211,238,0.12), transparent 50%)",
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(139, 92, 246, 0.35)",
        card: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
        "fade-up": {
          "0%": { opacity: 0, transform: "translateY(12px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
      animation: {
        scan: "scan 2.4s ease-in-out infinite",
        "fade-up": "fade-up 0.6s ease-out forwards",
      },
    },
  },
  plugins: [],
};
