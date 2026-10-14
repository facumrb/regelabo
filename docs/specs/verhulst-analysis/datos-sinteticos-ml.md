# Análisis Verhulst: Generar Datos Sintéticos Controlados

> **Caso de uso #2:** Generar datos sintéticos controlados
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**Caja Negra con Config. Externa + Paralelismo**

El modelo `model2018()` se usa sin modificaciones internas. Lo que distingue a esta funcionalidad es la ejecución de **múltiples instancias en paralelo** (K simulaciones en lote) mediante el pipeline `ParallelRAMSimulationsEFR.py`, y la estrategia de almacenamiento masivo de resultados. No se toca el código del modelo en ningún momento.

> [!IMPORTANT]
> El código fuente del modelo Verhulst permanece intacto. Toda la lógica de lote y paralelismo vive en el `simulation-service`, no en el modelo.

---

## 2. Entradas al Modelo

| Parámetro | Origen (UI/Config) | Función/Archivo del Modelo | Descripción |
|---|---|---|---|
| `sheraP` | Catálogo pre-computado (`Poles/FlatXX/StartingPoles.dat`) o `ohc_ind()` para audiogramas custom | `model2018()` arg directo | Perfil coclear (1001 floats) |
| `nH`, `nM`, `nL` | Formulario UI — valor único o rango de barrido | `model2018()` args directos | Fibras AN: alta (13), media (3), baja (3) espontaneidad — valores default |
| `sign` | Generado por `get_RAM_stims.py` u otro generador | `model2018()` arg `sign` | Estímulo acústico (ndarray 1D). Para esta funcionalidad: prioritariamente RAM para EFR |
| `fs` | Config del estímulo | `model2018()` arg `fs` | Frecuencia de muestreo del estímulo (típico: 100 kHz) |
| `storeflag` | Seleccionado por el investigador en UI | `model2018()` arg `storeflag` | `'bw'` (ABR), `'an'` (tasas AN), `'ihc'` (potenciales), etc. — múltiples flags posibles |
| `fc` | Config de la grilla | `model2018()` arg `fc` | Frecuencias características; `'abr'` para ABR, array de frecuencias para EFR |

### Parámetros de la Grilla (nivel sistema, NO del modelo)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `profiles[]` | Lista de nombres de perfiles | `["Flat00", "Flat20", "Flat40", "Slope20"]` |
| `stimuli[]` | Lista de configs de estímulo | `[{type: "RAM", fm: 98, fc: 4000, level: 65}]` |
| `n_fibers_grid[]` | Variaciones de fibras AN a barrer | `[{nH:13,nM:3,nL:3}, {nH:7,nM:3,nL:3}]` |
| `outputs_requested[]` | Qué salidas almacenar | `["efr", "w1", "w3", "w5"]` |

---

## 3. Salidas del Modelo Consumidas

| Output | Nombre en código | Formato | Uso en esta funcionalidad |
|---|---|---|---|
| EFR (magnitud espectral) | `output.efr` o calcular FFT de `w1+w3+w5` | float (µV) | **Columna principal** del dataset CSV resultante |
| Onda ABR nervio auditivo | `output.w1` | ndarray float | Almacenado en MAT por simulación |
| Onda ABR núcleo coclear | `output.w3` | ndarray float | Almacenado en MAT por simulación |
| Onda ABR colículo inferior | `output.w5` | ndarray float | Almacenado en MAT por simulación |
| Tasa de disparo AN | `output.an_sout_` | ndarray (N_CF × N_samples) | Almacenado si `storeflag='an'` — datasets de investigación avanzada |
| Velocidad BM | `output.bm_velocity` | ndarray | Almacenado si `storeflag='bm'` — investigación de mecánica coclear |

### Formato de salida agregada (CSV del lote)

```csv
simulation_id, batch_id, profile_name, nH, nM, nL, stimulus_type, fm_hz, level_dB, efr_uV, w1_peak_ms, w3_peak_ms, w5_peak_ms
sim_001, batch_20260512, Flat00, 13, 3, 3, RAM, 98, 65, 0.452, 1.4, 3.6, 5.8
sim_002, batch_20260512, Flat20, 13, 3, 3, RAM, 98, 65, 0.311, 1.6, 3.9, 6.1
...
```

