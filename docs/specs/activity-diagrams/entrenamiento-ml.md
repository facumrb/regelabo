# Diagrama de Actividad: Entrenamiento de Inteligencia Artificial (ML)

> **Caso de uso #8:** Entrenamiento de Inteligencia Artificial (Machine Learning)
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Generar un dataset masivo de pares **(perfil auditivo → señal EFR/ABR simulada)** con el modelo Verhulst, para entrenar un modelo de Machine Learning capaz de detectar patrones de pérdida auditiva en nuevos pacientes de forma autónoma.

### Sub-metas / Objetivos intermedios

- **M1:** Definir el espacio de perfiles a simular (todos los perfiles del catálogo + variantes de fibras AN).
- **M2:** Ejecutar la generación masiva del dataset (funcionalidad #2 como paso base).
- **M3:** Exportar el dataset en formato compatible con frameworks de ML (CSV, NumPy, HDF5).
- **M4:** Documentar el dataset (metadatos, distribución de clases, parámetros) para reproducibilidad.

### Clasificación en la taxonomía del proyecto

```
Meta Principal: Simulación EFR (Verhulst 2018)
└── Sub-meta: Entrenamiento de IA / ML  ← esta
    ├── M1: Definición del espacio de datos
    ├── M2: Generación masiva (via #2 — Datos Sintéticos)
    ├── M3: Exportación en formato ML
    └── M4: Documentación del dataset
```

> [!IMPORTANT]
> Esta funcionalidad es un **superconjunto de #2 (Datos Sintéticos)** con una capa adicional de organización y exportación orientada a ML. El investigador de ML no interactúa directamente con la simulación: primero un fonoaudiólogo o investigador de audiología define los perfiles clínicamente relevantes, y luego el dataset se exporta.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `║` = Barra de sincronización
- `╔═══╗` = Actividad compuesta (caja negra)

### Flujo principal

```
[●] INICIO
  │
  ▼
[1. Investigador accede al módulo "Generación de Dataset para ML"]
  │
  ▼
[2. Define el objetivo del dataset:
     - ¿Clasificación de pérdida? (ej. normal vs. Flat20 vs. Slope20)
     - ¿Regresión? (predecir grado de pérdida)
     - ¿Detección de sinaptopatía? (nH normal vs. reducido)
     → Esto determina qué perfiles y variantes incluir como "clases"]
  │
  ▼
[3. Configura la grilla del dataset:
     - Perfiles OHC: [Flat00, Flat20, Flat40, Flat60, Flat80,
                       Slope20, Slope30, Slope45, Slope60...]
     - Variantes AN: [{nH:13,nM:3,nL:3}, {nH:7,...}, {nH:1,...}]
     - Estímulos: [RAM(fc=4kHz, fm=98Hz, 65dB), RAM(fc=2kHz, fm=80Hz, 70dB)]
     → Total pares de entrenamiento: N_perfiles × N_AN × N_estimulos]
  │
  ▼
[4. Define la etiqueta (label) para cada combinación:
     - Etiqueta de clase (ej. "Normal", "Flat Leve", "Sinaptopatía Severa")
     - Etiquetas numéricas (ej. grado de pérdida en dB, valor nH)
     - Metadatos adicionales: perfil_name, nH, nM, nL, tipo_estimulo]
  │
  ▼
[5. Sistema calcula: N total de simulaciones = |perfiles| × |AN| × |estímulos|
    Muestra estimación de tiempo y espacio en disco]
  │
  ▼
<6. ¿Confirma la generación del dataset?>
  │                  │
  │ Sí               │ No → [Ajustar grilla] → paso 3
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  7. GENERACIÓN MASIVA DEL DATASET (CAJA NEGRA)             ║
║  ─────────────────────────────────────────────────────────  ║
║  [Reutiliza la funcionalidad #2 — Datos Sintéticos]        ║
║  Entrada: N combinaciones (perfil, estímulo, fibras AN)     ║
║  Salida: N × {EFR (µV), w1[], w3[], w5[], etiqueta}        ║
║                                                             ║
║  Ver verhulst-analysis/entrenamiento-ml.md                  ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error parcial → [Registrar, continuar con exitosas]
  │
  ▼
[8. Sistema muestra progreso:
     - Simulaciones completadas / totales
     - Distribución de clases completadas hasta el momento]
  │
  ▼
<9. ¿Dataset completo?>
  │        │
  │ No     │ Sí
  │ (espera)│
  ▼         ▼
[Polling  [10. Sistema estructura el dataset para ML:
continúa]       - CSV: columnas [id, perfil, nH, nM, nL, fm, nivel, EFR_uV, label]
                - Arrays: directorio con .npy por señal ABR completa
                - HDF5: un archivo unificado con datasets/X y datasets/y]
          │
          ▼
         [11. Sistema genera report de distribución del dataset:
               - Histograma de clases (balance/desbalance)
               - Estadísticas descriptivas de EFR por clase
               - N de ejemplos por perfil]
          │
          ▼
         [12. Investigador revisa distribución y decide si está balanceado]
          │
          ▼
         <13. ¿El dataset está suficientemente balanceado?>
           │                    │
           │ Sí                 │ No → [Ajustar grilla para equilibrar
           │                           clases subrepresentadas] → paso 3
           │
           ▼
          [14. Exporta dataset final:
                - Formato elegido (CSV / NumPy .npy / HDF5)
                - README del dataset con descripción de columnas,
                  distribución de clases y parámetros de generación]
           │
           ▼
          [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 6 | ¿Confirmar generación? | Sí → ejecutar | No → ajustar grilla |
| 7 | Generación masiva | OK → estructurar | Error parcial → registrar, continuar |
| 9 | ¿Dataset completo? | No → polling | Sí → estructurar para ML |
| 13 | ¿Dataset balanceado? | Sí → exportar | No → ajustar grilla, re-generar clases faltantes |
