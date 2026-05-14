# Diagrama de Actividad: Apoyo Diagnóstico por Arquetipos Clínicos

> **Caso de uso #16:** Apoyo Diagnóstico por Arquetipos Clínicos (Clasificación Vectorial)
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Dado el registro ABR real de un paciente con pérdida auditiva de causa incierta, el fonoaudiólogo obtiene un **indicio diagnóstico instantáneo** al compararlo automáticamente contra una biblioteca de "arquetipos clínicos" pre-simulados, sin necesidad de correr una nueva simulación ni de conocimientos de IA.

### Sub-metas / Objetivos intermedios

- **M1:** Cargar el ABR real del paciente al sistema.
- **M2:** El sistema busca el arquetipo más parecido en la biblioteca pre-computada.
- **M3:** Ver el reporte de coincidencia y la superposición gráfica del ABR real vs. el arquetipo sugerido.
- **M4:** Interpretar el resultado como hipótesis diagnóstica ("el paciente se parece al Arquetipo de Trauma Acústico").

### Clasificación en la taxonomía del proyecto

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Apoyo Diagnóstico por Arquetipos Clínicos  ← esta
│   ├── M1: Ingestión de ABR real del paciente
│   ├── M2: Búsqueda vectorial en biblioteca de arquetipos
│   ├── M3: Visualización de coincidencia
│   └── M4: Interpretación diagnóstica
└── Sub-meta: Datos Sintéticos en Lote (#2) [proveedor de arquetipos]
```

> [!IMPORTANT]
> Esta funcionalidad es **consumidora** de los datos generados por el caso #2 (lote masivo). La biblioteca de arquetipos debe estar pre-computada antes de que esta funcionalidad pueda usarse. No invoca `model2018()` en tiempo real durante la búsqueda.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `→` = Flujo
- `╔═══╗` = Actividad compuesta (caja negra — aquí: búsqueda vectorial)

### Flujo principal

```
[●] INICIO
  │
  ▼
[1. Fonoaudiólogo accede al módulo "Apoyo Diagnóstico — Arquetipos Clínicos"]
  │
  ▼
[2. Sistema presenta interfaz de carga de datos del paciente]
  │
  ▼
<3. ¿Cómo provee el ABR del paciente?>
  │                                        │
  │ [Archivo de equipo BERA real]          │ [Datos previamente registrados en el sistema]
  ▼                                        ▼
[3a. Sube archivo MAT/CSV/EDF             [3b. Busca y selecciona el registro
  con las ondas ABR reales del paciente]     del paciente en el histórico del sistema]
  │                                        │
  ▼                                        │
[3a.1 Sistema valida formato del archivo:  │
   - Columnas: time[], amplitude[]         │
   - Duración mínima y frecuencia          │
     de muestreo adecuada]                 │
  │                                        │
<3a.2 ¿Archivo válido?>                   │
  │           │                            │
  │ Sí        │ No → [Mostrar error,       │
  │           │       volver a 3a]         │
  │           │                            │
  ▼           ▼                            ▼
[4. Sistema normaliza la señal ABR recibida:
     - Re-muestreo al fs estándar (20 kHz) si es necesario
     - Ventaneo temporal al intervalo estándar (0-10 ms)
     - Normalización de amplitud (µV)]
  │
  ▼
[5. Fonoaudiólogo revisa previsualización de la señal cargada
    y confirma que es la onda correcta]
  │
  ▼
<6. ¿Confirma la señal cargada?>
  │                     │
  │ Sí                  │ No → [Volver a cargar, paso 3]
  │
  ▼
[7. Fonoaudiólogo (opcionalmente) filtra la biblioteca:
     - Solo buscar en arquetipos de "pérdida plana"
     - Solo buscar en arquetipos de "pérdida en pendiente"
     - Solo buscar en arquetipos de "sinaptopatía"
     - Buscar en todos (default)]
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  8. BÚSQUEDA POR SIMILITUD VECTORIAL (CAJA NEGRA)          ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada: vector ABR normalizado del paciente               ║
║  Proceso: búsqueda coseno en pgvector (PostgreSQL)          ║
║           contra biblioteca de K arquetipos pre-indexados   ║
║  Salida:  Top-N arquetipos con score de similitud           ║
║                                                             ║
║  Ver verhulst-analysis/arquetipos-clinicos-diagnostico.md   ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error (DB no disponible / biblioteca vacía)
  │            ▼
  │      [8a. Mostrar mensaje de error:
  │       "Biblioteca de arquetipos no disponible.
  │        Contacte al administrador del sistema."] → FIN
  │
  ▼
[9. Sistema muestra reporte de coincidencia:
     Top-3 arquetipos más similares, ordenados por score:

     ┌─────────────────────────────────────────────────────┐
     │  #1 Trauma Acústico Moderado         85% similitud │
     │  #2 Sinaptopatía Coclear Leve        72% similitud │
     │  #3 Pérdida Plana 20dB               58% similitud │
     └─────────────────────────────────────────────────────┘]
  │
  ▼
[10. Plotly.js renderiza superposición gráfica:
       - Traza principal: ABR real del paciente (negro, grueso)
       - Traza superpuesta: ABR del Arquetipo #1 (color, punteado)
       - Panel de métricas: EFR, latencias W1/W3/W5 de ambos]
  │
  ▼
<11. ¿Desea ver el detalle de otro arquetipo del top-3?>
  │                     │
  │ Sí → selecciona     │ No
  │ #2 o #3 y vuelve    │
  │ a paso 10           │
                         ▼
                        [12. Fonoaudiólogo interpreta el reporte:
                              - ¿El arquetipo sugerido tiene sentido clínico?
                              - ¿El overlay visual confirma morfología similar?
                              - Registra la hipótesis diagnóstica en el sistema]
                         │
                         ▼
                        [13. Exporta informe diagnóstico:
                              PDF con gráfico de overlay + tabla de arquetipos
                              + metadatos del paciente]
                         │
                         ▼
                        [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 3 | ¿Cómo provee el ABR? | Sube archivo nuevo | Selecciona registro existente |
| 3a.2 | ¿Archivo válido? | Sí → continuar | No → mostrar error, volver |
| 6 | ¿Confirma señal? | Sí → continuar | No → volver a cargar |
| 8 | Búsqueda vectorial | OK → mostrar resultados | Error → mensaje, fin |
| 11 | ¿Ver otro arquetipo? | Sí → seleccionar del top-3 | No → interpretar y exportar |

---

## 3. Nota: Pre-condición de la Biblioteca

> [!WARNING]
> **Esta funcionalidad requiere que la biblioteca de arquetipos esté pre-computada.** Si el `batch_id` de la generación masiva no existe o está vacío, la búsqueda retornará error. El flujo de generación de la biblioteca es el de la funcionalidad #2 (Datos Sintéticos en Lote), ejecutado con la grilla de perfiles estándar del proyecto.

```
PRE-CONDICIÓN:
  Funcionalidad #2 ejecutada exitosamente
  → K arquetipos indexados en pgvector (PostgreSQL)
  → ENTONCES esta funcionalidad está disponible

DEPENDENCIA:
  archetypal_library.status = 'populated'
  archetypal_library.count >= MIN_ARCHETYPES (ej: 33 perfiles × 5 variantes fibras = 165)
```
