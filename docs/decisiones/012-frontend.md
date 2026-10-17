# 012 — Frontend

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Decisión
React + **TypeScript** + Vite + Tailwind + Plotly, con `react-router` para tener páginas reales (login, casos, simulación, arquetipos, admin). Los componentes del prototipo (`.jsx`) se migraron a `.tsx` el 2026-10-16 (paso 4b) y `allowJs` quedó apagado.

## Alternativas descartadas
- **React + JavaScript:** sin migración, pero sin la detección de errores en tiempo de desarrollo; el equipo prefiere TypeScript, ya que el desarrollo se apoya en IA.