---

## 4. Interfaz API Requerida

| Endpoint | Método | Descripción |
|---|---|---|
| `/batches/` | POST | Crear un nuevo lote de simulaciones con la grilla definida |
| `/batches/{batch_id}` | GET | Consultar estado del lote (progreso, errores, ETA) |
| `/batches/{batch_id}/results` | GET | Obtener resultados agregados del lote |
| `/batches/{batch_id}/export` | GET | Descargar CSV o MAT del lote completo |
| `/batches/{batch_id}/simulations/{sim_id}` | GET | Detalle de una simulación individual del lote |

### DTO de Request

```python
class BatchSimulationRequest(BaseModel):
    profiles: list[str]                         # ["Flat00", "Flat20", ...]
    audiograms: list[AudiogramDTO] | None = None # alternativa a profiles pre-computados
    n_fibers_grid: list[FibersConfig]           # [{nH:13, nM:3, nL:3}, ...]
    stimuli: list[StimulusConfig]               # [{type:"RAM", fm:98, fc:4000, level:65}]
    outputs_requested: list[OutputFlag]         # ["efr", "w1", "w3", "w5"]
    metadata: BatchMetadata | None = None       # nombre del experimento, notas

class BatchMetadata(BaseModel):
    experiment_name: str
    researcher: str | None = None
    notes: str | None = None
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo

- **Por simulación individual:** 2–10 minutos (según perfil y estímulo).
- **Lote de 100 simulaciones con 4 workers paralelos:** ~50–250 minutos.
- **Lote de 33 perfiles × 3 estímulos × 2 configs fibras = 198 sims:** ~4–16 horas.

> [!WARNING]
> Para lotes grandes (>50 simulaciones), se recomienda ejecutar en horario nocturno o con recursos dedicados. El dashboard debe mostrar ETA y progreso en tiempo real via WebSocket.

### Paralelismo / Lotes

Existen dos niveles de paralelismo:
1. **A nivel Celery:** Múltiples workers Celery procesan tareas independientes del pool.
2. **A nivel modelo:** `ParallelRAMSimulationsEFR.py` ya implementa paralelismo interno con `multiprocessing`.

La integración recomendada es que **cada tarea Celery maneje una sola simulación**, permitiendo monitoreo granular y reintentos individuales en caso de fallo.

### Persistencia

- **Resultados comprimidos:** Almacenar arrays completos (w1, w3, w5) en archivos `.mat` en object storage (MinIO o S3), referenciados por `simulation_id`.
- **Métricas agregadas:** Persistir en PostgreSQL (tabla `batch_simulations`) las columnas escalares (EFR µV, latencias pico, etc.) para consultas SQL rápidas.
- **pgvector:** Para la funcionalidad #16 (Arquetipos), los vectores de waveform ABR se indexan en pgvector en PostgreSQL para búsqueda por similitud coseno.

### Reutilización con otras funcionalidades

| Funcionalidad | Relación | Qué comparte |
|---|---|---|
| #8 (Entrenamiento ML) | Consumidor | Usa el CSV de este lote como dataset de entrenamiento |
| #16 (Arquetipos Clínicos) | Consumidor | Usa los vectores waveform de este lote indexados en pgvector |
| #9 (Screening Neonatal) | Comparte infraestructura | Usa el mismo endpoint de simulación individual |
| #5 (Validación clínica) | Comparte infraestructura | Puede exportar MAT para comparar con datos reales |

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Datos Sintéticos en Lote |
|---|---|---|
| N° de simulaciones | 1 por interacción | K (decenas a miles) |
| `storeflag` | `'bw'` (ABR) | Configurable por el investigador: `'bw'`, `'an'`, `'ihc'`, etc. |
| `fc` | `'abr'` | Configurable: `'abr'` o array de frecuencias para EFR |
| Actor | Fonoaudiólogo clínico | Investigador / Data scientist |
| Salidas consumidas | w1, w3, w5 + latencias para un caso | CSV masivo + MAT + JSON metadatos |
| Tiempo de espera UX | Progress bar (1 sim) | Dashboard de lote con progreso por simulación |
| Modificación interna | No | No |
| Estrategia de almacenamiento | Una fila en DB | N filas en DB + archivos MAT en object storage |
