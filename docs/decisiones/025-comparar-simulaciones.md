# 025 — Superponer simulaciones

**Fecha:** 2026-10-30 · **Estado:** aceptada el 2026-11-16 (primera versión implementada en `feat/superponer`)

## Contexto
- Hoy, para comparar dos simulaciones hay que abrir sus detalles en dos pestañas.
- Es la forma más directa de mostrar lo central del modelo de Verhulst: dos audiogramas iguales con distinta cantidad de fibras (sordera oculta) dan un EFR distinto. La idea ya aparece como "CU1 Comparador de Perfiles Auditivos" (`docs/guias/visualizaciones_documentacion_y_requerimientos.md`) y en `docs/specs/requerimientos-sordera-oculta-comparativa.md`.
- "Comparación" ya designa otra cosa: contrastar una simulación con los arquetipos (RN7–RN9, tabla `comparacion`, módulo del Compañero B).

## Propuesta
- **Primera versión, sin backend:** elegir 2 simulaciones propias desde el historial o desde el detalle; superponer EFR y ondas ABR con la paleta de series (decisión 024) y una tabla con las diferencias de parámetros. RN4 se cumple sola: el historial solo lista las propias.
- **Después:** guardar comparaciones, más de 2 simulaciones, exportar a PDF o CSV.
- **Nombre distinto** del de la comparación con arquetipos (por ejemplo, "Superponer simulaciones" o "Comparar entre simulaciones"), para no mezclar los dos conceptos.
- Se suma como una de las próximas funcionalidades, en su propia rama, después del rediseño. El botón no aparece hasta que exista: uno que no hace nada confunde a quien recién entra.

## Decisión (2026-11-16)
- **Nombre:** "Superponer simulaciones" (ruta `/superponer`), distinto de la comparación con arquetipos.
- **Cantidad:** de 2 a 4 simulaciones propias y **terminadas**. Más de 4 curvas superpuestas no se leen; la paleta de series tiene 6 colores y cada simulación conserva el suyo (S1–S4) en los gráficos y la tabla.
- **Entrada:** casillas en el Historial con una barra "N de 4 elegidas · Superponer"; en el detalle de una simulación terminada, "Superponer con…" abre el historial con esa ya marcada (`/simulaciones?superponer=<id>`).
- **Pantalla:** tabla con perfil, estímulo, fibras, valor de EFR y fecha, que resalta en color lo que difiere; espectro FFT superpuesto; y la onda temporal elegida con un selector (EFR total, I, III o V), para no mezclar hasta 16 curvas.
- **No se guarda:** vive en la dirección (`/superponer?ids=a,b,c`), que se puede volver a abrir o guardar en favoritos. Sin backend: cada simulación se pide con `GET /api/simulaciones/{id}`, que ya aplica RN4 (una ajena da 404).

## Alternativas descartadas
- **"Comparar simulaciones":** se confunde con la comparación contra arquetipos (RN7–RN9).
- **Solo 2:** alcanza para la sordera oculta, pero no para ver una progresión (normal, leve, severa).
- **Todas las ondas de todas las simulaciones en un gráfico:** con más de 2 se vuelve ilegible.
- **Guardar superposiciones con nombre:** tabla nueva y pantalla de lista; queda para después, junto con exportar a PDF o CSV.

## Pendiente
- A qué integrante y caso de uso del TPI corresponde (hoy lo hizo Valentino, en el módulo de Simulación + historial).
