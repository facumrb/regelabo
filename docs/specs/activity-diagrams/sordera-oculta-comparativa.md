# Diagrama de Actividad: Sordera Oculta — Edad vs. Trauma Acústico

> **Caso de uso #12:** Sordera Oculta: Edad vs. Trauma Acústico
> **Fecha:** 2026-08-04 | **Revisión:** v2
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Diferenciar, desde la firma eléctrica (EFR y morfología ABR), dos fenotipos clínicos de sordera oculta que superficialmente comparten características similares en el audiograma: la **presbiacusia** (degradación lenta y gradual de las células ciliadas externas por envejecimiento) frente al **trauma acústico súbito** (destrucción sináptica severa con cóclea aparentemente intacta).

### Sub-metas / Objetivos intermedios

- **M1:** Configurar el fenotipo "Envejecimiento" usando perfiles `Slope` con fibras nerviosas normales (el daño está en la cóclea).
- **M2:** Configurar el fenotipo "Trauma Acústico" usando el perfil coclear `Flat00` (cóclea sana) con fibras AN fuertemente reducidas (el daño está en la sinapsis).
- **M3:** Comparar la amplitud del EFR entre ambos fenotipos para identificar si la caída de señal es diferenciable.
- **M4:** Analizar morfológicamente las ondas W1, W3 y W5 del ABR para observar si el lugar del daño deja una huella distinta en el recorrido de la señal hacia el cerebro.

### Clasificación en la taxonomía del proyecto

```text
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Análisis comparativo de fenotipos  ← esta
│   ├── M1: Configuración de Fenotipo Envejecimiento (Slope + AN normales)
│   ├── M2: Configuración de Fenotipo Trauma (Flat00 + AN reducidas)
│   ├── M3: Comparación de amplitud EFR entre ambos fenotipos
│   └── M4: Análisis morfológico W1, W3, W5 del ABR
└── [Funcionalidad base para diseño de pruebas diferenciales futuras]
```

> [!NOTE]
> Esta funcionalidad es el caso de uso "clínico comparativo" más representativo de la plataforma. Ningún audiograma convencional puede distinguir estos dos fenotipos — solo el EFR simulado puede hacerlo.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `→` = Flujo
- `╔═══╗` = Actividad compuesta (caja negra / microservicio)

### Flujo principal

```text
[●] INICIO
  │
  ▼
[1. Investigador accede al módulo "Análisis Comparativo de Fenotipos"]
  │
  ▼
[2. Investigador configura el estímulo acústico de evaluación:
    ○ Tipo: RAM (por defecto)
    ○ Frecuencia portadora: 4 kHz (por defecto)
    ○ Nivel: 65 dB SPL (por defecto)]
  │
  ▼
[3. Investigador selecciona el FENOTIPO A — "Envejecimiento (Presbiacusia)":

    <3a. ¿Qué nivel de envejecimiento coclear?>
    │
    ├── Leve    → Slope15 (15 dB pérdida en agudos), nH=13, nM=3, nL=3
    ├── Moderado → Slope25 (25 dB pérdida en agudos), nH=13, nM=3, nL=3
    └── Severo   → Slope35_5 (35 dB pérdida en agudos), nH=13, nM=3, nL=3]
  │
  ▼
[4. Investigador selecciona el FENOTIPO B — "Trauma Acústico Súbito (Sinaptopatía)":

    <4a. ¿Qué nivel de daño sináptico?>
    │
    ├── Leve    → Flat00 (cóclea sana), nH=7, nM=3, nL=3
    ├── Moderado → Flat00 (cóclea sana), nH=4, nM=2, nL=2
    └── Severo   → Flat00 (cóclea sana), nH=1, nM=1, nL=1]
  │
  ▼
[5. Investigador hace clic en "Comparar Fenotipos"]
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  6. PIPELINE DE CONSULTA DUAL (BACKEND / POSTGRESQL)         ║
║  ─────────────────────────────────────────────────────────   ║
║  Entrada: (SlopeXX + AN normal) y (Flat00 + AN reducido)     ║
║           + tipo de estímulo seleccionado                    ║
║  Proceso: `core-service` ejecuta dos queries simultáneas a   ║
║           `precomputed_profiles` (una por fenotipo).         ║
║  Salida: EFR, W1, W3, W5 de Fenotipo A y Fenotipo B.        ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error → [Mostrar: "Perfil no disponible para combinación"] → volver a 3
  │
  ▼
[7. Frontend renderiza panel dividido en dos secciones:
    - Panel A (Gráfico de barras): EFR µV de Fenotipo Envejecimiento vs. Fenotipo Trauma
    - Panel B (Superposición de ondas): W1, W3, W5 de ambos fenotipos en colores distintos]
  │
  ▼
[8. Investigador analiza los resultados:
    ¿La onda W1 es más afectada en el Trauma que en el Envejecimiento?
    ¿La onda W5 (colículo inferior) se preserva relativamente en el Trauma?
    ¿La amplitud del EFR cae de manera diferente entre ambos?]
  │
  ▼
<9. ¿Desea modificar la combinación de fenotipos?>
  │                    │
  │ Sí → volver a 3    │ No
                       │
                       ▼
                      [10. Investigador exporta reporte comparativo (PDF + CSV)]
                       │
                       ▼
                      [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 3a | Nivel de Presbiacusia | Leve (Slope15) / Mod (Slope25) / Severo (Slope35_5) | Determina el perfil `Slope` con fibras AN normales a buscar en la DB. |
| 4a | Nivel de Trauma Sináptico | Leve / Mod / Severo | Determina la reducción de `nH, nM, nL` sobre `Flat00` a buscar en la DB. |
| 6 | Resultado del pipeline DB | OK → renderizar gráficos | Error → perfil no pre-computado para esa combinación |
| 9 | ¿Modificar fenotipos? | Sí → volver a 3 | No → exportar, fin |
