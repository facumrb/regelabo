# Diagrama de Actividad: Investigación en Screening Neonatal (BERA/ABR)

> **Caso de uso #9:** Investigación en Screening Neonatal (BERA/ABR)
> **Fecha:** 2026-05-12 | **Revisión:** v1
> **Fuentes:** [functionalitiesOverview.md](../functionalitiesOverview.md), [analisisScreeningNeonatal.md](../analisisScreeningNeonatal.md), [Integration Points Bera Abr.md](../Integration%20Points%20Bera%20Abr.md)

---

## 1. Metas del Fonoaudiólogo / Investigador

### Meta Principal

Estudiar cómo distintos perfiles patológicos deforman las ondas ABR (I, III, V) en neonatos simulados, ayudando al fonoaudiólogo a leer estudios BERA reales con mayor precisión y a generar hipótesis sobre sorderas congénitas.

### Sub-metas / Objetivos intermedios

- **M1:** Seleccionar un perfil patológico hipotético para el neonato (no existe audiograma conductual en recién nacidos).
- **M2:** Ejecutar la simulación ABR con el modelo Verhulst.
- **M3:** Visualizar las ondas W1, W3, W5 individuales y el ABR compuesto.
- **M4:** Analizar latencias, amplitudes e intervalos interpico.
- **M5:** Opcionalmente comparar el ABR simulado contra un BERA real del neonato.

### Clasificación: SUB-META del EFR

El Screening BERA/ABR comparte **exactamente el mismo pipeline** que el EFR. La cadena `ohc_ind() → model2018(storeflag='bw', fc='abr') → output.w1, w3, w5` es idéntica. Lo que cambia es exclusivamente la **capa de presentación**: el EFR analiza magnitud espectral del compuesto; el ABR analiza morfología temporal, latencia y amplitud de ondas individuales.

| Aspecto | EFR (Meta Principal) | ABR/BERA (Sub-meta) |
|---|---|---|
| Señal de interés | `EFR = W1 + W3 + W5` (suma) | `W1`, `W3`, `W5` individuales |
| Pipeline del modelo | `model2018()` | `model2018()` — **la misma** |
| Diferencia real | FFT del compuesto | Análisis temporal de ondas individuales |

### Taxonomía

```
Meta Principal: Simulación EFR (Verhulst 2018)
├── Sub-meta: Screening Neonatal BERA/ABR  ← esta
├── Sub-meta: Sordera Oculta (Sinaptopatía)
├── Sub-meta: Optimización de Estímulos
├── Sub-meta: Generación de Datos Sintéticos (ML)
└── Sub-meta: Validación contra datos reales
```

### Consideración clínica clave

En un **neonato** no existe audiograma conductual. Los inputs son perfiles patológicos paramétricos pre-computados (Flat/Slope) que representan hipótesis de pérdida, o datos crudos MAT/CSV importados de equipos BERA reales para comparación.

---

## 2. Flujo Principal (DA)

### Nomenclatura
- `[●]` = Nodo inicio/fin
- `[Acción]` = Actividad
- `<Decisión>` = Bifurcación (rombo)
- `╔═══╗` = Actividad compuesta (caja negra)

### Flujo principal (Verhulst como caja negra)

> [!NOTE]
> El pipeline del modelo Verhulst (paso 10) se trata como una **actividad opaca** desde la perspectiva del caso de uso. El detalle interno se documenta en el [análisis Verhulst](../verhulst-analysis/screening-neonatal.md).

```
[●] INICIO
  │
  ▼
[1. Fonoaudiólogo accede al módulo "Screening BERA/ABR"]
  │
  ▼
[2. Sistema presenta formulario de configuración]
  │
  ▼
<3. ¿Cómo define el perfil auditivo del neonato?>
  │                                    │
  │ [Perfil pre-computado]             │ [Audiograma hipotético]
  ▼                                    ▼
[3a. Selecciona perfil               [3b. Ingresa frecuencias (Hz)
 del catálogo (Flat/Slope)]           y pérdidas (dB HL) manualmente]
  │                                    │
  │                                    ▼
  │                              [3b.1 Sistema valida:
  │                               - misma longitud freq/dB
  │                               - rango válido (125-8000 Hz)
  │                               - dB HL entre 0 y 120]
  │                                    │
  │                                    ▼
  │                              <3b.2 ¿Validación OK?>
  │                                │           │
  │                                │ Sí        │ No
  │                                │           ▼
  │                                │    [Mostrar error,
  │                                │     volver a 3b]
  │                                │
  ▼                                ▼
[4. Configura fibras AN: nH, nM, nL (sliders con defaults 13/3/3)]
  │
  ▼
[5. Selecciona tipo de estímulo (click / tone burst / RAM)]
  │
  ▼
<6. ¿Tiene datos BERA reales para comparar?>
  │                         │
  │ No                      │ Sí
  │                         ▼
  │                   [6a. Sube archivo MAT/CSV]
  │                         │
  │                         ▼
  │                   <6b. ¿Formato válido?>
  │                     │           │
  │                     │ Sí        │ No
  │                     │           ▼
  │                     │    [Mostrar error formato,
  │                     │     volver a 6a]
  │                     │
  ▼                     ▼
[7. Fonoaudiólogo presiona "Ejecutar Simulación"]
  │
  ▼
[8. Controlador valida request completo (Pydantic schema)]
  │
  ▼
<9. ¿Request válido?>
  │           │
  │ Sí        │ No → [Retornar HTTP 422 + detalle de error] → FIN
  │
  ▼
╔══════════════════════════════════════════════════════════════╗
║  10. PIPELINE DE SIMULACIÓN VERHULST (CAJA NEGRA)          ║
║  ─────────────────────────────────────────────────────────  ║
║  Entrada: perfil auditivo, config fibras, tipo estímulo    ║
║  Salida:  w1[], w3[], w5[], abr[], time_axis[], fs, cf[]   ║
║                                                             ║
║  Ver verhulst-analysis/screening-neonatal.md                ║
╚══════════════════════════════════════════════════════════════╝
  │            │
  │ OK         │ Error
  │            ▼
  │      [10a. Registrar error en DB,
  │       notificar frontend → "Error en simulación"] → FIN
  │
  ▼
[11. Frontend recibe notificación de completitud (polling / WebSocket)]
  │
  ▼
[12. Plotly.js renderiza gráfico interactivo con 4 trazas (W1, W3, W5, ABR)]
  │
  ▼
<13. ¿Se subieron datos BERA reales (E5)?>
  │                    │
  │ No                 │ Sí
  │                    ▼
  │              [13a. Superponer traza BERA real
  │               como línea punteada en el gráfico]
  │                    │
  ▼                    ▼
[14. Sistema calcula automáticamente:
     - Latencias pico W1, W3, W5 (ms)
     - Intervalos interpico I-III, III-V, I-V (ms)
     - Amplitudes pico-a-pico (µV)]
  │
  ▼
[15. Fonoaudiólogo analiza visualmente las ondas I, III y V:
     - Identifica presencia/ausencia de cada onda
     - Evalúa morfología y replicabilidad
     - Compara latencias contra valores normativos neonatales
     - Interpreta si el perfil patológico explica la deformación]
  │
  ▼
<16. ¿Desea ejecutar otra simulación con parámetros diferentes?>
  │                    │
  │ No                 │ Sí → volver a paso 3
  │
  ▼
[17. Fonoaudiólogo guarda/exporta resultados (opcional)]
  │
  ▼
[●] FIN
```

