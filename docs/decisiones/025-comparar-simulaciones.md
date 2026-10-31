# 025 — Comparar simulaciones entre sí

**Fecha:** 2026-10-30 · **Estado:** propuesta (falta la sesión de preguntas para diseñarla)

## Contexto
- Hoy, para comparar dos simulaciones hay que abrir sus detalles en dos pestañas.
- Es la forma más directa de mostrar lo central del modelo de Verhulst: dos audiogramas iguales con distinta cantidad de fibras (sordera oculta) dan un EFR distinto. La idea ya aparece como "CU1 Comparador de Perfiles Auditivos" (`docs/guias/visualizaciones_documentacion_y_requerimientos.md`) y en `docs/specs/requerimientos-sordera-oculta-comparativa.md`.
- "Comparación" ya designa otra cosa: contrastar una simulación con los arquetipos (RN7–RN9, tabla `comparacion`, módulo del Compañero B).

## Propuesta
- **Primera versión, sin backend:** elegir 2 simulaciones propias desde el historial o desde el detalle; superponer EFR y ondas ABR con la paleta de series (decisión 024) y una tabla con las diferencias de parámetros. RN4 se cumple sola: el historial solo lista las propias.
- **Después:** guardar comparaciones, más de 2 simulaciones, exportar a PDF o CSV.
- **Nombre distinto** del de la comparación con arquetipos (por ejemplo, "Superponer simulaciones" o "Comparar entre simulaciones"), para no mezclar los dos conceptos.
- Se suma como una de las próximas funcionalidades, en su propia rama, después del rediseño. El botón no aparece hasta que exista: uno que no hace nada confunde a quien recién entra.

## A definir
- Nombre definitivo, desde dónde se entra, cuántas simulaciones, qué gráficos se superponen y si se guarda.
- A qué integrante y caso de uso del TPI corresponde.
