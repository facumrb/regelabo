# Diagrama de Actividad: Estudiar Mecanismos Fisiológicos del Oído Interno

> **Caso de uso #1:** Estudiar mecanismos fisiológicos
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Aislar y observar el comportamiento de una etapa específica del oído interno (cóclea, célula ciliada interna, sinapsis, núcleo coclear, colículo inferior) cuando una estructura falla, algo imposible de hacer en un paciente humano real.

### Sub-metas / Objetivos intermedios

- **M1:** Seleccionar qué estructura biológica se quiere estudiar (OHC, IHC, AN, CN, IC).
- **M2:** Configurar el daño específico de esa estructura (perfil OHC o reducción de fibras).
- **M3:** Elegir qué etapa del pipeline registrar como salida (`storeflag`).
- **M4:** Comparar la respuesta de la estructura ante un oído sano vs. el oído con la patología configurada.

### Clasificación en la taxonomía del proyecto

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Estudiar mecanismos fisiológicos  ← esta
│   ├── M1: Selección de etapa biológica objetivo
│   ├── M2: Configuración del daño
│   ├── M3: Registro de salida específica (storeflag)
│   └── M4: Comparación sano vs. patológico
└── [Base metodológica de todas las demás funcionalidades]
```

> [!NOTE]
> Esta es la funcionalidad más "de laboratorio" de todas. Su usuario es principalmente un **investigador** (no necesariamente un clínico). El módulo actúa como un osciloscopio biológico: se puede enfocar en cualquier etapa del pipeline.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `→` = Flujo
- `╔═══╗` = Actividad compuesta (caja negra)

### Flujo principal

```
[●] INICIO
  │
  ▼
[1. Investigador accede al módulo "Exploración de Mecanismos Fisiológicos"]
  │
  ▼
[2. Sistema presenta panel de configuración de experimento]
  │
  ▼
[3. Investigador selecciona la ETAPA BIOLÓGICA a estudiar:
    ○ Cóclea — Velocidad de membrana basilar (BM)
    ○ Célula Ciliada Interna (IHC) — Potencial de membrana
    ○ Nervio Auditivo (AN) — Tasas de disparo
    ○ Núcleo Coclear (CN) — Respuesta CN
    ○ Colículo Inferior (IC) — Respuesta IC (onda W5)
    ○ ABR completo — Ondas W1, W3, W5]
  │
  ▼
[4. Investigador define el DAÑO a simular:

    <4a. ¿Qué estructura está dañada?>
     │                          │
     │ [Cóclea — OHC]           │ [Sinapsis — Fibras AN]
     ▼                          ▼
    [4a-OHC: selecciona         [4a-AN: configura nH, nM, nL
     perfil de polos             con reducción específica
     (Flat00..Flat80,            ej. nH=7, nM=3, nL=3
     Slope15..Slope80)]          para sinaptopatía]
     │                           │
     ▼                           ▼
    [Carga sheraP del           [Mantiene sheraP de Flat00
     perfil seleccionado]        (OHC sana) + aplica reducción AN]]

  │
  ▼
[5. Selecciona el estímulo de entrada:
     Tipo (click, tono puro, RAM), frecuencia, nivel dB SPL, duración]
  │
  ▼
<6. ¿Desea incluir perfil SANO como referencia de comparación?>
  │               │
  │ Sí            │ No
  ▼               │
[6a. Sistema agrega    │
  simulación paralela  │
  con Flat00 + AN      │
  normativos]          │
  │               │
  ▼               ▼
[7. Investigador presiona "Ejecutar experimento"]
  │
  ▼
[8. Sistema valida configuración]
  │
  ▼
<9. ¿Configuración válida?>
  │           │
  │ Sí        │ No → [Mostrar errores] → volver a 4
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  10. PIPELINE VERHULST — SALIDA ESPECÍFICA (CAJA NEGRA)    ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada: sheraP, nH/nM/nL, estímulo, storeflag elegido    ║
║  Salida:  etapa biológica seleccionada en paso 3            ║
║           [+ misma etapa del perfil sano si se eligió]      ║
║                                                             ║
║  Ver verhulst-analysis/mecanismos-fisiologicos.md           ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error → [Registrar, notificar] → FIN
  │
  ▼
[11. Frontend renderiza visualización específica según la etapa elegida:
      - BM velocity: gráfico de velocidad vs. lugar coclear (frecuencia)
      - IHC: potencial de membrana vs. tiempo por canal de frecuencia
      - AN: rasterplot o PSTH de tasas de disparo
      - CN/IC: ondas temporales por población neuronal
      - ABR: trazas W1, W3, W5]
  │
  ▼
[12. Si se incluyó perfil sano (paso 6):
      Superpone ambas trazas (sano vs. patológico) en el mismo gráfico
      con diferente color]
  │
  ▼
[13. Investigador interpreta:
      ¿En qué etapa se origina la diferencia?
      ¿El daño OHC afecta antes o después que el daño AN?
      ¿La respuesta IC se preserva cuando la AN falla?]
  │
  ▼
<14. ¿Desea modificar el daño o la etapa a observar y re-ejecutar?>
  │                    │
  │ Sí → volver a 3    │ No
                        │
                        ▼
                       [15. Exporta gráfico + datos crudos de la etapa]
                        │
                        ▼
                       [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 4a | ¿Qué estructura está dañada? | OHC (polos Shera) | Fibras AN (nH/nM/nL) |
| 6 | ¿Incluir perfil sano de referencia? | Sí → simulación paralela | No → solo perfil patológico |
| 9 | ¿Configuración válida? | Sí → ejecutar | No → errores, volver |
| 10 | Pipeline Verhulst | OK → visualizar | Error → registrar, fin |
| 14 | ¿Re-ejecutar? | Sí → loop a 3 | No → exportar, fin |
