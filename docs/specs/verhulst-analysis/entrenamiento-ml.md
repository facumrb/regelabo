# Análisis Verhulst: Entrenamiento de Inteligencia Artificial (ML)

> **Caso de uso #8:** Entrenamiento de Inteligencia Artificial (Machine Learning)
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**Caja Negra con Config. Externa — Superconjunto del pipeline de Datos Sintéticos (#2) con capa de etiquetado ML**

El modelo `model2018()` se usa exactamente igual que en la funcionalidad #2 (sin modificaciones internas). Lo que distingue a esta funcionalidad es la **capa de organización semántica**: las simulaciones se estructuran como pares `(input_features, label)` compatibles con frameworks de ML (scikit-learn, PyTorch, TensorFlow). El modelo Verhulst actúa como el **oráculo de etiquetado** del dataset.

> [!NOTE]
> El modelo Verhulst no "aprende" ni se modifica. Es la **fuente de verdad** del dataset: dada una configuración de parámetros (perfil OHC + fibras AN + estímulo), genera la señal EFR/ABR que corresponde a ese "paciente virtual". El modelo de ML que se entrenará después es un componente completamente separado.

---

## 2. Entradas al Modelo

Idénticas a la funcionalidad #2 (ver [verhulst-analysis/datos-sinteticos-ml.md](datos-sinteticos-ml.md)), con las siguientes especificidades:

| Parámetro | Valor para esta funcionalidad | Descripción |
|---|---|---|
| `sheraP` | **Todos** los perfiles del catálogo (33 disponibles) + personalizados via `ohc_ind()` | Máxima cobertura del espacio de perfiles para diversidad del dataset |
| `nH`, `nM`, `nL` | Grid de variantes: al menos sano + 2-3 grados de sinaptopatía | Necesario para que el ML pueda distinguir sinaptopatía de daño OHC |
| `sign` | Estímulo estándar fijo (RAM, fc=4kHz, fm=98Hz, 65dB SPL) | **Fijo para todo el dataset** → el ML aprende el mapeo perfil→EFR, no optimización de estímulo |
| `storeflag` | `'bw'` | ABR completo para máxima información en los vectores de features |
| `fc` | `'abr'` | Frecuencias características estándar |

### Distribución de la grilla del dataset

| Eje de variación | Opciones típicas | N |
|---|---|---|
| Perfiles OHC (Flat) | Flat00, Flat20, Flat40, Flat60, Flat80 | 5 |
| Perfiles OHC (Slope) | Slope20, Slope30, Slope45, Slope60 | 4 |
| Variantes AN (fibras) | Sano (13/3/3), Leve (7/3/3), Mod (4/2/2), Sev (1/1/1) | 4 |
| Estímulos | RAM estándar (1, fijo) | 1 |
| **Total pares** | | **9 perfiles × 4 variantes AN = 36 pares base** |

Para un dataset ML robusto se recomienda ampliar a ~165 pares usando los 33 perfiles completos del catálogo Verhulst.

---

## 3. Salidas del Modelo Consumidas

| Output | Uso como Feature / Label para ML |
|---|---|
| EFR escalar (µV) | **Feature** — columna principal del dataset CSV |
| `output.w1` (vector) | **Feature** — vector de características temporales ABR, normalizado a longitud fija L |
| `output.w3` (vector) | **Feature** — vector de características temporales ABR |
| `output.w5` (vector) | **Feature** — vector de características temporales ABR |
| ABR compuesto `w1+w3+w5` | **Feature** — señal compuesta (alternativa a usar w1/w3/w5 separados) |
| Latencias pico W1/W3/W5 | **Feature derivada** — calculada post-simulación por el sistema |
| Perfil OHC | **Label** — clase de pérdida coclear (clasificación) o grado en dB (regresión) |
| nH, nM, nL | **Label** — grado de sinaptopatía |

### Estructura del dataset exportado

```python
# dataset.csv — features escalares + labels
simulation_id, profile_name, nH, nM, nL, fm_hz, level_dB,
efr_uV, w1_peak_ms, w3_peak_ms, w5_peak_ms, w1_amp_uV, w3_amp_uV, w5_amp_uV,
label_cochlear_loss_dB, label_synapthopathy_grade, label_class

# X_abr.npy — features vectoriales (N_samples × L)
# Cada fila es el ABR compuesto normalizado a L=200 puntos
# y_labels.npy — etiquetas correspondientes (N_samples,)
```

---

## 4. Interfaz API Requerida

Reutiliza la API de lotes de la funcionalidad #2, con endpoint adicional para exportación ML:

| Endpoint | Método | Descripción |
|---|---|---|
| `/batches/` | POST | Crear lote masivo (mismo que #2) |
| `/batches/{batch_id}` | GET | Estado del lote |
| `/batches/{batch_id}/export/ml` | GET | Exportar dataset en formato ML (CSV + NPY + HDF5) |
| `/batches/{batch_id}/stats` | GET | Distribución de clases, estadísticas descriptivas |

### DTO de exportación ML

```python
class MLExportRequest(BaseModel):
    batch_id: str
    format: Literal["csv", "numpy", "hdf5", "all"] = "all"
    normalize_abr: bool = True           # Normalizar ABR a longitud fija L
    abr_length: int = 200                # Longitud del vector ABR normalizado
    include_raw_arrays: bool = False     # Si True, incluye w1/w3/w5 completos
    label_column: str = "profile_name"  # Columna a usar como label principal
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo

- Mismo que funcionalidad #2: depende del tamaño de la grilla.
- Dataset mínimo recomendado (36 pares): ~1–6 horas con 4 workers.
- Dataset completo (165 pares): ~5–27 horas.

### Normalización de vectores ABR para ML

Las ondas ABR tienen longitud N_samples que puede variar según la duración del estímulo y la fs. Para que el ML pueda operar sobre vectores de tamaño fijo, el sistema debe:
1. Extraer la ventana temporal de interés (ej. 0–15 ms post-estímulo).
2. Re-muestrear a longitud fija L (ej. L=200 puntos).
3. Normalizar amplitud (z-score o [0,1] por señal).

### Balance de clases

> [!WARNING]
> Si la grilla tiene más perfiles Flat que Slope (o vice versa), el dataset resultante estará desbalanceado. Se recomienda verificar la distribución de clases antes de exportar y aplicar técnicas de balanceo (oversampling con SMOTE o generación adicional de clases subrepresentadas).

### Reutilización con otras funcionalidades

| Funcionalidad | Relación |
|---|---|
| #2 (Datos Sintéticos) | **Idéntica infraestructura** — esta funcionalidad agrega la capa de exportación ML |
| #16 (Arquetipos Clínicos) | Comparte el dataset; la biblioteca de arquetipos es un subconjunto del dataset ML |
| #3 / #12 (Sordera Oculta) | El dataset ML debe incluir ejemplos de sinaptopatía (nH reducido con Flat00) para entrenar detección de sordera oculta |

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Entrenamiento ML |
|---|---|---|
| N° de simulaciones | 1 | Decenas a cientos (grilla completa) |
| Propósito | Diagnóstico de un caso clínico | **Generación de dataset de entrenamiento** |
| `sheraP` | Un perfil por simulación | **Todos los perfiles del catálogo** |
| `nH`, `nM`, `nL` | Un valor por simulación | **Grid de variantes de sinaptopatía** |
| Estímulo | Elegido por el usuario | **Fijo y estándar** (reproducibilidad del dataset) |
| Salida exportada | ABR del caso + latencias | **CSV + NPY + HDF5 estructurado para ML** |
| Modificación interna | No | No |
| Consumidor final | Fonoaudiólogo clínico | **Modelo de ML** |
