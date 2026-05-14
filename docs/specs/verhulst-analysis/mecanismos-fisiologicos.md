# Análisis Verhulst: Estudiar Mecanismos Fisiológicos del Oído Interno

> **Caso de uso #1:** Estudiar mecanismos fisiológicos
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**Caja Negra con Config. Externa — `storeflag` como selector de etapa biológica**

El modelo se usa sin modificaciones internas, pero el parámetro `storeflag` actúa como un "selector de canal de observación" que expone diferentes etapas del pipeline biológico. Esta es la única funcionalidad donde `storeflag` es **configurable por el usuario** (en todas las demás se fija a `'bw'` para ABR). El modelo ya implementa este mecanismo; solo hay que exponerlo en la UI.

---

## 2. Entradas al Modelo

| Parámetro | Origen (UI/Config) | Función/Archivo del Modelo | Descripción |
|---|---|---|---|
| `sheraP` | Selector de perfil OHC en UI | `model2018()` | Perfil coclear — puede ser Flat/Slope para estudiar daño OHC |
| `nH`, `nM`, `nL` | Sliders en UI (valores individuales) | `model2018()` | Reducción selectiva de fibras AN para estudiar sinaptopatía |
| `sign` | Selector de estímulo en UI | `model2018()` | Click, tono puro, RAM — elegido según qué etapa se estudia |
| `fs` | Config del estímulo | `model2018()` | Frecuencia de muestreo |
| **`storeflag`** | **Selector de etapa en UI — configurable por el usuario** | `model2018()` | **Parámetro clave de esta funcionalidad** |
| `fc` | Config (puede ser `'abr'` o array) | `model2018()` | Frecuencias características |

### Valores de `storeflag` y su significado biológico

| `storeflag` | Etapa biológica | Salida expuesta | Cuándo usarlo |
|---|---|---|---|
| `'bm'` | Membrana Basilar (BM) | Velocidad BM por lugar coclear | Estudiar mecánica coclear / efecto de OHC |
| `'ihc'` | Célula Ciliada Interna | Potencial de membrana IHC | Estudiar transducción mechano-eléctrica |
| `'an'` | Nervio Auditivo (AN) | Tasas de disparo por fibra | Estudiar efecto de sinaptopatía |
| `'cn'` | Núcleo Coclear (CN) | Respuesta CN temporal | Estudiar procesamiento subcortical temprano |
| `'bw'` | Tronco Cerebral (ABR) | Ondas W1, W3, W5 | Estudiar respuesta a nivel ABR (default) |

---

## 3. Salidas del Modelo Consumidas

La salida depende directamente del `storeflag` elegido:

| `storeflag` | Campo en `output` | Dimensiones | Visualización |
|---|---|---|---|
| `'bm'` | `output.bm_velocity` | (N_CF × N_samples) | Mapa de calor: lugar coclear vs. tiempo |
| `'ihc'` | `output.ihc_potential` | (N_CF × N_samples) | Curvas de potencial por canal de frecuencia |
| `'an'` | `output.an_sout_` | (N_fibers × N_CF × N_samples) | PSTH / rasterplot por subpoblación |
| `'cn'` | `output.cn_output` | (N_CF × N_samples) | Ondas por canal de frecuencia |
| `'bw'` | `output.w1`, `output.w3`, `output.w5` | (N_samples,) | Trazas ABR temporales |

> [!NOTE]
> La salida de `'bm'`, `'ihc'` y `'an'` es matricial (N_CF × N_samples), lo que requiere visualizaciones especiales (mapas de calor, PSTH) en el frontend. Solo `'bw'` produce vectores 1D simples.

---

## 4. Interfaz API Requerida

| Endpoint | Método | Descripción |
|---|---|---|
| `/simulate/physiology` | POST | Simulación con `storeflag` configurable por el usuario |
| `/simulate/physiology/{task_id}` | GET | Polling del resultado |

### DTO de Request

```python
class PhysiologySimulationRequest(BaseModel):
    # Configuración del daño
    profile: str | None = None           # Perfil OHC pre-computado (ej. "Flat20")
    audiogram: AudiogramDTO | None = None # Alternativa: audiograma custom
    n_fibers: FibersConfig = FibersConfig(nH=13, nM=3, nL=3)  # Reducción AN opcional

    # Selector de etapa biológica (clave de esta funcionalidad)
    store_flag: Literal['bm', 'ihc', 'an', 'cn', 'bw'] = 'bw'

    # Estímulo
    stimulus: StimulusConfig

    # Comparación con sano (opcional)
    include_healthy_reference: bool = False

    metadata: SimulationMetadata | None = None
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo

- Similar al Screening BERA: 2–10 minutos por simulación individual.
- Si se incluye referencia sana: 2× el tiempo (2 simulaciones paralelas).

### Consideración especial: tamaño de salida

> [!WARNING]
> Las salidas matriciales (`storeflag='bm'`, `'ihc'`, `'an'`) son **órdenes de magnitud más grandes** que las ondas ABR (W1, W3, W5). Un array `an_sout_` puede tener dimensiones (19 fibras × 401 frecuencias × 20.000 muestras), lo que representa ~1.2 GB en float64. Es **imprescindible** comprimir (HDF5 / `.mat`) y paginar la transferencia al frontend.

### Paralelismo

Si se incluye referencia sana: 2 tareas Celery independientes → ejecutan en paralelo.

### Reutilización con otras funcionalidades

| Funcionalidad | Relación |
|---|---|
| #3 (Hipótesis Sordera Oculta) | Comparte el concepto de manipular nH/nM/nL; aquí además se puede observar la etapa AN directamente |
| #9 (Screening Neonatal) | Comparte endpoint base; esta funcionalidad es la generalización del `storeflag='bw'` que el Screening usa de forma fija |
| #2 (Datos Sintéticos) | En lotes científicos avanzados puede interesar almacenar salidas de `'an'` para entrenar modelos |

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Mecanismos Fisiológicos |
|---|---|---|
| `storeflag` | **`'bw'` — fijo** | **Configurable por el usuario** — es el parámetro central |
| Output consumido | Solo w1, w3, w5 | Cualquier etapa: bm, ihc, an, cn, bw |
| Tamaño de salida | Pequeño (3 arrays 1D × ~200 puntos) | Puede ser muy grande (matrices N_CF × N_samples) |
| Actor | Fonoaudiólogo clínico | Investigador / neurocientífico auditivo |
| Visualización | Gráfico temporal ABR | Varía: mapa de calor (BM/IHC), PSTH (AN), curvas temporales (CN/ABR) |
| Modificación interna | No | No |
