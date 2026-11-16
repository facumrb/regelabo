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
- **No se guarda:** vive en la dirección (`/superponer?ids=a,b,c`), que se puede volver a abrir o guardar en favoritos. Sin backend: cada simulación se pide con `GET /api/simulaciones/{id}`, que ya aplica RN4 (una ajena da 404). *Cambiado el mismo día: ver "Comparativas guardadas".*

- **Exportar (2026-11-16):** "Descargar CSV" con una fila por simulación (parámetros, EFR y fecha; coma y punto decimal, UTF-8 con BOM para Excel) e "Imprimir o guardar PDF" con el diálogo del navegador: oculta la barra, los botones y los avisos, y en tema oscuro imprime un momento en claro (`imprimirEnClaro` en `context/tema.ts`) porque Plotly dibuja con colores fijos. Sin librerías nuevas.

## Cambio del 2026-11-16: comparativas guardadas
A pedido de Valentino se revierte el descarte de "guardar con nombre".
- **Nombre:** "Comparativas guardadas", para no confundirse con los casos de estudio ni con la comparación con arquetipos.
- **Datos:** tabla `comparativa` (dueño, caso opcional, título de hasta 100, notas de hasta 2000, borrado lógico) y `comparativa_simulacion` (las simulaciones en orden, S1–S4); migración `f7a2c4e6b9d1`. Copia el módulo Casos: `/api/comparativas` con listar (cursor, filtro por caso), crear, ver, editar (título, notas y caso; las simulaciones no cambian) y borrar. Validaciones: de 2 a 4, sin repetir, propias (ajena: 404 como RN4) y terminadas; caso propio.
- **Pantalla:** "Guardar comparativa" en la superposición; una guardada se abre en la misma pantalla con `?comparativa=<id>`, con su título y notas, "Editar" y "Borrar". Se listan en la pestaña *Comparativas* del Historial y, las de un caso, en su ficha.
- Descartados para esta versión: cambiar las simulaciones de una guardada (se arma otra desde el Historial) y un ítem propio en la barra (en el celular serían 5 pestañas).

## Alternativas descartadas
- **"Comparar simulaciones":** se confunde con la comparación contra arquetipos (RN7–RN9).
- **Solo 2:** alcanza para la sordera oculta, pero no para ver una progresión (normal, leve, severa).
- **Todas las ondas de todas las simulaciones en un gráfico:** con más de 2 se vuelve ilegible.
- ~~**Guardar superposiciones con nombre**~~: se descartó primero porque la dirección ya permitía volver a abrirla; se revirtió el mismo día (ver arriba).
- **Generar el PDF en el servidor o con una librería:** el diálogo de impresión del navegador ya guarda PDF.

## Pendiente
- A qué integrante y caso de uso del TPI corresponde (hoy lo hizo Valentino, en el módulo de Simulación + historial).
