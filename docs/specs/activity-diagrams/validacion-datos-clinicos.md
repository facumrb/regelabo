# Diagrama de Actividad: Validar Modelos con Datos Clínicos Reales

> **Caso de uso #5:** Validar modelos con datos clínicos reales
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Comprobar que el simulador Verhulst reproduce fielmente la respuesta eléctrica real de un paciente real, superponiendo la señal simulada (usando el audiograma real del paciente como entrada) sobre el EEG/ABR medido clínicamente.

### Sub-metas / Objetivos intermedios

- **M1:** Cargar el audiograma real del paciente para generar el perfil coclear personalizado.
- **M2:** Cargar la señal ABR/EFR real medida con el equipo clínico.
- **M3:** Ejecutar la simulación con ese perfil.
- **M4:** Comparar visualmente y métricamente la señal simulada vs. la real.
- **M5:** Cuantificar el error de predicción del modelo.

### Clasificación en la taxonomía del proyecto

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Validar modelos con datos clínicos reales  ← esta
│   ├── M1: Carga de audiograma real → ohc_ind() → sheraP
│   ├── M2: Carga de señal real (ABR/EFR de equipo)
│   ├── M3: Simulación con perfil personalizado
│   └── M4: Comparación y métricas de error
└── [Valida la precisión del modelo Verhulst como herramienta de I+D]
```

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
[1. Investigador accede al módulo "Validación contra Datos Clínicos Reales"]
  │
  ▼
[2. Sistema solicita los datos del paciente real]
  │
  ▼
══════════ PASO A: DATOS DE ENTRADA DEL PACIENTE ══════════
  │
  ▼
[3. Ingresa o carga el AUDIOGRAMA REAL del paciente:
     - Frecuencias (Hz): 250, 500, 1000, 2000, 4000, 8000
     - Umbrales (dB HL): valor medido para cada frecuencia
     → El sistema usará ohc_ind() para convertir a perfil coclear]
  │
  ▼
[4. Carga la SEÑAL REAL medida en el equipo clínico:
     Archivo MAT/CSV/EDF con columna time y amplitude del ABR o EFR real]
  │
  ▼
[4.1 Sistema valida el archivo de señal real:
      - Formato correcto
      - Duración y fs adecuadas]
  │
  ▼
<4.2 ¿Archivo válido?>
  │           │
  │ Sí        │ No → [Mostrar error de formato] → volver a 4
  │
  ▼
══════════ PASO B: CONFIGURACIÓN DE LA SIMULACIÓN ══════════
  │
  ▼
[5. Investigador indica el ESTÍMULO usado en la medición real:
     Tipo (click, tono, RAM), frecuencia, nivel SPL
     → El sistema replicará exactamente ese estímulo en la simulación]
  │
  ▼
[6. Configura las fibras AN (nH, nM, nL):
     Default: normativo (13/3/3)
     Opcional: ajustar si el paciente tiene sospecha de sinaptopatía]
  │
  ▼
[7. Investigador presiona "Ejecutar validación"]
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  8. PIPELINE VERHULST — PERFIL PERSONALIZADO (CAJA NEGRA)  ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada:                                                   ║
║    - audiograma real → ohc_ind() → sheraP personalizado     ║
║    - estímulo réplica del equipo clínico                    ║
║    - nH, nM, nL configurados                               ║
║  Salida: EFR simulado (µV) + w1[], w3[], w5[]               ║
║                                                             ║
║  Ver verhulst-analysis/validacion-datos-clinicos.md         ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error → [Registrar, notificar] → FIN
  │
  ▼
══════════ PASO C: COMPARACIÓN Y MÉTRICAS ══════════
  │
  ▼
[9. Sistema normaliza ambas señales al mismo eje temporal
    (re-muestreo si fs difieren)]
  │
  ▼
[10. Plotly.js renderiza overlay de comparación:
       - Traza azul: ABR/EFR simulado
       - Traza roja (punteada): ABR/EFR real del paciente
       - Panel de error: diferencia punto a punto]
  │
  ▼
[11. Sistema calcula métricas de concordancia:
       - Correlación de Pearson (señal simulada vs. real)
       - Error Cuadrático Medio (RMS error) en µV
       - Diferencia de latencias pico W1/W3/W5 en ms
       - Diferencia de amplitudes en %]
  │
  ▼
[12. Investigador interpreta el grado de concordancia:
       - ¿El modelo reproduce bien la morfología del ABR?
       - ¿Las latencias coinciden dentro de ±0.5 ms?
       - ¿Hay discrepancias sistemáticas (bias)?]
  │
  ▼
<13. ¿Desea ajustar fibras AN y re-simular para mejorar el ajuste?>
  │                               │
  │ Sí → volver a paso 6          │ No
                                   │
                                   ▼
                                  [14. Exporta informe de validación:
                                        - CSV de ambas señales
                                        - Tabla de métricas de concordancia
                                        - Imagen del overlay]
                                   │
                                   ▼
                                  [●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 4.2 | ¿Archivo válido? | Sí → continuar | No → mostrar error, volver |
| 8 | Pipeline Verhulst | OK → comparar | Error → registrar, fin |
| 13 | ¿Ajustar y re-simular? | Sí → cambiar nH/nM/nL, loop | No → exportar, fin |
