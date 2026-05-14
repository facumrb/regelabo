# Análisis Verhulst: Investigación en Screening Neonatal (BERA/ABR)

> **Caso de uso #9:** Investigación en Screening Neonatal (BERA/ABR)
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [Integration Points Bera Abr.md](../Integration%20Points%20Bera%20Abr.md)

---

## 1. Veredicto

**Caja Negra Pura — Pipeline estándar sin modificaciones**

El modelo `model2018()` se invoca con parámetros estándar (`storeflag='bw'`, `fc='abr'`). No se modifica ningún archivo interno. Este es el caso de uso **canónico**: todas las demás funcionalidades se comparan contra este pipeline.

> [!IMPORTANT]
> El `simulation-service` no necesita un endpoint nuevo para ABR. El mismo endpoint EFR sirve para ambos. La diferenciación ocurre en el **frontend** y opcionalmente en un servicio de análisis post-procesamiento.

---

## 2. Entradas al Modelo

| Parámetro | Origen (UI/Config) | Función/Archivo | Descripción |
|---|---|---|---|
| `sheraP` | Catálogo pre-computado o `ohc_ind()` para audiograma hipotético | `model2018()` | Perfil coclear (ndarray 1001,) |
| `nH`, `nM`, `nL` | Sliders UI con defaults 13/3/3 | `model2018()` | Fibras AN alta/media/baja espontaneidad |
| `sign` | Generador interno (click/tone_burst/RAM) | `model2018()` | Estímulo acústico (ndarray 1D) |
| `fs` | Config del estímulo (~100 kHz) | `model2018()` | Frecuencia de muestreo |
| `storeflag` | **Fijo: `'bw'`** | `model2018()` | Almacenar ondas ABR del tronco cerebral |
| `fc` | **Fijo: `'abr'`** | `model2018()` | Frecuencias características para ABR |

> [!NOTE]
> **E1 y E2 son mutuamente excluyentes.** O se usa un perfil pre-computado, o se construye uno personalizado via `ohc_ind()`. Nunca ambos.

### Tabla detallada de entradas

| # | Input | Origen | Formato | Destino en código |
|---|---|---|---|---|
| **E1** | Perfil patológico del neonato | Dropdown UI | `string` (ej. `"Flat20"`) | `np.loadtxt(f'data/Poles/{perfil}/StartingPoles.dat')` → `sheraP` |
| **E2** | Audiograma hipotético (opcional) | Formulario paramétrico | `{freqs: float[], dB: float[]}` | `ohc_ind(name, hl_freqs_hz, hl_db, base_dir, show_figs=False)` |
| **E3** | Configuración fibras AN | Sliders o presets | `{nH: int, nM: int, nL: int}` | Parámetros de `model2018()` |
| **E4** | Tipo de estímulo | Selector UI | `string` → `"click"` / `"tone_burst"` / `"RAM"` | Generación de `np.ndarray` 1D como `sign` |
| **E5** | Datos BERA reales (opcional) | Upload archivo | `.mat` o `.csv` (time, amplitude) | Pandas → overlay en gráfico Plotly |
| **E6** | Metadatos del caso | Formulario | `{nombre_caso, notas, edad_gestacional?}` | PostgreSQL → tabla `simulations` |

---

## 3. Salidas del Modelo Consumidas

| # | Output | Nombre en código | Formato API | Uso en Frontend (Plotly.js) |
|---|---|---|---|---|
| **S1** | Onda W1 (Nervio Auditivo) | `output.w1` | `w1: float[]` | Traza individual, color verde |
| **S2** | Onda W3 (Núcleo Coclear) | `output.w3` | `w3: float[]` | Traza individual, color azul |
| **S3** | Onda W5 (Colículo Inferior) | `output.w5` | `w5: float[]` | Traza individual, color violeta |
| **S4** | ABR compuesto | `w1 + w3 + w5` | `abr: float[]` | Traza superpuesta principal |
| **S5** | Frecuencia de muestreo | `output.fs_abr` | `fs: float` (20 kHz) | Escalado eje X |
| **S6** | Eje temporal | `arange(N) / fs_abr` | `time_axis: float[]` | Eje X del gráfico |
| **S7** | Frecuencias características | `output.cf` | `cf: float[]` | Tooltip informativo |
| **S8** | Metadatos de simulación | generados por servicio | `{simulation_id, status, ...}` | Panel de estado |

