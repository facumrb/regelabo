# Diagrama de Actividad: Generar Datos Sintéticos Controlados

> **Caso de uso #2:** Generar datos sintéticos controlados
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Crear grandes conjuntos de datos de pacientes virtuales con perfiles auditivos exactamente definidos, para experimentos de validación de herramientas de diagnóstico, entrenamiento de modelos estadísticos o publicaciones de investigación.

### Sub-metas / Objetivos intermedios

- **M1:** Definir la grilla de simulación (qué perfiles × estímulos × niveles se van a simular).
- **M2:** Lanzar el proceso de simulación en lote sin necesidad de supervisión continua.
- **M3:** Obtener los resultados (EFR, ABR, etc.) en formato exportable (CSV / MAT).
- **M4:** Acceder a los datos generados para análisis estadístico externo.

### Clasificación en la taxonomía del proyecto

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Generar datos sintéticos controlados  ← esta
│   ├── M1: Definir grilla de simulación
│   ├── M2: Ejecutar en lote (pipeline paralelo)
│   ├── M3: Exportar resultados (CSV/MAT)
│   └── M4: Acceder y analizar datos generados
├── Sub-meta: Screening Neonatal BERA/ABR
├── Sub-meta: Sordera Oculta
└── Sub-meta: Entrenamiento ML
```

> [!NOTE]
> Esta funcionalidad es la **base de datos** de la que se alimentan las funcionalidades #8 (ML) y #16 (Arquetipos Clínicos). Su generación masiva y automatizada es crítica para el ecosistema del laboratorio.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `→` = Flujo
- `║` = Barra de sincronización (fork/join paralelo)
- `╔═══╗` = Actividad compuesta (caja negra)

### Flujo principal

```
[●] INICIO
  │
  ▼
[1. Investigador accede al módulo "Generación de Datos Sintéticos"]
  │
  ▼
[2. Sistema presenta formulario de configuración de grilla]
  │
  ▼
<3. ¿Cómo selecciona los perfiles auditivos?>
  │                                        │
  │ [Perfiles pre-computados del catálogo] │ [Audiogramas personalizados]
  ▼                                        ▼
[3a. Selecciona uno o más perfiles       [3b. Sube archivo CSV/JSON con
 del catálogo (Flat00..Flat80,            múltiples audiogramas
 Slope15..Slope80, etc.)]                 {id, freqs[], dB[]}]
  │                                        │
  │                                        ▼
  │                                  [3b.1 Sistema valida formato:
  │                                   - columnas correctas (id, freqs, dB)
  │                                   - rangos válidos por fila]
  │                                        │
  │                                  <3b.2 ¿Archivo válido?>
  │                                    │           │
  │                                    │ Sí        │ No
  │                                    │           ▼
  │                                    │    [Mostrar errores por fila,
  │                                    │     volver a 3b]
  │                                    │
  ▼                                    ▼
[4. Configura parámetros de fibras AN para todos los sujetos:
     nH, nM, nL — valor único o rango con paso (ej. nH: 13, nM: 3, nL: 3)]
  │
  ▼
[5. Define los estímulos de la grilla:
     Tipo (RAM/click/tone), frecuencias portadoras, niveles dB SPL]
  │
  ▼
[6. Define las salidas a almacenar: EFR, w1/w3/w5, an_sout, BM]
  │
  ▼
[7. Revisa resumen de grilla: N sujetos × M estímulos = K simulaciones totales]
  │
  ▼
<8. ¿Confirma lanzar el lote?>
  │                │
  │ Sí             │ No → [Volver a ajustar grilla] → paso 4
  │
  ▼
[9. Sistema crea K tareas Celery en cola de ejecución paralela]
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  10. PIPELINE DE SIMULACIÓN VERHULST EN LOTE (CAJA NEGRA) ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada: K combinaciones (perfil auditivo, estímulo,      ║
║           config fibras AN)                                ║
║  Salida:  K resultados (EFR, w1[], w3[], w5[], etc.)       ║
║                                                             ║
║  Ver verhulst-analysis/datos-sinteticos-ml.md              ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error parcial (algunas simulaciones fallan)
  │            ▼
  │      [10a. Registrar simulaciones fallidas con detalle de error
  │       Continuar con las exitosas]
  │            │
  ▼            ▼
[11. Sistema muestra panel de progreso:
      - Simulaciones completadas / totales
      - Simulaciones con error
      - Tiempo transcurrido / estimado]
  │
  ▼
<12. ¿Todas las simulaciones del lote completadas?>
  │                │
  │ No             │ Sí
  │ (espera)       │
  ▼                ▼
[Polling          [13. Sistema genera archivos exportables:
 continúa]              - CSV con columnas: sujeto_id, perfil, estímulo, EFR, ...
                         - MAT con arrays completos por simulación
                         - JSON con metadatos del lote]
                   │
                   ▼
                  [14. Investigador descarga los archivos generados]
                   │
                   ▼
                  <15. ¿Desea lanzar otro lote con parámetros diferentes?>
                    │                    │
                    │ Sí → volver a 4    │ No
                                         │
                                         ▼
                                        [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 3 | Fuente de perfiles auditivos | Pre-computados del catálogo | Audiogramas personalizados (upload) |
| 3b.2 | ¿Archivo válido? | Sí → continuar | No → mostrar errores, volver |
| 8 | ¿Confirma lote? | Sí → encolar K tareas | No → volver a ajustar |
| 10 | Pipeline en lote | OK (todas ok) | Error parcial → registrar y continuar |
| 12 | ¿Lote completo? | No → polling | Sí → exportar |
| 15 | ¿Otro lote? | Sí → loop a paso 4 | No → fin |

---

## 3. Subdiagrama: Estrategia de Paralelismo del Lote

> [!IMPORTANT]
> El pipeline paralelo de Verhulst (`ParallelRAMSimulationsEFR.py`) puede ejecutar múltiples simulaciones simultáneamente. El DA interno muestra cómo se distribuyen las K tareas.

```
[●] INICIO (desde paso 9 del DA principal)
  │
  ▼
[P1. Sistema construye lista de K combinaciones (perfil, estímulo, fibras)]
  │
  ▼
║ FORK: distribuir K tareas a workers disponibles ║
  │       │           │               │
  ▼       ▼           ▼               ▼
[P2a.   [P2b.       [P2c.           [P2d.
 Task1]  Task2]      Task3]          Task_K]
  │       │           │               │
  ▼       ▼           ▼               ▼
[Cada worker ejecuta:
  - Cargar sheraP del perfil
  - Generar estímulo
  - model2018(stim, fs, sheraP, nH, nM, nL, storeflag, fc)
  - Extraer salidas configuradas
  - Persistir en DB + Storage]
  │
║ JOIN: esperar a que todas las tareas finalicen (o timeout) ║
  │
  ▼
[P3. Agregar resultados + generar CSV/MAT de lote]
  │
  ▼
[●] FIN (retorna a paso 11 del DA principal)
```
