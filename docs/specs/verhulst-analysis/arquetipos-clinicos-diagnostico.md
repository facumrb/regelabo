# Análisis Verhulst: Apoyo Diagnóstico por Arquetipos Clínicos

> **Caso de uso #16:** Apoyo Diagnóstico por Arquetipos Clínicos (Clasificación Vectorial)
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Veredicto

**No Utiliza el Modelo en Tiempo Real — Consumidor de datos pre-generados**

La funcionalidad #16 **no llama a `model2018()` durante la interacción del fonoaudiólogo**. El modelo fue utilizado en una fase previa (funcionalidad #2, generación masiva) para construir la biblioteca de arquetipos. En tiempo de ejecución, esta funcionalidad solo realiza una **búsqueda de similitud vectorial** en PostgreSQL (con extensión pgvector) contra los vectores ABR pre-indexados.

> [!IMPORTANT]
> Esto convierte a esta funcionalidad en la más rápida de todo el sistema: la respuesta es en **milisegundos**, no en minutos. El cuello de botella fue resuelto offline en la fase de generación de la biblioteca.

---

## 2. Entradas al Modelo

> **No aplica directamente en tiempo real.** El modelo fue consumido en la fase de generación de arquetipos (funcionalidad #2).

### Parámetros usados en la fase offline (generación de biblioteca)

| Parámetro | Valor usado | Descripción |
|---|---|---|
| `sheraP` | 33 perfiles pre-computados: Flat00..Flat80, Slope15..Slope80, normales | Todos los perfiles del catálogo standard |
| `nH`, `nM`, `nL` | Múltiples combinaciones (ej. 5 variantes por perfil OHC) | Grid de sinaptopatía × pérdida coclear |
| `sign` | RAM estándar (fc=4kHz, fm=98Hz, 65 dB SPL) | Estímulo normalizado de la biblioteca |
| `storeflag` | `'bw'` | Ondas ABR (w1, w3, w5) para construcción de vectores |
| `fc` | `'abr'` | Frecuencias características estándar |

### Parámetros de la fase online (búsqueda en tiempo real)

| Parámetro | Origen | Descripción |
|---|---|---|
| `query_vector` | ABR real del paciente, normalizado y re-muestreado | Vector de consulta para búsqueda coseno |
| `filter_category` | Selección del fonoaudiólogo (opcional) | Filtro sobre subconjunto de arquetipos (ej. solo sinaptopatía) |
| `top_k` | Config del sistema (default: 3) | Número de arquetipos a retornar |

---

## 3. Salidas del Modelo Consumidas (de la biblioteca)

Los arquetipos almacenados en la biblioteca contienen:

| Campo | Nombre en DB | Formato | Uso en esta funcionalidad |
|---|---|---|---|
| Vector ABR indexado | `abr_embedding` | `vector(N)` en pgvector | Comparación coseno con ABR del paciente |
| Onda ABR nerv. auditivo | `w1_array` (en storage) | ndarray float | Overlay visual en el gráfico de comparación |
| Onda ABR núcleo coclear | `w3_array` (en storage) | ndarray float | Overlay visual |
| Onda ABR colículo inferior | `w5_array` (en storage) | ndarray float | Overlay visual |
| EFR (µV) | `efr_value` | float | Mostrado en tabla de métricas del arquetipo |
| Perfil OHC | `profile_name` | string | Etiqueta diagnóstica del arquetipo |
| Config fibras AN | `nH`, `nM`, `nL` | int | Descripción del arquetipo |
| Etiqueta clínica | `clinical_label` | string | "Normal", "Trauma Acústico", "Sinaptopatía Leve", etc. |
| Score de similitud | calculado en consulta | float [0-1] | Porcentaje de coincidencia mostrado al fonoaudiólogo |

---

## 4. Interfaz API Requerida

### APIs de búsqueda (tiempo real — sin invocar modelo)

| Endpoint | Método | Descripción |
|---|---|---|
| `/archetypes/search` | POST | Búsqueda vectorial por similitud con el ABR del paciente |
| `/archetypes/` | GET | Listar todos los arquetipos disponibles en la biblioteca |
| `/archetypes/{id}` | GET | Obtener detalle y ondas de un arquetipo específico |
| `/archetypes/status` | GET | Estado de la biblioteca (cuántos arquetipos, última actualización) |

### APIs de gestión de la biblioteca (admin — invoca modelo offline)

| Endpoint | Método | Descripción |
|---|---|---|
| `/archetypes/build` | POST | Lanzar generación masiva (usa funcionalidad #2 internamente) |
| `/archetypes/build/{job_id}` | GET | Estado de la construcción de la biblioteca |

### DTO de Request de búsqueda

```python
class ArchetypeSearchRequest(BaseModel):
    abr_signal: list[float]              # Onda ABR del paciente (normalizada a fs_standard)
    fs_patient: float                    # Frecuencia de muestreo original del equipo BERA
    filter_category: str | None = None  # "flat_loss"|"slope_loss"|"synapthopathy"|None (todos)
    top_k: int = 3                       # Cuántos arquetipos retornar
    patient_metadata: PatientRef | None = None

class ArchetypeSearchResponse(BaseModel):
    results: list[ArchetypeMatch]        # Top-K arquetipos ordenados por similitud
    query_vector_preview: list[float]    # ABR normalizado como fue enviado a pgvector

class ArchetypeMatch(BaseModel):
    archetype_id: str
    clinical_label: str                  # "Trauma Acústico Moderado"
    similarity_score: float              # 0.0 - 1.0
    profile_name: str                    # "Flat40"
    fibers_config: FibersConfig          # {nH: 7, nM: 3, nL: 3}
    abr_w1: list[float]                  # Onda del arquetipo para overlay
    abr_w3: list[float]
    abr_w5: list[float]
    efr_uV: float
```

---

## 5. Consideraciones de Implementación

### Tiempo de cómputo (fase online)

- **Búsqueda vectorial en pgvector:** < 10 ms para bibliotecas de hasta 10.000 arquetipos.
- **Carga de ondas del arquetipo desde storage:** 50–200 ms (red + descompresión).
- **Total percibido por el usuario:** < 500 ms → experiencia casi instantánea.

### Tiempo de cómputo (fase offline — construcción de biblioteca)

- Ver funcionalidad #2: 4–16 horas para 165+ arquetipos con 4 workers paralelos.
- La biblioteca se construye una vez y se puede enriquecer incrementalmente.

### Paralelismo

- No aplica en la búsqueda online (secuencial, instantánea).
- La construcción offline usa el pipeline paralelo de la funcionalidad #2.

### Persistencia

**Esquema de base de datos crítico:**

```sql
-- Tabla principal de arquetipos
CREATE TABLE archetypes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinical_label TEXT NOT NULL,           -- "Trauma Acústico Moderado"
    profile_name TEXT NOT NULL,             -- "Flat40"
    n_h INTEGER NOT NULL,
    n_m INTEGER NOT NULL,
    n_l INTEGER NOT NULL,
    stimulus_type TEXT NOT NULL,            -- "RAM"
    efr_uV REAL,
    w1_peak_ms REAL,
    w3_peak_ms REAL,
    w5_peak_ms REAL,
    abr_embedding vector(200),              -- pgvector: ABR normalizado (ej. 200 puntos)
    abr_storage_path TEXT,                  -- Path al .mat completo en object storage
    created_at TIMESTAMPTZ DEFAULT now(),
    batch_id UUID REFERENCES batches(id)    -- Trazabilidad con la generación masiva
);

-- Índice HNSW para búsqueda vectorial eficiente
CREATE INDEX ON archetypes
USING hnsw (abr_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### Reutilización con otras funcionalidades

| Funcionalidad | Relación |
|---|---|
| #2 (Datos Sintéticos) | **Proveedor** — genera los arquetipos que esta funcionalidad indexa |
| #9 (Screening Neonatal) | Comparte el formato de ondas ABR; los ABR del screening podrían compararse contra arquetipos |
| #12 (Edad vs. Trauma) | Los perfiles de ese experimento son candidatos para arquetipos en la biblioteca |

---

## 6. Diferencias con el Pipeline Estándar (Screening BERA)

| Aspecto | Screening BERA (referencia) | Arquetipos Clínicos |
|---|---|---|
| ¿Invoca `model2018()`? | **Sí** (en tiempo real, 2-10 min) | **No** (en tiempo real). El modelo solo se usa offline |
| Tiempo de respuesta | 2–10 minutos | < 500 ms |
| `sheraP` / `nH/nM/nL` | Elegidos por el usuario | Pre-definidos en la biblioteca (no editables en el módulo) |
| Input del usuario | Parámetros de simulación | **ABR real del paciente** (archivo o registro) |
| Output | Ondas simuladas del perfil configurado | Arquetipos más similares + overlay |
| Modificación interna | No | No (ni siquiera invoca el modelo) |
| Arquitectura | simulation-service → Celery → model2018 | search-service → pgvector → PostgreSQL |
