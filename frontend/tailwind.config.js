/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['selector', '[data-tema="oscuro"]'],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'], mono: ['"JetBrains Mono"', 'monospace'] },
      colors: {
        // Paleta E (decisión 024): los valores cambian con el tema en index.css
        fondo: 'var(--bg)',
        panel: 'var(--panel)',
        tinta: 'var(--tinta)',
        tenue: 'var(--tenue)',
        linea: 'var(--linea)',
        acento: { DEFAULT: 'var(--acento)', tinta: 'var(--acento-tinta)', suave: 'var(--acento-suave)' },
        c2: 'var(--c2)',
        c3: 'var(--c3)',
      }
    },
  },
  plugins: [],
}
