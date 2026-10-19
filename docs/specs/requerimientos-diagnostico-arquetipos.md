# Casos de Uso y Requerimientos: Apoyo Diagnóstico por Arquetipos Clínicos

> Documento derivado de `verhulst-analysis/diagnostico-arquetipos.md` y `activity-diagrams/arquetipos-clinicos-diagnostico.md`

> [!CAUTION]
> **Estado de implementación: Parcialmente postergado.**
> Los requerimientos de este módulo están divididos en dos fases. Los marcados con `[FASE 1]` son implementables en el sprint actual. Los marcados con `[FASE 2 — FUTURA]` dependen del `llm-service` y la infraestructura de IA, cuya implementación está postergada indefinidamente.

---

## 1. Casos de Uso

| ID | Nombre | Actor Principal | Descripción | Precondiciones | Postcondiciones | Fase |
|----|--------|-----------------|-------------|----------------|-----------------|------|
| CU-01 | Acceder al Módulo de Arquetipos | Fonoaudiólogo | El usuario navega al panel de "Apoyo Diagnóstico por Arquetipos Clínicos" | La biblioteca de arquetipos (`precomputed_profiles`) debe tener al menos un perfil disponible | El sistema muestra la interfaz con la opción de cargar datos del paciente | 1 |
| CU-02 | Cargar Registro ABR del Paciente | Fonoaudiólogo | El usuario sube el archivo con las ondas ABR reales de su paciente (MAT, CSV o EDF) o selecciona un registro ya existente en el sistema | El archivo tiene columnas válidas: `time[]` y `amplitude[]` | El archivo se valida, normaliza y previsualiza en el frontend | 1 |
| CU-03 | Confirmar y Normalizar Señal | Fonoaudiólogo | El usuario revisa la previsualización de la onda cargada y confirma que es la correcta antes de proceder | CU-02 completado | La señal está lista para comparar: remuestreada a 20 kHz y acotada al rango 0-10 ms | 1 |
| CU-04 | Seleccionar Arquetipos de Referencia Manualmente | Fonoaudiólogo | El usuario elige de la lista de arquetipos disponibles (ej. "Trauma Leve", "Presbiacusia Moderada") cuál o cuáles quiere comparar visualmente contra su paciente | CU-03 completado, `precomputed_profiles` disponible | El sistema recupera los arrays ABR de los arquetipos seleccionados | 1 |
| CU-05 | Visualizar Superposición ABR | Fonoaudiólogo | El usuario ve en el gráfico de Plotly.js la onda real del paciente (traza sólida) superpuesta sobre las ondas simuladas de los arquetipos elegidos (trazas punteadas), con sus respectivas latencias y amplitudes | CU-04 completado | Gráfico interactivo renderizado con leyenda por arquetipo | 1 |
| CU-06 | Interpretar y Registrar Hipótesis Diagnóstica | Fonoaudiólogo | El usuario determina visualmente qué arquetipo es morfológicamente más similar al ABR de su paciente y lo registra como hipótesis diagnóstica en el sistema | CU-05 completado | La hipótesis queda vinculada al registro del paciente en la base de datos | 1 |
| CU-07 | Exportar Informe Diagnóstico | Fonoaudiólogo | El usuario genera un PDF con el gráfico de superposición, los metadatos de configuración de cada arquetipo y la hipótesis registrada | CU-06 completado | PDF generado y descargado por el navegador | 1 |
| CU-08 | Búsqueda Automática por Similitud Vectorial | Sistema (IA) | El sistema busca automáticamente los N arquetipos más similares al ABR del paciente sin que el usuario los seleccione manualmente, usando distancia coseno sobre embeddings del `llm-service` | Biblioteca vectorial indexada en ChromaDB / pgvector | Top-3 arquetipos rankeados por score de similitud retornados al frontend | **2 — FUTURA** |

---

## 2. Requerimientos Funcionales

