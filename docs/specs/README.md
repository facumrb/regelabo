# Índice de Especificaciones — Análisis de Funcionalidades Verhulst

> **Proyecto:** Regelabo — Laboratorio Virtual Auditivo
> **Modelo central:** Verhulst et al. 2018
> **Actualizado:** 2026-05-12

---

## Estructura de Carpetas

```
docs/specs/
├── README.md                        ← este archivo (índice)
├── functionalitiesOverview.md       ← lista canónica de casos de uso
├── analisisScreeningNeonatal.md     ← análisis de referencia (formato unificado, legacy)
├── Integration Points Bera Abr.md  ← puntos técnicos de integración ABR
│
├── activity-diagrams/               ← Diagramas de actividad del fonoaudiólogo
│   ├── screening-neonatal.md       ← separado del doc legacy
│   ├── datos-sinteticos-ml.md
│   ├── hipotesis-sordera-oculta.md
│   ├── sordera-oculta-edad-trauma.md
│   ├── arquetipos-clinicos-diagnostico.md
│   ├── mecanismos-fisiologicos.md
│   ├── optimizacion-estimulos.md
│   ├── validacion-datos-clinicos.md
│   └── entrenamiento-ml.md
│
└── verhulst-analysis/               ← Análisis de uso del modelo Verhulst
    ├── screening-neonatal.md       ← separado del doc legacy via /speckit.analyze
    ├── datos-sinteticos-ml.md
    ├── hipotesis-sordera-oculta.md
    ├── sordera-oculta-edad-trauma.md
    ├── arquetipos-clinicos-diagnostico.md
    ├── mecanismos-fisiologicos.md
    ├── optimizacion-estimulos.md
    ├── validacion-datos-clinicos.md
    └── entrenamiento-ml.md
```

---

## Tabla de Estado de Análisis

| # | Funcionalidad | Factibilidad | DA Fonoaudiólogo | Análisis Verhulst |
|---|---|---|---|---|
| 1 | Estudiar mecanismos fisiológicos | ✅ Directa | [mecanismos-fisiologicos](activity-diagrams/mecanismos-fisiologicos.md) | [mecanismos-fisiologicos](verhulst-analysis/mecanismos-fisiologicos.md) |
| 2 | Generar datos sintéticos controlados | ✅ Directa | [datos-sinteticos-ml](activity-diagrams/datos-sinteticos-ml.md) | [datos-sinteticos-ml](verhulst-analysis/datos-sinteticos-ml.md) |
| 3 | Explorar hipótesis sordera oculta | ✅ Directa | [hipotesis-sordera-oculta](activity-diagrams/hipotesis-sordera-oculta.md) | [hipotesis-sordera-oculta](verhulst-analysis/hipotesis-sordera-oculta.md) |
| 4 | Optimizar parámetros de estímulo | ✅ Directa | [optimizacion-estimulos](activity-diagrams/optimizacion-estimulos.md) | [optimizacion-estimulos](verhulst-analysis/optimizacion-estimulos.md) |
| 5 | Validar modelos con datos clínicos reales | ✅ Directa | [validacion-datos-clinicos](activity-diagrams/validacion-datos-clinicos.md) | [validacion-datos-clinicos](verhulst-analysis/validacion-datos-clinicos.md) |
| 8 | Entrenamiento de IA (Machine Learning) | ✅ Directa | [entrenamiento-ml](activity-diagrams/entrenamiento-ml.md) | [entrenamiento-ml](verhulst-analysis/entrenamiento-ml.md) |
| 9 | Investigación en Screening Neonatal (BERA/ABR) | ✅ Directa | [screening-neonatal](activity-diagrams/screening-neonatal.md) | [screening-neonatal](verhulst-analysis/screening-neonatal.md) |
| 12 | Sordera Oculta: Edad vs. Trauma Acústico | ✅ Directa | [sordera-oculta-edad-trauma](activity-diagrams/sordera-oculta-edad-trauma.md) | [sordera-oculta-edad-trauma](verhulst-analysis/sordera-oculta-edad-trauma.md) |
| 16 | Apoyo Diagnóstico por Arquetipos Clínicos | ✅ Directa | [arquetipos-clinicos-diagnostico](activity-diagrams/arquetipos-clinicos-diagnostico.md) | [arquetipos-clinicos-diagnostico](verhulst-analysis/arquetipos-clinicos-diagnostico.md) |
| 10 | Percepción de Habla en Ruido | ⚠️ Parcial | *(pendiente)* | *(pendiente)* |
| 14 | Beneficio de Audífonos | ⚠️ Parcial | *(pendiente)* | *(pendiente)* |
| 15 | Seguimiento del Habla | ⚠️ Parcial | *(pendiente)* | *(pendiente)* |
| 6 | Optimización de Implantes Cocleares | ❌ No factible | *(no planificado)* | *(no planificado)* |
| 7 | Audiología de Precisión / Gemelo Digital | ❌ No factible | *(no planificado)* | *(no planificado)* |
| 11 | Modelado del Tinnitus | ❌ No factible | *(no planificado)* | *(no planificado)* |
| 13 | Latencia Binaural | ❌ No factible | *(no planificado)* | *(no planificado)* |

---

## Mapa de Dependencias entre Funcionalidades

```
#2 (Datos Sintéticos en Lote)
  ├──→ #8 (Entrenamiento ML) [consumidor del CSV masivo]
  └──→ #16 (Arquetipos Clínicos) [consumidor del vector ABR indexado]

#3 (Hipótesis Sordera Oculta)
  └──→ #12 (Edad vs. Trauma) [especialización del experimento comparativo]

#9 (Screening Neonatal)
  └── Comparte infraestructura con #1, #3, #4, #5 [mismo endpoint /simulate]
```

---

## Cómo Agregar un Nuevo Análisis

Usar el comando del agente: `/speckit.analyze` (ver [workflow](../../.agents/workflow/speckit.analyze.md))

```
/speckit.analyze
funcionalidad_numero: <N>
funcionalidad_nombre: <nombre>
nombre_archivo: <slug>
```

El agente generará automáticamente los dos documentos y actualizará este índice.
