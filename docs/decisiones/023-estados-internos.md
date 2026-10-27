# 023 — Estados internos del modelo: siete figuras de estados internos

**Fecha:** 2026-10-27 · **Estado:** aceptada

## Contexto
- El estudio piloto (paper "Visualización fisiológica del modelo de Verhulst…", con su validación estadística en `validacionPlanAnalisis/`, fuera de git) compara la **Condición A** (compuesto EFR/ABR, lo que muestra hoy la pantalla) con la **Condición B** (el mismo compuesto más siete **figuras de estados internos**; ver `CONTEXT.md`).
- `model2018` ya calcula esos estados con `storeflag='d'` (polo de Shera, corrientes IHC, vesículas q/w/A por tipo de fibra, CN/IC excitatorio e inhibitorio), pero el motor no la pedía y solo devolvía w1/w3/w5.
- **Medición (Flat00, 4 kHz, 110 Hz, 70 dB):** sin `d`, pico de 1,1 GB; con `d`, ~6 GB de pico y 1,4 GB de arreglos de 401 canales. Una segunda corrida dejó sin RAM una máquina de 16 GB. El servidor todavía no tiene la RAM definida.
- w1/w3/w5 dan **idénticas** con y sin `d` (diferencia 0).
- `model2018` siempre arranca un `PlotOrchestrator` (matplotlib/Tk) dentro del worker.

## Decisión
- **Las figuras se calculan siempre**, en toda simulación. A y B comparten resultado, y por ahora no hay interruptor A/B en la UI: se suma un panel con las figuras.
- **El núcleo del modelo guarda solo lo graficado:** las funciones de `core/` reciben los canales pedidos (500/1k/4k/8k Hz) y guardan solo esos. El polo de Shera se guarda submuestreado a 1 ms (400 × 401, float32). Los arreglos internos de 401 canales nunca se materializan. Objetivo: un pico cercano al actual.
- El motor pide `storeflag='wd'` (solo usa w1/w3/w5 y los internos) y apaga el `PlotOrchestrator`.
- Cada figura guarda canal, frecuencia solicitada, frecuencia característica efectiva, muestreo, ventana, unidades, factor de escala y versión.
- **Persistencia:** una tabla nueva, 1 a 1 con `resultado_simulacion`, y el endpoint `GET /api/simulaciones/{id}/estados-internos`. El detalle y el historial no cargan esos datos.
- **Dibujo:** en el frontend con Plotly, como EFR/ABR. `diagnostic_plots.py` queda como referencia.
- Test de equivalencia: w1/w3/w5 con y sin las figuras deben coincidir. Se sube `VERSION_MODELO`.

## Alternativas descartadas
- **Guardar todo en crudo o comprimido (0,5–1,4 GB por simulación):** inviable en disco y en RAM.
- **Recortar al terminar cada etapa en `_solve_one_cochlea`:** toca un solo archivo y es más flexible, pero el pico estimado es de ~2 GB y el servidor no tiene RAM definida.
- **Calcular las figuras solo a pedido:** duplica simulaciones de ~75 s y complica la caché por huella (decisión 006).
- **Columna JSONB en `resultado_simulacion` o archivo `.npz`:** cargan megas en cada lectura, o salen de la capa `datos/`.
- **PNG con matplotlib en el backend:** no es interactivo ni tiene el estilo de la pantalla actual.

## Consecuencias
- Se editan 4 archivos de `services/verhulst/src/core/` y `model2018.py`: el código se aleja del original. Si se actualiza el modelo, hay que volver a aplicar estos cambios.
- Otro canal o ventana exige volver a simular (nueva `VERSION_MODELO`).
- Se invalida la caché de resultados anteriores.
- Fig. 3 reutiliza los 4 canales de las Figs. 4–6, con un selector de canal. Las ventanas de 50 ms de las Figs. 2 y 7 van de 0 a 50 ms desde el inicio del estímulo.
- El test de equivalencia se marca `@pytest.mark.lento` (queda fuera del `pytest` normal) y se corre con `systemd-run --user --scope -p MemoryMax=3G`, que es también el tope para cualquier medición del modelo.