| ID | Nombre | Descripción | Casos de Uso Relacionados | Fase |
|----|--------|-------------|---------------------------|------|
| RF-01 | Validación de Archivo ABR | El `core-service` debe validar que el archivo subido tenga columnas `time` y `amplitude`, una duración mínima de 10 ms y una frecuencia de muestreo compatible (≥ 10 kHz). Si falla, debe retornar un mensaje descriptivo del error al frontend. | CU-02 | 1 |
| RF-02 | Normalización de Señal | El backend debe re-muestrear la señal a 20 kHz, recortarla al ventaneo temporal 0-10 ms y normalizar la amplitud a µV para asegurar compatibilidad con los arquetipos pre-computados en la misma escala. | CU-03 | 1 |
| RF-03 | Listado de Arquetipos Disponibles | El `core-service` debe exponer un endpoint que retorne la lista de arquetipos disponibles en `precomputed_profiles` con su etiqueta clínica, para que el frontend los muestre en el selector. | CU-04 | 1 |
| RF-04 | Recuperación de Arquetipos Seleccionados | El `core-service` debe consultar `precomputed_profiles` para recuperar los arrays ABR (`w1`, `w3`, `w5`, `time_axis`) de los arquetipos que el usuario seleccionó manualmente. | CU-04 | 1 |
| RF-05 | Renderizado de Superposición (Plotly.js) | El frontend debe renderizar la traza del ABR del paciente (negro, línea gruesa) superpuesta a las trazas de los arquetipos seleccionados (colores diferenciados, línea punteada). El tooltip de hover debe mostrar nombre del arquetipo, amplitud en µV y latencia en ms. | CU-05 | 1 |
| RF-06 | Registro de Hipótesis Diagnóstica | El sistema debe permitir al fonoaudiólogo escribir o seleccionar la hipótesis diagnóstica y asociarla al ID del paciente/registro en la base de datos. | CU-06 | 1 |
| RF-07 | Exportación de Informe | El sistema debe generar un PDF que incluya el gráfico de superposición, una tabla con los metadatos de los arquetipos seleccionados y el texto de la hipótesis diagnóstica registrada. | CU-07 | 1 |
| RF-08 | Indexación Vectorial en ChromaDB | El `llm-service` debe ejecutar un proceso batch que vectorice los ABR de todos los arquetipos en `precomputed_profiles` y los indexe en ChromaDB para búsqueda por distancia coseno. | CU-08 | **2 — FUTURA** |
| RF-09 | Búsqueda Automática de Arquetipos Similares | El `llm-service` debe exponer un endpoint que reciba el vector ABR normalizado del paciente y retorne el Top-3 de arquetipos ordenados por score de similitud coseno. | CU-08 | **2 — FUTURA** |

---

## 3. Requerimientos No Funcionales

| ID | Categoría | Descripción | Relación con la Arquitectura | Fase |
|----|-----------|-------------|------------------------------|------|
| RNF-01 | Rendimiento | La carga del listado de arquetipos disponibles y la recuperación de los seleccionados debe tomar menos de 800 ms en total. | Lectura indexada en `precomputed_profiles` (PostgreSQL). | 1 |
| RNF-02 | Seguridad | Los archivos MAT/CSV subidos por el usuario deben pasar por validación de tipo MIME y contenido antes de cualquier procesamiento, para prevenir la ejecución de código malicioso. | Responsabilidad del `core-service`. | 1 |
| RNF-03 | Latencia de Búsqueda Vectorial | La búsqueda de similitud en ChromaDB sobre una biblioteca de hasta 500 arquetipos debe retornar resultados en menos de 300 ms. | `llm-service` con ChromaDB en modo `HNSW`. | **2 — FUTURA** |
| RNF-04 | Escalabilidad de la Biblioteca | El diseño de la base de datos vectorial debe soportar el crecimiento de la biblioteca de arquetipos (hasta 1000+ perfiles) sin requerir re-indexación total. | Arquitectura incremental de ChromaDB. | **2 — FUTURA** |

---

## 4. Diagrama de Relación entre Casos de Uso

```mermaid
useCaseDiagram
    actor "Fonoaudiólogo" as Fono
    package "Apoyo Diagnóstico — Fase 1 (Actual)" {
        usecase "CU-01: Acceder al Módulo" as CU01
        usecase "CU-02: Cargar Registro ABR" as CU02
        usecase "CU-03: Confirmar Señal" as CU03
        usecase "CU-04: Seleccionar Arquetipos Manual" as CU04
        usecase "CU-05: Visualizar Superposición ABR" as CU05
        usecase "CU-06: Registrar Hipótesis" as CU06
        usecase "CU-07: Exportar Informe" as CU07
    }
    package "Apoyo Diagnóstico — Fase 2 (Futura — IA)" {
        usecase "CU-08: Búsqueda Automática por IA" as CU08
    }
    
    Fono --> CU01
    CU01 --> CU02 : <<includes>>
    CU02 --> CU03 : <<includes>>
    CU03 --> CU04 : <<includes>>
    CU04 --> CU05 : <<includes>>
    CU05 --> CU06 : <<extends>>
    CU06 --> CU07 : <<extends>>
    CU03 --> CU08 : <<extends>>
```