### Transformación a gráficos (Plotly.js)

1. **Gráfico principal:** 4 trazas superpuestas (W1, W3, W5, ABR) vs. tiempo (ms)
2. **Marcadores interactivos:** Picos de latencia (I, III, V) con anotaciones hover
3. **Panel de métricas:** Latencia absoluta, intervalos interpico I-III / III-V / I-V, amplitudes
4. **Overlay opcional:** BERA real como traza punteada

---

## 4. Interfaz API Requerida

| Endpoint | Método | Descripción |
|---|---|---|
| `/simulate/abr` | POST | Simulación ABR individual (alias del EFR con `mode: "abr"`) |
| `/simulate/abr/{task_id}` | GET | Polling del resultado asíncrono |

### DTO de Request

```python
class ABRSimulationRequest(BaseModel):
    profile: str | None = None
    audiogram: AudiogramDTO | None = None
    n_fibers: FibersConfig = FibersConfig(nH=13, nM=3, nL=3)
    stimulus: StimulusConfig
    real_bera_url: str | None = None
    real_bera_fs: float | None = None
    metadata: NeonatalMetadata | None = None

class NeonatalMetadata(BaseModel):
    case_name: str
    gestational_age_weeks: int | None = None
    notes: str | None = None
```

### Ciclo de vida de datos

```
[Capa]              [Acción]                              [Dato transformado]
─────────────────────────────────────────────────────────────────────────────
Controlador     →   Recibe POST /simulate/abr             JSON request body
                →   Valida schema (Pydantic)               SimulationRequest DTO
                →   Delega a servicio                      —

Servicio        →   Determina fuente de polos              perfil | audiograma
                →   Si audiograma: ohc_ind()               → StartingPoles.dat (1001 floats)
                →   Si perfil: np.loadtxt()                → sheraP ndarray (1001,)
                →   Genera estímulo                        → stim ndarray 1D
                →   Encola tarea Celery                    → task_id

Worker          →   model2018(stim, fs, sheraP, ...)       — [2-10 min CPU]
                →   Extrae w1, w3, w5                      3x ndarray (N_samples,)
                →   Calcula ABR compuesto                  w1+w3+w5
                →   Calcula eje temporal                   t = arange(N) / fs_abr
                →   Serializa a JSON                       dict con listas

Controlador     →   Retorna JSON al frontend               SimulationResponse DTO
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo
- **Por simulación individual:** 2–10 minutos según perfil y estímulo.

### Paralelismo
No aplica. Cada interacción lanza **una sola simulación**. Para comparar múltiples perfiles, el fonoaudiólogo itera manualmente (DA paso 16 → volver a paso 3).

### Persistencia
- Una fila en `simulations` por ejecución.
- Arrays w1, w3, w5 en object storage referenciados por `simulation_id`.
- Metadatos neonatales (edad gestacional, notas) en PostgreSQL.

### Reutilización con otras funcionalidades

| Funcionalidad | Relación |
|---|---|
| Todas | **Este es el pipeline de referencia.** |
| #2 (Datos Sintéticos) | Usa el mismo endpoint individual × K veces |
| #3 (Sordera Oculta) | Extiende con comparación de variantes AN |
| #5 (Validación clínica) | Usa `ohc_ind()` con audiograma real |
| #16 (Arquetipos) | Los ABR de este screening pueden compararse contra la biblioteca |

---

## 6. Diferencias con el Pipeline Estándar

Este **es** el pipeline estándar. Los demás análisis se comparan contra este caso como referencia.

| Aspecto | Screening BERA (esta funcionalidad) |
|---|---|
| N° de simulaciones | 1 por interacción |
| `storeflag` | `'bw'` — fijo |
| `fc` | `'abr'` — fijo |
| `sheraP` | Variable: elegido por el usuario |
| `nH`, `nM`, `nL` | Default normativo (13/3/3) |
| Salidas consumidas | w1, w3, w5, ABR compuesto + latencias + amplitudes |
| Modificación interna del modelo | **No** |
