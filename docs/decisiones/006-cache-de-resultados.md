# 006 — Caché de resultados por huella

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Contexto
El modelo es **determinista**: el ruido de la cóclea usa una semilla fija (`subject`), así que los mismos parámetros dan siempre el mismo resultado. El plan de cuellos de botella proponía pre-calcular y cachear para responder al instante.

## Decisión
Cada simulación tiene una **huella** (SHA-256 de perfil, fibras, estímulo, semilla y versión del modelo). `resultado_simulacion` tiene la huella como valor único, y **varias simulaciones pueden apuntar al mismo resultado**. Antes de encolar, el negocio busca un resultado con esa huella; si existe, la simulación queda completada al instante y no consume cupo (RN10).

## Alternativas descartadas
- **Copiar el resultado en cada acierto de caché:** duplica ~50 KB por simulación.
- **Redis como caché:** una pieza más, sin necesidad.

## Consecuencias
- Si se modifica el código del modelo, hay que cambiar la versión incluida en la huella para no reusar resultados viejos.
- Los arquetipos funcionan como caché "precargada".