### Tabla de Bifurcaciones

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| 3 | Fuente del perfil auditivo | Pre-computado → selección directa | Audiograma hipotético → validación |
| 3b.2 | ¿Validación OK? | Sí → continuar | No → mostrar error, volver a 3b |
| 6 | ¿Datos BERA reales? | No → continuar | Sí → upload + validación formato |
| 6b | ¿Formato válido? | Sí → continuar | No → error, volver a 6a |
| 9 | ¿Request válido? | Sí → continuar | No → HTTP 422, fin |
| 10 | Pipeline Verhulst | OK → continuar | Error → registrar, notificar, fin |
| 13 | ¿Overlay BERA real? | No → solo simulado | Sí → superponer traza |
| 16 | ¿Otra simulación? | No → guardar/fin | Sí → loop a paso 3 |

---

## 3. Subdiagrama: Pipeline de Simulación Verhulst

> [!IMPORTANT]
> Detalla la actividad **10** del DA principal. Interfaz contractual: recibe parámetros de simulación, devuelve ondas ABR o un error.

```
[●] INICIO (desde DA principal, paso 10)
  │
  ▼
[S1. Servicio determina fuente de polos de Shera]
  │
  ▼
<S2. ¿Perfil pre-computado o audiograma custom?>
  │                                    │
  │ Pre-computado                      │ Custom
  ▼                                    ▼
[S2a. np.loadtxt(                    [S2b. ohc_ind(name, freqs,
 Poles/{perfil}/                       dB, base_dir,
 StartingPoles.dat)]                   show_figs=False)]
  │                                    │
  │                                    ▼
  │                              [S2b.1 Lee StartingPoles.dat
  │                               generado por ohc_ind()]
  │                                    │
  ▼                                    ▼
[S3. sheraP: ndarray (1001,) disponible]
  │
  ▼
[S4. Genera estímulo acústico (click/tone/RAM → ndarray 1D)]
  │
  ▼
[S5. Encola tarea Celery con parámetros completos]
  │
  ▼
[S6. Retorna task_id al frontend → UI muestra "Simulando..." con progress]
  │
  ▼
[S7. Worker Celery ejecuta model2018(stim, fs, sheraP, nH, nM, nL,
     fc='abr', storeflag='bw')]        ──── [2-10 min CPU]
  │
  ▼
<S8. ¿Simulación completada sin error?>
  │                    │
  │ Sí                 │ No → [Retornar señal de error al DA principal] → FIN
  │
  ▼
[S9. Extraer output.w1, output.w3, output.w5, output.fs_abr]
  │
  ▼
[S10. Calcular ABR = w1 + w3 + w5, time_axis = arange(N) / fs_abr]
  │
  ▼
[S11. Serializar a JSON {w1[], w3[], w5[], abr[], fs, time_axis[], cf[]}]
  │
  ▼
[S12. Persistir resultado en DB + Storage, actualizar estado tarea]
  │
  ▼
[●] FIN (retorna resultado al DA principal → paso 11)
```

| # | Decisión | Rama A | Rama B |
|---|---|---|---|
| S2 | Tipo de polos | Pre-computado → `np.loadtxt` | Custom → `ohc_ind()` |
| S8 | ¿Simulación OK? | Sí → extraer y serializar | No → error al DA principal |

---

## 4. Notas para Implementación

> [!TIP]
> **Reutilización máxima:** El endpoint `POST /simulate/abr` puede ser un alias del endpoint EFR genérico. La diferencia es que el frontend envía un flag `mode: "abr"` que indica `storeflag='bw'` + `fc='abr'`, y renderiza ondas individuales en vez del espectro EFR.

> [!WARNING]
> **Tiempo de cómputo:** La simulación toma 2-10 minutos. Entre el paso 10 y el 11 hay una espera asíncrona real. El frontend debe implementar polling o WebSocket.
