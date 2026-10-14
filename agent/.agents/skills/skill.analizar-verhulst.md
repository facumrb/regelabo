# Skill: Análisis de Uso del Modelo Verhulst

> **Trigger:** `speckit.analyze` → produce `verhulst-analysis/<nombre>.md`

---

## Propósito

Analiza cómo una funcionalidad del sistema Regelabo **utiliza el modelo de simulación Verhulst**. Determina si el modelo puede usarse como **caja negra** (invocación estándar sin modificaciones internas) o si requiere cambios en su código fuente.

---

## Veredictos posibles

| Veredicto | Significado |
|---|---|
| **Caja Negra Pura** | Se usa `model2018()` con los parámetros estándar. No se toca el código del modelo. |
| **Caja Negra con Config. Externa** | Se usan parámetros no-default de `model2018()` o se pre/post-procesan datos. El código del modelo NO se modifica. |
| **Modificación Interna Requerida** | Se necesita cambiar `model2018.py`, `inner_hair_cell2018.py`, `auditory_nerve2018.py` u otro archivo interno. |
| **No Utiliza el Modelo** | La funcionalidad usa datos pre-generados o consulta una base de datos de simulaciones ya ejecutadas. |

---

## Plantilla de Output

```markdown
# Análisis Verhulst: <Nombre de Funcionalidad>

> **Caso de uso #<N>:** <Nombre>
> **Fecha:** <fecha> | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**<Tipo de veredicto>**

<Justificación de una o dos oraciones.>

---

## 2. Entradas al Modelo

| Parámetro | Origen (UI/Config) | Función/Archivo del Modelo | Descripción |
|---|---|---|---|
| `sheraP` | <origen> | `model2018()` | Perfil auditivo (polos de Shera, ndarray 1001,) |
| `nH`, `nM`, `nL` | <origen> | `model2018()` | Fibras AN alta/media/baja espontaneidad |
| `sign` | <origen> | `model2018()` | Estímulo acústico (ndarray 1D) |
| `storeflag` | <valor fijo/configurable> | `model2018()` | Qué etapas almacenar |
| `fc` | <valor fijo/configurable> | `model2018()` | Frecuencias características |

---

## 3. Salidas del Modelo Consumidas

| Output | Nombre en código | Formato | Uso en esta funcionalidad |
|---|---|---|---|
| Onda ABR nervio auditivo | `output.w1` | ndarray float | <uso específico> |
| Onda ABR núcleo coclear | `output.w3` | ndarray float | <uso específico> |
| Onda ABR colículo inferior | `output.w5` | ndarray float | <uso específico> |
| EFR | `output.efr` | float (µV) | <uso específico> |
| Tasa de disparo AN | `output.an_sout_` | ndarray | <uso específico> |

> Solo listar las salidas que esta funcionalidad efectivamente consume.

---

## 4. Interfaz API Requerida

| Endpoint | Método | Descripción |
|---|---|---|
| `/simulate/<ruta>` | POST | <descripción> |
| `/results/<id>` | GET | Polling del resultado asíncrono |

### DTO de Request (esquema Pydantic)

```python
class <NombreFuncionalidad>Request(BaseModel):
    # completar según los parámetros específicos
    perfil: str | None = None
    audiogram: AudiogramDTO | None = None
    n_fibers: FibersConfig = FibersConfig()
    stimulus: StimulusConfig
    metadata: SimulationMetadata | None = None
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo
<Estimación: ej. "2-10 min por simulación estándar", "< 1 seg si usa cache de resultados pre-generados">

### Paralelismo / Lotes
<¿Requiere simulaciones en lote? ¿Pipeline paralelo como `ParallelRAMSimulationsEFR.py`?>

### Persistencia
<¿Resultados en PostgreSQL? ¿Archivos .mat? ¿pgvector para búsqueda por similitud?>

### Reutilización con otras funcionalidades
<¿Comparte endpoint o worker con otra funcionalidad? ¿Qué cambia?>

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Esta funcionalidad |
|---|---|---|
| `storeflag` | `'bw'` | <valor> |
| `fc` | `'abr'` | <valor> |
| Salidas consumidas | w1, w3, w5, abr | <salidas> |
| Post-procesamiento | Latencias, amplitudes | <post-proc> |
| Modificación interna | No | <Sí/No/Cuál> |
```

---

## Instrucciones de Ejecución

1. Leer descripción de la funcionalidad en `functionalitiesOverview.md`.
2. Identificar qué parámetros del modelo se manipulan (sección "Parámetro manipulado").
3. Identificar qué salidas se consumen (sección "Salida observada").
4. Determinar veredicto: ¿se necesita modificar código interno?
5. Mapear la interfaz API necesaria.
6. Comparar con el pipeline de referencia (Screening BERA).
7. Guardar en `docs/specs/verhulst-analysis/<nombre-representativo>.md`.
