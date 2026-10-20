# 007 — Arquetipos y similitud

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Contexto
La idea es sugerir posibles patologías con un nivel de confianza y gráficos superpuestos. No hay datos clínicos reales ni un modelo de ML entrenado.

## Decisión
- **Biblioteca curada de ~12 arquetipos con nombre clínico:** Normal; Presbiacusia leve, moderada y severa; Trauma sináptico leve, moderado y severo; Pérdida plana leve y moderada; combinaciones mixtas. Se simulan con un estímulo estándar (tono modulado RAM de 4 kHz a 70 dB SPL).
- **Similitud:** el ABR cargado se re-muestrea, se recorta a 0–10 ms y se compara con correlación de Pearson (0–100 %), más diferencias de latencia y amplitud de las ondas I, III y V. La regla de "concluyente" es RN7.
- **ABR de prueba:** son simulados con ruido y deriva de línea base, y se guardan en `docs/ejemplos/abr/`. Se cargan por el mismo flujo que un archivo real.

## Alternativas descartadas
- **Las 132 combinaciones del plan de cuellos de botella:** no tienen nombre clínico. Quedan para cuando exista el clasificador de ML.
- **Clasificador de ML:** queda como evolución; reemplaza solo el cálculo de similitud.

## Consecuencias
- RN9: todo resultado lleva el aviso de que es una coincidencia y no un diagnóstico.
