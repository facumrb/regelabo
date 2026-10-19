# Diagrama de Actividad: Optimizar Parámetros de Estímulo

> **Caso de uso #4:** Optimizar parámetros de estímulo
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Encontrar la configuración de estímulo (frecuencia portadora, frecuencia de modulación, nivel SPL, tipo) que produce la mayor amplitud de EFR para un perfil auditivo dado, con el objetivo de diseñar protocolos de medición clínica más sensibles.

### Sub-metas / Objetivos intermedios

- **M1:** Definir el perfil auditivo base sobre el que se va a optimizar.
- **M2:** Especificar el espacio de búsqueda del estímulo (rango de parámetros a barrer).
- **M3:** Ejecutar el barrido sistemático de configuraciones.
- **M4:** Identificar qué configuración maximiza la señal EFR.
- **M5:** Exportar los parámetros óptimos para usar en equipos clínicos reales.

### Clasificación en la taxonomía del proyecto

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Optimizar parámetros de estímulo  ← esta
│   ├── M1: Definir perfil auditivo base
│   ├── M2: Definir espacio de búsqueda (grilla de parámetros)
│   ├── M3: Barrido sistemático (lote de simulaciones)
│   └── M4: Identificar óptimo
└── [Depende de: #2 (Datos Sintéticos) para la ejecución en lote]
```

> [!NOTE]
> **Limitación actual:** Solo los estímulos RAM son soportados por `get_RAM_stims.py`. Clicks y tone bursts están disponibles pero el barrido está principalmente diseñado para EFR con RAM. La funcionalidad de optimización se enfoca en EFR RAM hasta que se extienda el generador de estímulos.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `╔═══╗` = Actividad compuesta (caja negra)

### Flujo principal

```
[●] INICIO
  │
  ▼
[1. Investigador accede al módulo "Optimización de Estímulo"]
  │
  ▼
[2. Selecciona el perfil auditivo a optimizar:
     - "Normal" (Flat00) — encontrar mejor estímulo para screening estándar
     - Patológico (ej. Flat40) — encontrar estímulo más sensible para ese daño
     - Personalizado via audiograma]
  │
  ▼
[3. Configura las fibras AN (default normativo o personalizado)]
  │
  ▼
[4. Define el ESPACIO DE BÚSQUEDA del estímulo:
    - Tipo de estímulo: [✓] RAM (obligatorio para EFR), [ ] Click, [ ] Tone Burst
    - Frecuencia portadora fc: rango [Hz] con paso (ej. 1000-8000 Hz, paso 1000)
    - Frecuencia de modulación fm: rango [Hz] con paso (ej. 80-200 Hz, paso 20)
    - Nivel SPL: rango [dB] con paso (ej. 50-80 dB, paso 5)
    → El sistema calcula: N combinaciones = |fc| × |fm| × |nivel|]
  │
  ▼
[5. Sistema muestra resumen: "Se ejecutarán N simulaciones. Tiempo estimado: X horas"]
  │
  ▼
<6. ¿Confirma el barrido?>
  │                │
  │ Sí             │ No → [Ajustar espacio de búsqueda] → paso 4
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  7. BARRIDO EN LOTE: N SIMULACIONES RAM (CAJA NEGRA)       ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada: perfil fijo + N combinaciones de (fc, fm, nivel)  ║
║  Salida:  N × EFR (µV) [+ opcionalmente w1, w3, w5]        ║
║                                                             ║
║  Ver verhulst-analysis/optimizacion-estimulos.md            ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error parcial → [Registrar fallos, continuar con exitosas]
  │
  ▼
[8. Sistema muestra panel de resultados del barrido:
     - Heatmap EFR (µV) con ejes fc vs. fm (o fc vs. nivel)
     - Punto máximo destacado: "EFR óptimo = X µV en fc=4kHz, fm=98Hz, nivel=65dB"
     - Curva de EFR vs. fc para fm fija (y viceversa)]
  │
  ▼
[9. Investigador identifica visualmente la región de máximo EFR]
  │
  ▼
<10. ¿Desea afinar la búsqueda en la región óptima (sub-barrido)?>
  │                               │
  │ Sí                            │ No
  ▼                               │
[10a. Ajusta espacio de búsqueda  │
  a subconjunto del rango         │
  óptimo identificado y           │
  vuelve a paso 4 con             │
  mayor resolución]               │
                                  ▼
                                 [11. Exporta resultados:
                                       - CSV completo del barrido (fc, fm, nivel, EFR)
                                       - Imagen del heatmap
                                       - Parámetros óptimos en JSON para uso en equipo]
                                  │
                                  ▼
                                 [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 6 | ¿Confirmar barrido? | Sí → ejecutar N simulaciones | No → ajustar espacio de búsqueda |
| 7 | Barrido en lote | OK → mostrar heatmap | Error parcial → registrar, continuar |
| 10 | ¿Sub-barrido de afinación? | Sí → reducir espacio, mayor resolución | No → exportar resultados |
