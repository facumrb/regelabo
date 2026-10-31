# Changelog

Cambios notables del proyecto. Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Sin publicar]

### Agregado
- `CONTEXT.md`: glosario del dominio (estado interno, figura de estado interno, compuesto EFR/ABR, condiciones A/B).
- `CHANGELOG.md`.
- Decisión 023: estados internos del modelo (siete figuras de estados internos).
- El motor calcula los estados internos de las siete figuras (`SalidaModelo.estados_internos`) guardando solo los canales de 500/1k/4k/8k Hz y el polo de Shera cada 1 ms: el pico de RAM sigue en ~1,1 GB (con `d` completa eran ~6 GB).
- Tabla `estados_internos` (1 a 1 con `resultado_simulacion`, migración `54e6d03c0fe8`): el worker guarda ahí las siete figuras (~4,6 MB de JSON por resultado, 5 cifras significativas). No viajan en el detalle de la simulación.
- `GET /api/simulaciones/{id}/estados-internos` (404 `estados_internos_no_disponibles` si no terminó o es de una versión anterior; ajena, 404 como siempre), tipos `EstadosInternos` en `tiposSimulacion.ts` y `simulacionesApi.estadosInternos`, request 16 en la colección de Bruno.
- Panel colapsable "Estados internos" (`PanelEstadosInternos.tsx`) con las siete figuras en Plotly, en el simulador y en el detalle del historial; pide los datos recién al abrirse.
- `.claude/launch.json` con `backend` y `frontend` para la vista previa del agente.
- Test `lento` de equivalencia: w1/w3/w5 idénticas con y sin estados internos (`uv run pytest -m lento`).

### Cambiado
- `VERSION_MODELO` pasa a `verhulst2018-2`: invalida la caché de resultados anteriores.
- `model2018` acepta `frecuencias_internas` y `graficar` (en el worker no arranca el `PlotOrchestrator` ni escribe `.npz` parciales); `store_internals` del núcleo acepta una lista de canales.
- `.gitignore`: ignora `validacionPlanAnalisis/` (validación estadística del estudio piloto, de uso local).
