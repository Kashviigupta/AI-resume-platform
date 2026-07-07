/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // "Editorial markup" palette — resume-as-document, scored like an
        // annotated draft. Kept distinct from generic cream/terracotta AI defaults.
        paper: '#FBFAF6',       // light mode background (cool-leaning off-white, not warm cream)
        ink: '#171A21',         // dark mode background / primary text on paper
        inkline: '#2A2E37',     // secondary dark surface
        highlight: '#F5C518',   // signature accent — "highlighter pen" marks
        match: '#1F8A70',       // good score / match-related accent
        flag: '#E35B4F',        // weak-area / missing-skill accent
        slate: {
          150: '#E9E7DF',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      borderRadius: {
        card: '10px',
      },
    },
  },
  plugins: [],
}
